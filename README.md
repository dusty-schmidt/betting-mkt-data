# Betting Markets Data Aggregator

A real-time sports betting odds aggregation service that fetches, normalizes, and exposes betting data from multiple providers through a unified REST API.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- `uv` package manager
- Git (for development workflow)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd betting-mkt-data

# Install dependencies
uv sync

# Initialize database
uv run python -c "from src.core.database import init_db; init_db()"

# Start the application
uv run python run.py
```

The service will start on `http://localhost:5000`

### Environment Variables

```bash
# Database path (default: betting_markets.db)
export DB_PATH=/path/to/database.db

# Log directory (default: logs/)
export LOG_DIR=/path/to/logs

# Server port (default: 5000)
export API_PORT=5000

# Log level (default: INFO)
export LOG_LEVEL=INFO
```

## 📋 Overview

This application aggregates sports betting odds from multiple providers, normalizes the data, and provides a unified API interface. It features automated data collection, intelligent failure handling, and AI-powered monitoring.

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Providers  │ -> │  Scheduler  │ -> │  Database   │ -> │     API     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       v                  v                  v                  v
DraftKings           Background        SQLite DB        REST Endpoints
FanDuel              Threads           betting_markets  Port 5000
[Custom...]          Parallel          .db
```

### Key Features

- **Multi-Provider Support**: Auto-discovery of betting providers via `importlib`
- **Real-Time Data**: Configurable fetch intervals per sport/provider
- **Normalized Data**: Standardized formats across all providers
- **Thread-Safe**: Explicit locking for concurrent operations
- **Health Monitoring**: AI-powered status reporting and failure analysis
- **Production Ready**: Log rotation, error handling, graceful shutdowns

## 🏗️ Project Structure

```
betting-mkt-data/
├── src/
│   ├── api/              # Flask REST API
│   ├── core/             # Core services (DB, scheduler, orchestration)
│   ├── providers/        # Betting data providers
│   │   ├── base.py       # Abstract base provider class
│   │   └── draftkings/   # DraftKings implementation
│   └── llm/              # AI monitoring integration
├── docs/                 # Detailed documentation
├── tests/                # Test suite
├── config.yaml           # Scheduling configuration
└── run.py               # Application entry point
```

## 🔧 Configuration

Update `config.yaml` to customize fetch intervals:

```yaml
intervals:
  NFL:
    DraftKings: 300   # 5 minutes
    FanDuel: 300
  NBA:
    DraftKings: 600   # 10 minutes
    FanDuel: 600
  MLB:
    DraftKings: 900   # 15 minutes
    FanDuel: 900
```

## 📚 Documentation

- **[API Reference](docs/API.md)** - REST endpoints and response formats
- **[Database Guide](docs/DATABASE.md)** - Schema, operations, and best practices
- **[Provider Development](docs/PROVIDERS.md)** - How to add new betting providers
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and flow
- **[Configuration](docs/CONFIGURATION.md)** - Complete configuration reference
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🧪 Development

### Workflow

Use the automated development workflow:

```bash
# Start work session (creates timestamped work log)
./dev-workflow.sh start

# Make your changes...

# End work session (commits and updates work log)
./dev-workflow.sh end
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_api.py -v

# Run with coverage
uv run pytest --cov=src tests/
```

### Debugging

```bash
# Monitor application logs
tail -f logs/app.log

# Check database contents
sqlite3 betting_markets.db ".tables"
sqlite3 betting_markets.db "SELECT * FROM games LIMIT 5;"

# Test API endpoints
curl http://localhost:5000/api/v1/games
curl http://localhost:5000/api/v1/status
```

## 🛠️ Development Guidelines

### Code Standards

1. **Logging**: Always use `get_logger(__name__)`, never `print()`
2. **Database**: Use context managers with `get_connection()`
3. **Threading**: Explicit locking with `threading.Lock()`
4. **Providers**: Inherit from `BaseProvider` for auto-discovery
5. **Models**: Extend `BaseDataModel` for new data structures

### Database Access

```python
from src.core.database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE sport = ?", ("NFL",))
    results = cur.fetchall()
```

### Logging

```python
from src.core.logger import get_logger

log = get_logger(__name__)
log.info("Starting data fetch", extra={"sport": "NFL", "provider": "DraftKings"})
log.error("Failed to fetch odds", exc_info=True)
```

## 🚨 Known Issues

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for current issues and workarounds.

## 📄 License

[Add your license information here]

## 🤝 Contributing

1. Check current tasks in `dev-docs/TASKS.md`
2. Use `./dev-workflow.sh start` before making changes
3. Follow the coding standards above
4. Write tests for new features
5. Update documentation as needed
6. Use `./dev-workflow.sh end` to complete work

## 📞 Support

- Check the troubleshooting guide
- Review application logs in `logs/app.log`
- Examine work logs in `dev-docs/work-logs/`
- Review current tasks in `dev-docs/TASKS.md`