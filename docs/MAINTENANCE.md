# Maintenance Guide

This document outlines maintenance procedures for the ERP01 system.

## Automated Maintenance Scripts

### Health Check
Run system health checks to verify environment, dependencies, and tests:

```bash
python scripts/maintenance.py health
```

**Checks performed:**
- Virtual environment existence
- Dependency installation status
- Test suite execution

### Backup
Create backups of critical project files:

```bash
python scripts/maintenance.py backup
```

**Backed up:**
- `config/`, `modules/`, `utils/`, `sprint_planning/` directories
- `main.py`, `requirements.txt`, `.env.example` files

Backups are stored in `backups/backup_YYYYMMDD_HHMMSS/`

### Clear Cache
Remove Python bytecode and test caches:

```bash
python scripts/maintenance.py clear-cache
```

**Cleared:**
- `__pycache__/` directories
- `*.pyc` files
- `.pytest_cache/`
- Coverage files (`.coverage`, `coverage.xml`)

### Rotate Logs
Rotate log files with timestamps (if logs directory exists):

```bash
python scripts/maintenance.py rotate-logs
```

## Scheduled Maintenance (Cron)

To automate maintenance tasks, add to your crontab:

```bash
# Daily health check at 6 AM
0 6 * * * cd /path/to/ERP01 && /path/to/ERP01/.venv/bin/python scripts/maintenance.py health >> logs/maintenance.log 2>&1

# Weekly backup on Sundays at 2 AM
0 2 * * 0 cd /path/to/ERP01 && /path/to/ERP01/.venv/bin/python scripts/maintenance.py backup >> logs/maintenance.log 2>&1

# Daily cache clearing at midnight
0 0 * * * cd /path/to/ERP01 && /path/to/ERP01/.venv/bin/python scripts/maintenance.py clear-cache >> logs/maintenance.log 2>&1
```

## Monitoring

### Log Files
Monitor application logs in the `logs/` directory:
- `app.log`: Main application logs
- `error.log`: Error-specific logs
- `maintenance.log`: Maintenance script logs

### Key Metrics to Watch
- Test coverage (maintain >80%)
- Build success rate
- Response times
- Error rates
- Disk space usage

## Troubleshooting

### Common Issues

**Tests failing after dependency update:**
```bash
# Clear cache and reinstall
python scripts/maintenance.py clear-cache
pip install -r requirements.txt --force-reinstall
```

**Virtual environment corrupted:**
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Disk space low:**
```bash
# Clear all caches and old backups
python scripts/maintenance.py clear-cache
# Manually remove old backups (keep last 7 days)
find backups/ -type d -mtime +7 -exec rm -rf {} +
```

## Security Updates

Regularly update dependencies:

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade <package-name>

# Update all packages (test thoroughly!)
pip install --upgrade -r requirements.txt
```

Run full test suite after any updates:
```bash
pytest --cov=.
```

## Performance Optimization

### Database Maintenance
- Regular index optimization
- Query performance monitoring
- Connection pool tuning

### Code Optimization
- Profile slow operations
- Review and optimize algorithms
- Implement caching where appropriate

## Disaster Recovery

### Backup Restoration
```bash
# Restore from backup
cp -r backups/backup_YYYYMMDD_HHMMSS/* .
```

### Rollback Procedure
1. Identify the problematic commit/version
2. Checkout previous stable version: `git checkout <tag-or-commit>`
3. Redeploy
4. Investigate and fix the issue
5. Create new release after fix

## Contact

For maintenance issues, contact the development team or create an issue in the project repository.
