#!/bin/bash
# Production Deployment Script for ERP01
set -e

echo "[START] Starting ERP01 Production Deployment..."

# Configuration
APP_NAME="erp01"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SYSTEMD_SERVICE="$APP_NAME.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR] Please run as root (sudo)"
    exit 1
fi

# Create app user if not exists
if ! id -u $APP_NAME >/dev/null 2>&1; then
    echo "👤 Creating app user..."
    useradd -r -s /bin/false $APP_NAME
fi

# Create application directory
echo "[DIR] Setting up directories..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/data
mkdir -p $APP_DIR/logs

# Copy application files
echo "[FILES] Copying application files..."
cp -r * $APP_DIR/
chown -R $APP_NAME:$APP_NAME $APP_DIR

# Create virtual environment
echo "🐍 Creating virtual environment..."
cd $APP_DIR
python3 -m venv venv
chown -R $APP_NAME:$APP_NAME venv

# Install dependencies
echo "📥 Installing dependencies..."
su - $APP_NAME -s /bin/bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn"

# Setup systemd service
echo "[SYSTEMD] Configuring systemd..."
cp $SYSTEMD_SERVICE /etc/systemd/system/
systemctl daemon-reload
systemctl enable $APP_NAME

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    echo "[SECURITY] Configuring firewall..."
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

# Start service
echo "🏁 Starting service..."
systemctl start $APP_NAME

# Check status
echo "[STATUS] Checking status..."
systemctl status $APP_NAME --no-pager

echo ""
echo "[OK] Deployment complete!"
echo "[URL] Access your application at: http://your-server-ip"
echo "[LOGS] View logs: journalctl -u $APP_NAME -f"
echo "[RESTART] Restart: systemctl restart $APP_NAME"
echo "[STOP] Stop: systemctl stop $APP_NAME"
