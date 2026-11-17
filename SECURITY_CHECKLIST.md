# ERP01 Production Security Checklist

## 🔐 Pre-Deployment Security

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY (min 32 chars)
- [ ] Use HTTPS with valid SSL certificate
- [ ] Configure firewall (allow only 80, 443)
- [ ] Disable debug mode (DEBUG=false)
- [ ] Set secure cookie flags
- [ ] Review and restrict CORS policies
- [ ] Update all dependencies to latest versions

## 🛡️ Runtime Security

- [ ] Run as non-root user (erp01)
- [ ] Enable automatic security updates
- [ ] Configure fail2ban for SSH
- [ ] Set up intrusion detection (optional)
- [ ] Enable audit logging
- [ ] Configure log rotation
- [ ] Monitor for suspicious activity

## Monitoring & Alerting

- [ ] Set up uptime monitoring
- [ ] Configure error rate alerts
- [ ] Monitor resource usage (CPU, RAM, Disk)
- [ ] Set up log aggregation (ELK/Loki)
- [ ] Create backup verification alerts
- [ ] Configure database backup monitoring

## 💾 Backup Strategy

- [ ] Daily automated database backups
- [ ] Weekly full system backups
- [ ] Off-site backup storage
- [ ] Test backup restoration quarterly
- [ ] Document backup recovery procedure

## Disaster Recovery

- [ ] Document recovery time objective (RTO)
- [ ] Document recovery point objective (RPO)
- [ ] Create runbook for common failures
- [ ] Test disaster recovery plan annually
- [ ] Maintain spare server capacity

## Compliance

- [ ] GDPR compliance (if applicable)
- [ ] Data retention policies
- [ ] Privacy policy updated
- [ ] Terms of service reviewed
- [ ] Accessibility standards (WCAG)
