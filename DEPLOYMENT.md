# ERP01 Production Deployment Guide

## Quick Start Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Direct Deployment

```bash
# Run deployment script (requires sudo)
sudo ./deploy.sh

# Or manual installation:
sudo useradd -r -s /bin/false erp01
sudo mkdir -p /opt/erp01
sudo cp -r * /opt/erp01/
sudo chown -R erp01:erp01 /opt/erp01

cd /opt/erp01
sudo -u erp01 python3 -m venv venv
sudo -u erp01 /opt/erp01/venv/bin/pip install -r requirements.txt gunicorn

# Setup systemd
sudo cp erp01.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable erp01
sudo systemctl start erp01
```

## Configuration

1. Copy `.env.production` to `.env`
2. Update all values for your environment
3. Generate a strong SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Nginx Reverse Proxy

1. Copy `nginx.conf` to `/etc/nginx/sites-available/erp01`
2. Enable site: `ln -s /etc/nginx/sites-available/erp01 /etc/nginx/sites-enabled/`
3. Test config: `nginx -t`
4. Reload: `systemctl reload nginx`
5. Install SSL: `certbot --nginx -d your-domain.com`

## Monitoring

### Health Checks
- API: `curl http://localhost:5000/api/status`
- Systemd: `systemctl status erp01`
- Docker: `docker-compose ps`

### Metrics
- Enable metrics in `.env`: `ENABLE_METRICS=true`
- Access metrics: `http://localhost:9090/metrics`
- Integrate with Prometheus/Grafana

## Security Hardening

See `SECURITY_CHECKLIST.md` for complete security guide.

Quick actions:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow 80,443/tcp
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

## 💾 Backup

### Database Backup
```bash
# PostgreSQL
pg_dump erp01 > backup_$(date +%Y%m%d).sql

# SQLite
cp erp01.db erp01_backup_$(date +%Y%m%d).db
```

### Full Backup
```bash
tar -czf erp01_backup_$(date +%Y%m%d).tar.gz /opt/erp01
```

## Updates

```bash
# Pull latest code
cd /opt/erp01
git pull

# Install new dependencies
sudo -u erp01 /opt/erp01/venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl restart erp01

# Or with Docker
docker-compose pull
docker-compose up -d
```

## 🆘 Troubleshooting

### View Logs
```bash
# Systemd
journalctl -u erp01 -f

# Docker
docker-compose logs -f

# Application logs
tail -f /opt/erp01/logs/app.log
```

### Common Issues

**Service won't start:**
```bash
sudo systemctl status erp01
sudo journalctl -u erp01 -n 50
```

**Port already in use:**
```bash
sudo lsof -i :5000
sudo systemctl stop conflicting-service
```

**Permission errors:**
```bash
sudo chown -R erp01:erp01 /opt/erp01
```

## 📞 Support

For production support and enterprise features, contact your system administrator.
