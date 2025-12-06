# Troubleshooting Guide

Comprehensive troubleshooting guide for the Betting Markets Data Aggregator system.

## Common Issues and Solutions

### 1. Application Won't Start

#### Symptoms
- Application fails to start on port 5000
- Import errors during startup
- Configuration file not found errors

#### Diagnosis Steps

```bash
# Check if port is already in use
sudo netstat -tlnp | grep :5000
# or
lsof -ti:5000

# Verify Python environment
python --version
uv --version

# Check logs for startup errors
tail -f logs/app.log
```

#### Solutions

**Port Already in Use**:
```bash
# Find and kill process using port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or change port
export API_PORT=5001
uv run python run.py
```

**Missing Dependencies**:
```bash
# Reinstall dependencies
uv sync --reinstall

# Or install manually
pip install -r requirements.txt
```

**Configuration File Missing**:
```bash
# Create default configuration
cat > config.yaml << EOF
intervals:
  NFL:
    DraftKings: 300
  NBA:
    DraftKings: 600
EOF
```

### 2. Database Issues

#### Database Locked Error

**Symptoms**:
```
sqlite3.OperationalError: database is locked
```

**Diagnosis**:
```bash
# Check for hanging connections
ps aux | grep python

# Look for stale lock files
ls -la betting_markets.db*
```

**Solutions**:
```python
# In Python, ensure all connections use context managers
# ❌ Wrong
conn = get_connection()
# ... operations ...
conn.close()  # Easy to forget

# ✅ Correct
with get_connection() as conn:
    # ... operations ...
    # Connection auto-closed
```

**Force Database Unlock**:
```bash
# Stop application
sudo pkill -f betting-aggregator

# Remove stale lock files
rm -f betting_markets.db-wal
rm -f betting_markets.db-shm

# Restart application
uv run python run.py
```

#### Database Corruption

**Symptoms**:
- "database disk image is malformed" errors
- Queries returning unexpected results
- Application crashes during database operations

**Diagnosis**:
```bash
# Check database integrity
sqlite3 betting_markets.db "PRAGMA integrity_check;"

# Check database structure
sqlite3 betting_markets.db ".schema"
```

**Solutions**:
```bash
# Restore from backup if available
cp backups/backup_YYYYMMDD_HHMMSS.db.gz betting_markets.db.gz
gunzip betting_markets.db.gz

# Rebuild database from scratch
rm betting_markets.db
uv run python -c "from src.core.database import init_db; init_db()"
```

### 3. Provider API Issues

#### Provider Not Returning Data

**Symptoms**:
- Empty game lists in API responses
- High provider failure rates
- Timeout errors in logs

**Diagnosis**:
```bash
# Check provider-specific logs
grep -i "draftkings" logs/app.log
grep -i "fanduel" logs/app.log

# Test provider APIs manually
curl -v "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/1"
```

**Solutions**:

**Rate Limiting**:
```yaml
# Increase intervals in config.yaml
intervals:
  NFL:
    DraftKings: 600  # Increased from 300
    FanDuel: 600
```

**Timeout Issues**:
```yaml
# Increase timeout values
provider_config:
  DraftKings:
    timeout: 30  # Increased from 15
    max_retries: 5  # Increased from 3
```

**API Changes**:
```python
# Check for API endpoint changes in provider code
# Update API URLs and headers as needed
# DraftKings may change their API structure
```

#### Provider Authentication Issues

**Symptoms**:
- 401 Unauthorized responses
- API key errors
- Rate limit exceeded messages

**Diagnosis**:
```bash
# Check headers in provider code
# Look for outdated API keys or headers
grep -r "Authorization" src/providers/
```

**Solutions**:
```python
# Update headers in provider mappings
# src/providers/draftkings/mappings.py
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    # Add updated headers as needed
}
```

### 4. Scheduler Issues

#### Scheduler Not Running

**Symptoms**:
- No background data updates
- Scheduler threads not visible
- Static data in API responses

**Diagnosis**:
```bash
# Check if scheduler is starting
grep -i "scheduler" logs/app.log

# Verify configuration is loaded
grep -i "config" logs/app.log
```

**Solutions**:
```python
# Check config.yaml format
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
    print(config)

# Verify sport names match provider expectations
# Should be "NFL", "NBA", "MLB", "NHL"
```

**Configuration Errors**:
```yaml
# ❌ Incorrect format
intervals:
  nfl:  # Should be uppercase
    DraftKings: 300

# ✅ Correct format
intervals:
  NFL:  # Uppercase sport name
    DraftKings: 300
```

#### Thread Management Issues

**Symptoms**:
- Too many threads running
- Memory usage continuously growing
- Application slowdown

**Diagnosis**:
```bash
# Count running threads
ps aux | grep python | wc -l

# Check thread activity
grep -i "thread" logs/app.log
```

**Solutions**:
```python
# Ensure threads are properly managed
# Check scheduler.py for proper thread cleanup

def stop(self):
    self.running = False
    for t in self.threads:
        t.join(timeout=1.0)  # Don't hang indefinitely
    log.info("Scheduler stopped.")
```

### 5. API Issues

#### Slow API Responses

**Symptoms**:
- API requests taking >1 second
- Timeouts from client applications
- High server response times

**Diagnosis**:
```bash
# Test API response time
time curl http://localhost:5000/api/v1/games

# Check database performance
sqlite3 betting_markets.db "EXPLAIN QUERY PLAN SELECT * FROM games;"

# Monitor system resources
top
htop
```

**Solutions**:
```sql
-- Add database indexes for better performance
CREATE INDEX idx_games_sport ON games(sport);
CREATE INDEX idx_games_start_time ON games(start_time);
CREATE INDEX idx_odds_provider ON odds(provider);
```

**API Response Optimization**:
```python
# Limit results in API responses
@api_bp.route('/games')
def list_games():
    # Add pagination
    limit = request.args.get('limit', 100)
    offset = request.args.get('offset', 0)
    
    cur.execute("SELECT * FROM games LIMIT ? OFFSET ?", (limit, offset))
    # ... rest of implementation
```

#### 500 Internal Server Errors

**Symptoms**:
- API returns HTTP 500
- "Internal Server Error" messages
- Application crashes on API requests

**Diagnosis**:
```bash
# Check recent errors in logs
tail -50 logs/app.log | grep -i error

# Test specific endpoints
curl -v http://localhost:5000/api/v1/games
```

**Common Causes and Solutions**:

**Database Connection Issues**:
```python
# Ensure proper error handling
try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM games")
        # ...
except Exception as e:
    log.error(f"Database error: {e}")
    return jsonify({"error": "Database unavailable"}), 500
```

**Missing Environment Variables**:
```bash
# Check required environment variables
echo "DB_PATH: $DB_PATH"
echo "LOG_DIR: $LOG_DIR"

# Set defaults if missing
export DB_PATH=${DB_PATH:-./betting_markets.db}
export LOG_DIR=${LOG_DIR:-./logs}
```

### 6. Performance Issues

#### High Memory Usage

**Symptoms**:
- System running out of memory
- Application becoming slow
- OOM (Out of Memory) errors

**Diagnosis**:
```bash
# Monitor memory usage
ps aux | grep python
top -p $(pgrep -f betting-aggregator)

# Check for memory leaks in logs
grep -i "memory" logs/app.log
```

**Solutions**:
```python
# Implement connection pooling limits
# Ensure context managers properly close connections
# Add memory monitoring

import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    log.info(f"Memory usage: {memory_mb:.1f} MB")
    
    if memory_mb > 1000:  # 1GB threshold
        log.warning("High memory usage detected")
```

#### Database Performance

**Symptoms**:
- Slow database queries
- Database file growing rapidly
- Frequent disk I/O

**Solutions**:
```python
# Implement data cleanup
def cleanup_old_data():
    """Remove data older than 30 days."""
    with get_connection() as conn:
        cur = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=30)
        cur.execute(
            "DELETE FROM games WHERE start_time < ?", 
            (cutoff_date.isoformat(),)
        )
        deleted = cur.rowcount
        conn.commit()
        log.info(f"Cleaned up {deleted} old game records")
```

**Database Optimization**:
```sql
-- Run these commands to optimize database
VACUUM;
ANALYZE;
PRAGMA optimize;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;
```

### 7. Logging Issues

#### Log Files Not Being Created

**Symptoms**:
- No logs/app.log file
- "No handlers found" warnings
- Missing log output

**Diagnosis**:
```bash
# Check log directory permissions
ls -la logs/
whoami

# Test logging directly
python -c "
from src.core.logger import get_logger
log = get_logger(__name__)
log.info('Test message')
"
```

**Solutions**:
```python
# Ensure log directory exists and has proper permissions
import os
import stat

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Set proper permissions
os.chmod(log_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

# Test logging
log = get_logger(__name__)
log.info("Logging is working")
```

**Log Rotation Issues**:
```python
# Check log rotation configuration
# Logs should rotate when they exceed 5MB
# Check if old log files are being created
ls -la logs/app.log*
```

### 8. Development Issues

#### Import Errors

**Symptoms**:
- "ModuleNotFoundError" when running tests
- Import errors in provider code
- Circular import issues

**Solutions**:
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with uv which handles paths
uv run python -m pytest tests/

# Check module structure
find src/ -name "*.py" | head -20
```

#### Test Failures

**Symptoms**:
- Unit tests failing
- Integration test errors
- Provider test timeouts

**Solutions**:
```bash
# Run specific tests for debugging
uv run pytest tests/test_dk_integration.py::TestDraftKingsIntegration::test_fetch_nfl_games -v -s

# Mock provider APIs in tests
# Use pytest-mock for mocking external calls

def test_provider_with_mock(mocker):
    # Mock the API call
    mock_response = {"events": [...]}
    mocker.patch('requests.get', return_value=mock_response)
    
    provider = DraftKingsProvider()
    games = provider.fetch_odds("NFL")
    assert len(games) > 0
```

## Debugging Techniques

### Enable Debug Logging

```bash
# Set debug level for detailed logging
export LOG_LEVEL=DEBUG
uv run python run.py

# Or in config.yaml
provider_config:
  DraftKings:
    debug: true  # Provider-specific debug logging
```

### Use Debug Tools

```python
# Add debug endpoints temporarily
@api_bp.route('/debug/config')
def debug_config():
    config = load_config()
    return jsonify(config)

@api_bp.route('/debug/providers')
def debug_providers():
    providers = get_all_providers()
    return jsonify([p.__class__.__name__ for p in providers])

@api_bp.route('/debug/database')
def debug_database():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as game_count FROM games")
        game_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) as odds_count FROM odds")
        odds_count = cur.fetchone()[0]
        return jsonify({
            "games": game_count,
            "odds": odds_count
        })
```

### Network Debugging

```bash
# Test provider connectivity
curl -I "https://sportsbook-nash.draftkings.com"
curl -v -H "User-Agent: Mozilla/5.0..." "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/1"

# Check DNS resolution
nslookup sportsbook-nash.draftkings.com

# Test with different User-Agents
curl -H "User-Agent: CustomBot/1.0" "https://api.example.com"
```

### Database Debugging

```bash
# Connect to database directly
sqlite3 betting_markets.db

# Useful SQLite commands
.tables
.schema
SELECT COUNT(*) FROM games;
SELECT * FROM games LIMIT 5;
PRAGMA table_info(games);
PRAGMA index_list(games);

# Enable query logging
sqlite3 betting_markets.db "PRAGMA compile_options;"
```

### Memory and Performance Profiling

```python
# Add memory profiling to identify leaks
import tracemalloc
import cProfile

def profile_memory():
    tracemalloc.start()
    
    # Run your code here
    orchestrate("NFL")
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    tracemalloc.stop()

def profile_performance():
    cProfile.run('orchestrate("NFL")', 'profile_stats')
    import pstats
    p = pstats.Stats('profile_stats')
    p.sort_stats('cumulative').print_stats(10)
```

## Health Check Commands

### System Health Check

```bash
#!/bin/bash
# health-check.sh - Comprehensive system health check

echo "=== Betting Aggregator Health Check ==="
echo "Timestamp: $(date)"
echo ""

# Check if application is running
if pgrep -f "betting-aggregator" > /dev/null; then
    echo "✅ Application process is running"
else
    echo "❌ Application process not found"
fi

# Check API endpoints
echo "Testing API endpoints..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/status)
if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ Status endpoint responding (HTTP $HTTP_CODE)"
else
    echo "❌ Status endpoint failed (HTTP $HTTP_CODE)"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/v1/games)
if [ $HTTP_CODE -eq 200 ]; then
    echo "✅ Games endpoint responding (HTTP $HTTP_CODE)"
else
    echo "❌ Games endpoint failed (HTTP $HTTP_CODE)"
fi

# Check database
if [ -f "betting_markets.db" ]; then
    echo "✅ Database file exists"
    GAME_COUNT=$(sqlite3 betting_markets.db "SELECT COUNT(*) FROM games;" 2>/dev/null || echo "ERROR")
    if [ "$GAME_COUNT" != "ERROR" ]; then
        echo "✅ Database accessible ($GAME_COUNT games)"
    else
        echo "❌ Database not accessible"
    fi
else
    echo "❌ Database file not found"
fi

# Check logs
if [ -f "logs/app.log" ]; then
    echo "✅ Log file exists"
    LOG_SIZE=$(du -h logs/app.log | cut -f1)
    echo "   Log size: $LOG_SIZE"
else
    echo "❌ Log file not found"
fi

# Check configuration
if [ -f "config.yaml" ]; then
    echo "✅ Configuration file exists"
else
    echo "❌ Configuration file not found"
fi

# Check disk space
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage OK ($DISK_USAGE%)"
elif [ $DISK_USAGE -lt 90 ]; then
    echo "⚠️  Disk usage high ($DISK_USAGE%)"
else
    echo "❌ Disk usage critical ($DISK_USAGE%)"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f"), $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE < 80" | bc -l) )); then
    echo "✅ Memory usage OK ($MEMORY_USAGE%)"
else
    echo "⚠️  Memory usage high ($MEMORY_USAGE%)"
fi

echo ""
echo "=== Health Check Complete ==="
```

### Database Health Check

```python
#!/usr/bin/env python3
# db-health-check.py

import sqlite3
import os
from pathlib import Path

def check_database_health():
    """Comprehensive database health check."""
    db_path = Path("betting_markets.db")
    
    print("=== Database Health Check ===")
    
    if not db_path.exists():
        print("❌ Database file does not exist")
        return False
    
    print("✅ Database file exists")
    file_size = db_path.stat().st_size / 1024 / 1024  # MB
    print(f"   File size: {file_size:.1f} MB")
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Check tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"✅ Tables found: {', '.join(tables)}")
        
        # Check table row counts
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   {table}: {count} rows")
        
        # Check data freshness
        cur.execute("SELECT MAX(start_time) FROM games WHERE start_time IS NOT NULL")
        latest_game = cur.fetchone()[0]
        if latest_game:
            print(f"✅ Latest game data: {latest_game}")
        else:
            print("⚠️  No game data found")
        
        # Check integrity
        cur.execute("PRAGMA integrity_check")
        integrity_result = cur.fetchone()[0]
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"❌ Database integrity check failed: {integrity_result}")
        
        # Check index usage
        cur.execute("PRAGMA index_list(games)")
        indexes = cur.fetchall()
        print(f"✅ Games table indexes: {len(indexes)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_database_health()
```

## Getting Help

### Log Analysis

When troubleshooting, always check the logs first:

```bash
# View recent errors
tail -50 logs/app.log | grep -i error

# Search for specific provider issues
grep -i "provider.*fail" logs/app.log

# Check for configuration issues
grep -i "config" logs/app.log

# Monitor logs in real-time
tail -f logs/app.log
```

### Common Log Patterns

```
✅ Successful operations:
"Successfully fetched 15 games from DraftKings"
"Database updated with 25 new odds records"
"Scheduler started with 4 active threads"

⚠️ Warnings:
"No league mapping found for sport_id: UNKNOWN"
"Could not find subcategory ID for sport: UFC"
"Rate limited, waiting 60 seconds"

❌ Errors:
"Provider DraftKings failed: Connection timeout"
"Database connection failed: database is locked"
"API request failed: 401 Unauthorized"
```

### Support Information

When reporting issues, include:

1. **System Information**:
   - Operating system and version
   - Python version (`python --version`)
   - Application version or commit hash

2. **Configuration**:
   - Non-sensitive parts of `config.yaml`
   - Environment variables (sanitized)

3. **Error Details**:
   - Full error messages from logs
   - Steps to reproduce the issue
   - Expected vs actual behavior

4. **System State**:
   - Output from health check scripts
   - Database status
   - Resource usage (CPU, memory, disk)

### Prevention Tips

1. **Regular Monitoring**:
   - Set up automated health checks
   - Monitor log files for patterns
   - Track performance metrics

2. **Backup Strategy**:
   - Regular database backups
   - Configuration file versioning
   - Test restore procedures

3. **Update Management**:
   - Test updates in development first
   - Keep dependencies current
   - Monitor provider API changes

4. **Documentation**:
   - Document custom configurations
   - Keep troubleshooting procedures updated
   - Maintain runbooks for common issues

This troubleshooting guide should help resolve most common issues with the betting markets aggregator system. For issues not covered here, check the logs carefully and use the debugging techniques outlined above.