# Betting Markets Aggregator

A set-and-forget service that fetches betting odds from multiple providers and exposes them via API.

## Quick Start

### Docker (Recommended)
```bash
docker build -t betting-markets .
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  betting-markets
```

### Local
```bash
uv sync
uv run python run.py
```

## API

- `GET /api/v1/games` - List all games
- `GET /api/v1/status` - Service health

Default: `http://localhost:5000/api/v1/`

## Configuration

Edit `config.yaml` to set fetch intervals per sport/provider.

## Documentation

- **Architecture**: `docs/ARCHITECTURE.md`
- **Development**: `DEV-README.md`
