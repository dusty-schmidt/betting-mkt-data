# Deployment Guide

Complete guide for deploying the Betting Markets Data Aggregator in various environments.

## Deployment Overview

This guide covers deployment strategies for development, testing, staging, and production environments. Choose the appropriate deployment method based on your requirements.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 512MB RAM, recommended 1GB+
- **Storage**: 1GB+ for database and logs
- **Network**: Outbound internet access for provider APIs
- **OS**: Linux, macOS, or Windows

### Dependencies

```bash
# Required packages
python -m pip install uv requests flask waitress pyyaml pydantic
```

Or using the project's `pyproject.toml`:

```bash
uv sync
```

## Development Deployment

### Local Development Setup

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd betting-mkt-data
uv sync
```

2. **Initialize Database**:
```bash
uv run python -c "from src.core.database import init_db; init_db()"
```

3. **Start Development Server**:
```bash
uv run python run.py
```

4. **Verify Deployment**:
```bash
curl http://localhost:5000/api/v1/status
curl http://localhost:5000/api/v1/games
```

### Development Environment Variables

```bash
# Development configuration
export DB_PATH=./dev_data/betting_markets.db
export LOG_DIR=./logs
export LOG_LEVEL=DEBUG
export API_PORT=5000
```

### Development Configuration File

```yaml
# config.yaml - Development
intervals:
  NFL:
    DraftKings: 60      # Frequent updates for testing
    FanDuel: 60
  NBA:
    DraftKings: 120
    FanDuel: 120

provider_config:
  DraftKings:
    rate_limit: 5.0     # Faster for development
    timeout: 5
    max_retries: 1
```

## Docker Deployment

### Dockerfile

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install uv && uv sync --frozen

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/status || exit 1

# Run application
CMD ["uv", "run", "python", "run.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  betting-aggregator:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_PATH=/app/data/betting_markets.db
      - LOG_DIR=/app/logs
      - LOG_LEVEL=INFO
      - API_PORT=5000
    volumes:
      - ./data:/app/data      # Persistent database
      - ./logs:/app/logs      # Persistent logs
      - ./config.yaml:/app/config.yaml  # Custom config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add nginx for reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - betting-aggregator
    restart: unless-stopped
```

### Docker Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f betting-aggregator

# Scale if needed
docker-compose up -d --scale betting-aggregator=2

# Stop and cleanup
docker-compose down
docker-compose down -v  # Remove volumes
```

## Production Deployment

### Systemd Service

Create a systemd service file for production deployment:

```ini
# /etc/systemd/system/betting-aggregator.service
[Unit]
Description=Betting Markets Data Aggregator
After=network.target
Wants=network.target

[Service]
Type=simple
User=appuser
Group=appgroup
WorkingDirectory=/opt/betting-aggregator
Environment=DB_PATH=/opt/betting-aggregator/data/betting_markets.db
Environment=LOG_DIR=/var/log/betting-aggregator
Environment=LOG_LEVEL=INFO
Environment=API_PORT=5000
ExecStart=/opt/betting-aggregator/venv/bin/python /opt/betting-aggregator/run.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/betting-aggregator/data
ReadWritePaths=/var/log/betting-aggregator

# Resource limits
LimitNOFILE=65536
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

### Production Installation

```bash
# 1. Create application user
sudo useradd -r -s /bin/false -d /opt/betting-aggregator appuser

# 2. Create directories
sudo mkdir -p /opt/betting-aggregator
sudo mkdir -p /var/log/betting-aggregator
sudo mkdir -p /opt/betting-aggregator/data

# 3. Set ownership
sudo chown -R appuser:appgroup /opt/betting-aggregator
sudo chown -R appuser:appgroup /var/log/betting-aggregator

# 4. Copy application
sudo cp -r . /opt/betting-aggregator/

# 5. Install dependencies
cd /opt/betting-aggregator
sudo -u appuser uv sync

# 6. Setup service
sudo cp deployment/betting-aggregator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable betting-aggregator

# 7. Start service
sudo systemctl start betting-aggregator

# 8. Check status
sudo systemctl status betting-aggregator
```

### Production Configuration

```yaml
# /opt/betting-aggregator/config.yaml - Production
intervals:
  NFL:
    DraftKings: 300     # Every 5 minutes
    FanDuel: 300
  NBA:
    DraftKings: 600     # Every 10 minutes
    FanDuel: 600
  MLB:
    DraftKings: 900     # Every 15 minutes
    FanDuel: 900
  NHL:
    DraftKings: 1200    # Every 20 minutes
    FanDuel: 1200

provider_config:
  DraftKings:
    rate_limit: 1.0     # Conservative rate limiting
    timeout: 15
    max_retries: 3
    headers:
      User-Agent: "Betting-Aggregator/1.0"

monitoring:
  health_check_interval: 60
  log_tail_lines: 20
  alert_thresholds:
    provider_failure_rate: 0.1
    api_response_time: 1000
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

```json
{
  "family": "betting-aggregator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "betting-aggregator",
      "image": "your-account.dkr.ecr.region.amazonaws.com/betting-aggregator:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DB_PATH",
          "value": "/app/data/betting_markets.db"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/betting-aggregator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/api/v1/status || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### Using AWS EC2

```bash
# Launch EC2 instance (Amazon Linux 2)
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t3.small \
    --key-name your-key-pair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --user-data file://user-data.sh

# User data script (user-data.sh)
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git
pip3 install uv

# Setup application
mkdir -p /opt/betting-aggregator
cd /opt/betting-aggregator
git clone <your-repo> .
uv sync

# Setup systemd service
cp deployment/betting-aggregator.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable betting-aggregator
systemctl start betting-aggregator
```

### Google Cloud Platform

#### Using Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/betting-aggregator:$BUILD_ID', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/betting-aggregator:$BUILD_ID']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'betting-aggregator'
      - '--image'
      - 'gcr.io/$PROJECT_ID/betting-aggregator:$BUILD_ID'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name betting-rg --location eastus

# Deploy container
az container create \
    --resource-group betting-rg \
    --name betting-aggregator \
    --image your-registry/betting-aggregator:latest \
    --cpu 1 \
    --memory 1 \
    --ports 5000 \
    --environment-variables \
        DB_PATH=/app/data/betting_markets.db \
        LOG_LEVEL=INFO
```

## Reverse Proxy Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/betting-aggregator
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration
    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000/api/v1/status;
        access_log off;
    }
}
```

### Apache Configuration

```apache
# /etc/apache2/sites-available/betting-aggregator.conf
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    SSLEngine on
    SSLCertificateFile /path/to/certificate.pem
    SSLCertificateKeyFile /path/to/private.key
    
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:5000/api/
    ProxyPassReverse /api/ http://localhost:5000/api/
    
    # Health check
    ProxyPass /health http://localhost:5000/api/v1/status
</VirtualHost>
```

## Monitoring and Logging

### Log Aggregation

#### Using ELK Stack

```yaml
# Filebeat configuration
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/betting-aggregator/*.log
  fields:
    service: betting-aggregator
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "betting-aggregator-%{+yyyy.MM.dd}"

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

#### Using CloudWatch (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch
sudo cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/betting-aggregator/app.log",
            "log_group_name": "betting-aggregator",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
EOF

sudo systemctl start amazon-cloudwatch-agent
```

### Health Monitoring

```bash
# Health check script
#!/bin/bash
# health-check.sh

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/status)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy (HTTP $RESPONSE)"
    exit 1
fi

# Add to crontab
# */5 * * * * /path/to/health-check.sh
```

### Prometheus Metrics (Future Enhancement)

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
REQUEST_COUNT = Counter('betting_api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('betting_api_request_duration_seconds', 'API request duration')
PROVIDER_FETCH_COUNT = Counter('betting_provider_fetches_total', 'Provider fetch attempts', ['provider', 'sport'])
PROVIDER_SUCCESS_COUNT = Counter('betting_provider_success_total', 'Provider fetch successes', ['provider', 'sport'])
GAMES_COUNT = Gauge('betting_games_total', 'Total games in database')
ODDS_COUNT = Gauge('betting_odds_total', 'Total odds records in database')

# Update metrics in API routes
@api_bp.route('/games')
def list_games():
    start_time = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/games').inc()
    
    try:
        # Your existing code
        games = get_games()
        REQUEST_DURATION.observe(time.time() - start_time)
        return jsonify(games)
    except Exception as e:
        REQUEST_DURATION.observe(time.time() - start_time)
        raise

# Expose metrics endpoint
@api_bp.route('/metrics')
def metrics():
    return generate_latest()
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/opt/backups/betting-aggregator"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/opt/betting-aggregator/data/betting_markets.db"

mkdir -p $BACKUP_DIR

# Create backup
sqlite3 $DB_PATH ".backup $BACKUP_DIR/backup_$DATE.db"

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.db.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.db.gz"
```

### Automated Backup with Cron

```bash
# Add to crontab
0 2 * * * /opt/betting-aggregator/scripts/backup-database.sh

# Or with systemd timer (recommended)
sudo cat > /etc/systemd/system/betting-aggregator-backup.service << EOF
[Unit]
Description=Betting Aggregator Database Backup
After=betting-aggregator.service

[Service]
Type=oneshot
ExecStart=/opt/betting-aggregator/scripts/backup-database.sh
User=appuser
EOF

sudo cat > /etc/systemd/system/betting-aggregator-backup.timer << EOF
[Unit]
Description=Daily backup timer
Requires=betting-aggregator-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl enable betting-aggregator-backup.timer
sudo systemctl start betting-aggregator-backup.timer
```

## Security Considerations

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# For internal deployments only
sudo ufw allow from 10.0.0.0/8 to any port 5000
```

### SSL/TLS Configuration

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### API Security (Future)

```python
# Add API key authentication
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY'):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/games')
@require_api_key
def list_games():
    # Your existing code
    pass
```

## Performance Tuning

### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_games_sport ON games(sport);
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games(start_time);
CREATE INDEX IF NOT EXISTS idx_odds_provider ON odds(provider);
CREATE INDEX IF NOT EXISTS idx_odds_market ON odds(market);

-- Optimize database settings
PRAGMA journal_mode = WAL;      -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;    -- Balance performance and safety
PRAGMA cache_size = 10000;      -- 10MB cache
PRAGMA temp_store = memory;     -- Store temp tables in memory
```

### Application Tuning

```python
# In run.py - Waitress configuration
from waitress import serve

serve(
    app,
    host="0.0.0.0",
    port=5000,
    threads=4,              # Adjust based on CPU cores
    connection_limit=1000,   # Maximum connections
    queue_max=1000,         # Request queue size
    channel_timeout=30      # Channel timeout
)
```

## Troubleshooting Deployment

### Common Issues

#### 1. Permission Errors

```bash
# Fix ownership and permissions
sudo chown -R appuser:appgroup /opt/betting-aggregator
sudo chmod +x /opt/betting-aggregator/run.py

# Check SELinux (RHEL/CentOS)
sudo setsebool -P httpd_can_network_connect 1
```

#### 2. Database Lock Issues

```bash
# Check for running processes
ps aux | grep python

# Kill hanging processes
sudo pkill -f betting-aggregator

# Remove stale lock file if needed
sudo rm -f /opt/betting-aggregator/data/betting_markets.db-wal
```

#### 3. Port Already in Use

```bash
# Find process using port 5000
sudo netstat -tlnp | grep :5000

# Kill process or change port
sudo lsof -ti:5000 | xargs kill -9
```

#### 4. Log Directory Issues

```bash
# Create and set permissions
sudo mkdir -p /var/log/betting-aggregator
sudo chown appuser:appgroup /var/log/betting-aggregator
sudo chmod 755 /var/log/betting-aggregator
```

### Deployment Verification

```bash
#!/bin/bash
# deployment-check.sh

echo "=== Deployment Verification ==="

# Check service status
if systemctl is-active --quiet betting-aggregator; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running"
    systemctl status betting-aggregator
fi

# Check API endpoints
echo "Testing API endpoints..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/status)
if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ Status endpoint OK"
else
    echo "❌ Status endpoint failed (HTTP $HTTP_CODE)"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/games)
if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ Games endpoint OK"
else
    echo "❌ Games endpoint failed (HTTP $HTTP_CODE)"
fi

# Check database
if [ -f "/opt/betting-aggregator/data/betting_markets.db" ]; then
    echo "✅ Database file exists"
else
    echo "❌ Database file missing"
fi

# Check logs
if [ -f "/var/log/betting-aggregator/app.log" ]; then
    echo "✅ Log file exists"
    RECENT_LOGS=$(tail -5 /var/log/betting-aggregator/app.log)
    echo "Recent logs:"
    echo "$RECENT_LOGS"
else
    echo "❌ Log file missing"
fi

echo "=== Verification Complete ==="
```

This deployment guide provides comprehensive coverage for deploying the betting markets aggregator in various environments with proper security, monitoring, and maintenance practices.