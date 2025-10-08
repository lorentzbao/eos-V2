# Deployment Guide

Production deployment guide for EOS Japanese Enterprise Search Engine.

---

## 🚀 Production Deployment

### Quick Production Setup

```bash
# Set production environment
export FLASK_ENV=production

# Run with production settings
uv run python run.py app.debug=false app.host=0.0.0.0 app.port=80
```

---

## ⚙️ Environment Configuration

### Environment Variables

```bash
# Flask settings
export FLASK_ENV=production
export FLASK_SECRET_KEY="your-secure-random-key-here"

# Application settings
export INDEX_DIR="data/indexes"
export DEBUG=false

# Optional: Database for search logs
export DATABASE_URL="postgresql://user:password@localhost/eos"
```

### Configuration Override

```bash
# Using Hydra overrides
uv run python run.py \
  app.debug=false \
  app.host=0.0.0.0 \
  app.port=80 \
  app.secret_key="${FLASK_SECRET_KEY}"
```

---

## 🔒 Security Checklist

### Before Deployment

- [ ] Change `app.secret_key` to secure random value
- [ ] Set `app.debug=false` 
- [ ] Implement proper authentication (replace username-only sessions)
- [ ] Add CSRF protection
- [ ] Enable HTTPS
- [ ] Set up rate limiting
- [ ] Validate and sanitize all user inputs
- [ ] Review file permissions (`chmod 755` for directories, `644` for files)
- [ ] Secure API endpoints with authentication
- [ ] Set up logging and monitoring

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
# Use this value for app.secret_key
```

---

## 🌐 Web Server Setup

### Option 1: Gunicorn (Recommended)

```bash
# Install Gunicorn
uv pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 'run:create_app()'

# With worker timeout
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 'run:create_app()'
```

**Gunicorn Configuration File** (`gunicorn.conf.py`):
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = "info"
```

Run with config:
```bash
gunicorn -c gunicorn.conf.py 'run:create_app()'
```

### Option 2: Nginx + Gunicorn

**Nginx Configuration** (`/etc/nginx/sites-available/eos`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large exports
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    location /static {
        alias /path/to/eos/app/static;
        expires 30d;
    }

    # Increase body size for document uploads
    client_max_body_size 100M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/eos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install Python dependencies
RUN uv sync

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:create_app()"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  eos:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
```

---

## 🗂️ Data Migration

### Moving Data Between Environments

```bash
# 1. Copy indexes (entire directory)
rsync -av data/indexes/ production-server:/path/to/eos/data/indexes/

# 2. Copy tokenized data (if needed for re-indexing)
rsync -av data/tokenized/ production-server:/path/to/eos/data/tokenized/

# 3. Verify index integrity
uv run python scripts/index_info.py

# 4. Update configuration paths if needed
# Edit conf/config.yaml
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/eos"
DATE=$(date +%Y%m%d)

# Backup indexes
tar -czf ${BACKUP_DIR}/indexes-${DATE}.tar.gz data/indexes/

# Backup search logs
tar -czf ${BACKUP_DIR}/logs-${DATE}.tar.gz data/search_logs/

# Keep only last 7 days
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
```

Set up cron job:
```bash
0 2 * * * /path/to/backup-script.sh
```

---

## 📊 Monitoring & Logging

### Application Logging

Update `run.py` to add logging:
```python
import logging

logging.basicConfig(
    filename='logs/eos.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Nginx Access Logs

```bash
# View access logs
tail -f /var/log/nginx/access.log

# View error logs
tail -f /var/log/nginx/error.log

# Analyze with goaccess
goaccess /var/log/nginx/access.log -o report.html
```

### Application Metrics

Monitor:
- Search response times
- Index size growth
- Memory usage
- CPU usage
- API endpoint usage

Tools:
- **Prometheus** + **Grafana** for metrics
- **Sentry** for error tracking
- **New Relic** or **DataDog** for APM

---

## 🔄 Systemd Service (Linux)

**Service File** (`/etc/systemd/system/eos.service`):
```ini
[Unit]
Description=EOS Search Engine
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/eos
Environment="FLASK_ENV=production"
Environment="FLASK_SECRET_KEY=your-secret-key"
ExecStart=/path/to/eos/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 'run:create_app()'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable eos
sudo systemctl start eos
sudo systemctl status eos
```

---

## 🔧 Performance Tuning

### Gunicorn Workers

```bash
# Calculate optimal workers: (2 x CPU cores) + 1
# For 4 CPU cores:
gunicorn -w 9 -b 0.0.0.0:8000 'run:create_app()'
```

### Database for Search Logs

For high traffic, replace file-based search logs with database:

```python
# Use PostgreSQL or MySQL instead of JSON files
# Update app/services/search_logger.py
```

### Index Optimization

```bash
# Optimize indexes regularly (via cron)
0 3 * * 0 cd /path/to/eos && uv run python -c "from app.services.search_service import SearchService; s = SearchService('data/indexes/tokyo'); s.optimize_index()"
```

### CSV Cache Cleanup

```bash
# Clean old CSV exports (via cron)
0 4 * * * find /path/to/eos/data/csv_cache -name "*.csv" -mtime +7 -delete
```

---

## 🔐 HTTPS Setup with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (certbot adds this automatically)
sudo certbot renew --dry-run
```

Update Nginx to redirect HTTP to HTTPS:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of configuration
}
```

---

## 🎯 Post-Deployment Checklist

- [ ] Application starts successfully
- [ ] All indexes loaded correctly
- [ ] Search functionality works
- [ ] CSV export works
- [ ] Prefecture/city dropdowns load
- [ ] User rankings display
- [ ] Search history persists
- [ ] Logs are being written
- [ ] Monitoring is active
- [ ] Backups are running
- [ ] HTTPS is working
- [ ] Performance is acceptable

---

**For more configuration details, see:**
- [Configuration Guide](../../CONFIGURATION.md)
- [Architecture Guide](./ARCHITECTURE.md)

**Last Updated:** 2025-10-08
