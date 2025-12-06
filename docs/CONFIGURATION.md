# Configuration Guide

Complete reference for configuring the Betting Markets Data Aggregator system.

## Configuration Overview

The system uses multiple configuration sources with a defined precedence order:

1. **Environment Variables** (highest priority)
2. **Configuration Files** (`config.yaml`)
3. **Default Values** (hardcoded)

## Environment Variables

Set these environment variables to override default behavior:

### Database Configuration

```bash
# Database file path (default: betting_markets.db)
export DB_PATH=/custom/path/to/betting_markets.db

# Example
export DB_PATH=/var/data/betting_markets_production.db
```

### Logging Configuration

```bash
# Log directory (default: logs/)
export LOG_DIR=/custom/log/path

# Log level (default: INFO)
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_LEVEL=DEBUG

# Example
export LOG_DIR=/var/log/betting-mkt
export LOG_LEVEL=WARNING
```

### API Server Configuration

```bash
# API server port (default: 5000)
export API_PORT=8080

# Example
export API_PORT=3000
```

### Development Environment

```bash
# Complete development setup
export DB_PATH=./dev_data/betting_markets.db
export LOG_DIR=./logs
export LOG_LEVEL=DEBUG
export API_PORT=5000
```

## Configuration Files

### config.yaml

Primary configuration file for scheduling intervals and provider settings.

#### File Location

- **Default**: `config.yaml` (in project root)
- **Can be moved**: Update the path in `src/core/scheduler.py` if needed

#### Structure

```yaml
# Central configuration for fetch intervals (in seconds)
# Structure: sport -> provider -> interval seconds
# Adjust as needed for "set and forget" operation

intervals:
  NFL:
    DraftKings: 300    # 5 minutes
    FanDuel: 300
  NBA:
    DraftKings: 600    # 10 minutes
    FanDuel: 600
  MLB:
    DraftKings: 900    # 15 minutes
    FanDuel: 900
  NHL:
    DraftKings: 600
    FanDuel: 600

# Provider-specific configuration (optional)
provider_config:
  DraftKings:
    rate_limit: 1.0      # Requests per second
    timeout: 15          # Request timeout in seconds
    max_retries: 3       # Maximum retry attempts
    
  FanDuel:
    rate_limit: 1.5      # Requests per second
    timeout: 10          # Request timeout in seconds
    max_retries: 2       # Maximum retry attempts

# Monitoring configuration
monitoring:
  health_check_interval: 60    # Seconds between health checks
  log_tail_lines: 20          # Lines to include in status reports
  alert_thresholds:
    provider_failure_rate: 0.1  # Alert if >10% provider failures
    api_response_time: 1000    # Alert if >1000ms response time
```

#### Interval Configuration

**Format**: `sport.provider: seconds`

```yaml
intervals:
  # Sport name (use standard abbreviations)
  NFL:
    # Provider name (must match provider class name)
    DraftKings: 300    # Fetch every 5 minutes
    FanDuel: 300       # Fetch every 5 minutes
    YourProvider: 180  # Custom provider every 3 minutes
  
  NBA:
    DraftKings: 600    # Fetch every 10 minutes
    FanDuel: 600       # Fetch every 10 minutes
  
  # Add new sports as needed
  NHL:
    DraftKings: 900    # Fetch every 15 minutes
    FanDuel: 900
  
  MLB:
    DraftKings: 1200   # Fetch every 20 minutes
    FanDuel: 1200
```

**Guidelines for Intervals**:
- **High-traffic sports** (NFL, NBA): 300-600 seconds
- **Medium-traffic sports** (MLB, NHL): 600-1200 seconds
- **Low-traffic sports** (UFC, Soccer): 1200+ seconds
- **Respect provider rate limits**: Don't overload APIs
- **Consider data freshness needs**: More frequent for live betting

#### Provider-Specific Configuration

```yaml
provider_config:
  DraftKings:
    # Rate limiting (requests per second)
    rate_limit: 1.0
    
    # HTTP request timeout
    timeout: 15
    
    # Maximum retry attempts for failed requests
    max_retries: 3
    
    # Custom headers if needed
    headers:
      User-Agent: "Custom User Agent"
      
    # API endpoints (if custom)
    endpoints:
      base_url: "https://sportsbook-nash.draftkings.com"
      odds_endpoint: "/api/sportscontent/dkusoh/v1"
  
  FanDuel:
    rate_limit: 1.5
    timeout: 10
    max_retries: 2
    
  YourProvider:
    rate_limit: 0.5    # Slower provider
    timeout: 20        # Longer timeout
    max_retries: 5     # More retries
    
    # Authentication configuration
    auth:
      type: "api_key"  # or "oauth", "basic"
      api_key: "your-api-key-here"
```

## Configuration Examples

### Development Configuration

```yaml
# config.yaml - Development
intervals:
  NFL:
    DraftKings: 60      # Frequent updates for testing
    FanDuel: 60
  NBA:
    DraftKings: 120     # Every 2 minutes
    FanDuel: 120

provider_config:
  DraftKings:
    rate_limit: 5.0     # Faster for testing
    timeout: 5          # Shorter timeout
    max_retries: 1      # Fail fast in development

monitoring:
  health_check_interval: 30   # More frequent health checks
  log_tail_lines: 50          # More log context
```

### Production Configuration

```yaml
# config.yaml - Production
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
    timeout: 15         # Reasonable timeout
    max_retries: 3      # Proper retry logic

monitoring:
  health_check_interval: 60   # Standard health checks
  log_tail_lines: 20          # Reasonable log context
  alert_thresholds:
    provider_failure_rate: 0.1
    api_response_time: 2000
```

### Testing Configuration

```yaml
# config.yaml - Testing
intervals:
  NFL:
    DraftKings: 10      # Very frequent for rapid testing
    FanDuel: 10
  NBA:
    DraftKings: 15
    FanDuel: 15

provider_config:
  DraftKings:
    rate_limit: 10.0    # Fast for testing
    timeout: 3          # Very short timeout
    max_retries: 0      # No retries in tests
    
monitoring:
  health_check_interval: 5    # Very frequent
  log_tail_lines: 10          # Minimal context
```

## Configuration Validation

### Validating Configuration Files

```python
# scripts/validate_config.py
import yaml
import sys
from pathlib import Path

def validate_config(config_path: str):
    """Validate configuration file structure."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        if 'intervals' not in config:
            print("❌ Missing 'intervals' section")
            return False
        
        intervals = config['intervals']
        if not isinstance(intervals, dict):
            print("❌ 'intervals' must be a dictionary")
            return False
        
        # Validate sport intervals
        for sport, providers in intervals.items():
            if not isinstance(providers, dict):
                print(f"❌ Providers for {sport} must be a dictionary")
                return False
            
            for provider, interval in providers.items():
                if not isinstance(interval, int) or interval <= 0:
                    print(f"❌ Invalid interval for {sport}.{provider}: {interval}")
                    return False
        
        print("✅ Configuration is valid")
        return True
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    validate_config(config_path)
```

### Configuration Testing

```bash
# Validate configuration
python scripts/validate_config.py config.yaml

# Test with different configurations
cp config.yaml config.yaml.backup
cp config.dev.yaml config.yaml
python run.py
# Test the application
cp config.yaml.backup config.yaml
```

## Environment-Specific Configuration

### Using Different Config Files

```bash
# Development
cp config.dev.yaml config.yaml

# Testing
cp config.test.yaml config.yaml

# Production
cp config.prod.yaml config.yaml
```

### Configuration Loading in Code

```python
# src/core/scheduler.py - Configuration loading
import os
import yaml
from pathlib import Path

def load_config():
    """Load configuration with environment overrides."""
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Environment variable overrides
    if os.getenv("PROVIDER_INTERVALS"):
        # Override intervals from environment
        import json
        intervals = json.loads(os.getenv("PROVIDER_INTERVALS"))
        config['intervals'] = intervals
    
    return config
```

## Dynamic Configuration

### Runtime Configuration Updates

```python
# src/core/config_manager.py
import yaml
import threading
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = {}
        self._lock = threading.Lock()
        self._last_modified = 0
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with self._lock:
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'r') as f:
                        self._config = yaml.safe_load(f) or {}
                    self._last_modified = self.config_path.stat().st_mtime
                else:
                    self._config = self._get_default_config()
                
                return self._config.copy()
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._get_default_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        # Check if file has been modified
        if self.config_path.exists():
            current_mtime = self.config_path.stat().st_mtime
            if current_mtime > self._last_modified:
                return self.load_config()
        
        with self._lock:
            return self._config.copy()
    
    def get_intervals(self) -> Dict[str, Dict[str, int]]:
        """Get provider intervals configuration."""
        config = self.get_config()
        return config.get('intervals', {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'intervals': {
                'NFL': {'DraftKings': 300},
                'NBA': {'DraftKings': 600}
            }
        }

# Global config manager instance
config_manager = ConfigManager()

# Use in scheduler
def get_intervals():
    return config_manager.get_intervals()
```

## Configuration Best Practices

### 1. Environment-Specific Files

```
config/
├── base.yaml          # Common configuration
├── development.yaml   # Development overrides
├── production.yaml    # Production overrides
└── testing.yaml       # Testing overrides
```

### 2. Configuration Validation

```bash
# Validate config before deployment
python -c "
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)
    assert 'intervals' in config, 'Missing intervals'
    for sport, providers in config['intervals'].items():
        for provider, interval in providers.items():
            assert isinstance(interval, int) and interval > 0
    print('✅ Config validation passed')
"
```

### 3. Secrets Management

```bash
# Use environment variables for sensitive data
export DRAFTKINGS_API_KEY="your-secret-key"
export FANDUEL_API_KEY="your-secret-key"

# In provider code
api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
```

### 4. Configuration Documentation

```yaml
# config.yaml with comments
intervals:
  # High-traffic sports: More frequent updates
  NFL:
    DraftKings: 300    # 5 minutes - NFL games change frequently
    FanDuel: 300
  
  # Medium-traffic sports: Standard updates  
  NBA:
    DraftKings: 600    # 10 minutes - Regular game rhythm
    FanDuel: 600
  
  # Low-traffic sports: Less frequent updates
  MLB:
    DraftKings: 900    # 15 minutes - Baseball games are slower
    FanDuel: 900
```

### 5. Monitoring Configuration

```yaml
# Add monitoring configuration
monitoring:
  # Health check settings
  health_check_interval: 60     # Check system health every minute
  log_tail_lines: 20           # Include last 20 log lines in status
  
  # Alert thresholds
  alert_thresholds:
    provider_failure_rate: 0.1   # Alert if >10% provider failures
    api_response_time: 1000      # Alert if >1000ms response time
    database_errors: 5           # Alert if >5 DB errors per hour
    
  # Performance targets
  performance_targets:
    api_response_time: 200      # Target: <200ms average response
    provider_success_rate: 0.95 # Target: >95% provider success
    data_freshness: 300         # Target: Data <5 minutes old
```

## Troubleshooting Configuration Issues

### Common Configuration Problems

#### 1. Missing Configuration File

```bash
# Error: Config file not found
# Solution: Create default config file
cat > config.yaml << EOF
intervals:
  NFL:
    DraftKings: 300
  NBA:
    DraftKings: 600
EOF
```

#### 2. Invalid YAML Syntax

```bash
# Error: YAML parsing error
# Solution: Validate YAML syntax
python -c "
import yaml
try:
    with open('config.yaml') as f:
        yaml.safe_load(f)
    print('YAML is valid')
except yaml.YAMLError as e:
    print(f'YAML Error: {e}')
"
```

#### 3. Invalid Interval Values

```python
# Check for invalid intervals
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

intervals = config.get('intervals', {})
for sport, providers in intervals.items():
    for provider, interval in providers.items():
        if not isinstance(interval, int) or interval <= 0:
            print(f"Invalid interval for {sport}.{provider}: {interval}")
```

#### 4. Environment Variable Conflicts

```bash
# Check for conflicting environment variables
echo "DB_PATH: $DB_PATH"
echo "LOG_LEVEL: $LOG_LEVEL"
echo "API_PORT: $API_PORT"

# Unset conflicting variables if needed
unset DB_PATH
unset LOG_LEVEL
```

### Configuration Debugging

```python
# Debug configuration loading
def debug_config():
    import os
    import yaml
    from pathlib import Path
    
    print("=== Configuration Debug Info ===")
    
    # Environment variables
    print(f"DB_PATH env: {os.getenv('DB_PATH')}")
    print(f"LOG_DIR env: {os.getenv('LOG_DIR')}")
    print(f"LOG_LEVEL env: {os.getenv('LOG_LEVEL')}")
    print(f"API_PORT env: {os.getenv('API_PORT')}")
    
    # Config file
    config_path = Path("config.yaml")
    print(f"Config file exists: {config_path.exists()}")
    print(f"Config file path: {config_path.absolute()}")
    
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        print(f"Config intervals: {config.get('intervals', {})}")
    
    print("=== End Debug Info ===")

# Add to scheduler initialization
# debug_config()
```

This comprehensive configuration guide ensures you can properly set up and manage the betting markets aggregator for any environment or use case.