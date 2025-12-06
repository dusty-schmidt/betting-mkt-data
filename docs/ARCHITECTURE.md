# Architecture Overview

Detailed architecture documentation for the Betting Markets Data Aggregator system.

## System Overview

The betting markets aggregator is a multi-component system designed to continuously collect, normalize, and serve betting odds data from multiple sportsbooks through a unified API.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Betting Markets System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Providers  │ -> │  Scheduler  │ -> │  Database   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         v                   v                   v              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ DraftKings  │    │ Background  │    │ SQLite DB   │         │
│  │ FanDuel     │    │ Threads     │    │ betting_    │         │
│  │ [Custom]    │    │ Parallel    │    │ markets.db  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             │                                  │
│                    ┌─────────────┐                             │
│                    │ Orchestrator│                             │
│                    └─────────────┘                             │
│                             │                                  │
│         ┌────────────────────────────────────────┐            │
│         │            REST API Layer              │            │
│         │          (Flask + Waitress)            │            │
│         │         Port 5000                      │            │
│         └────────────────────────────────────────┘            │
│                             │                                  │
│         ┌────────────────────────────────────────┐            │
│         │          Monitoring Layer              │            │
│         │         (LLM + Logging)                │            │
│         └────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Provider Layer

**Purpose**: Fetch data from external betting providers

**Location**: `src/providers/`

**Key Components**:
- `BaseProvider`: Abstract base class for all providers
- `DraftKingsProvider`: Production implementation
- `FanDuelProvider`: Example implementation
- Auto-discovery via `importlib`

**Responsibilities**:
- Connect to provider APIs
- Parse provider-specific data formats
- Normalize data to `StandardizedGame` format
- Handle rate limiting and error conditions
- Log all operations

**Data Flow**:
```
Provider API -> Raw Data -> Parsing -> StandardizedGame -> Provider Result
```

### 2. Scheduling Layer

**Purpose**: Manage data collection timing and orchestration

**Location**: `src/core/scheduler.py`

**Key Features**:
- Configuration-driven scheduling (`config.yaml`)
- Background threads for each provider/sport combination
- Graceful startup and shutdown
- Exception handling to prevent crashes

**Scheduling Strategy**:
```
Config.yaml -> Thread Pool -> Provider Execution -> Repeat
```

**Thread Management**:
- One thread per sport/provider combination
- Daemon threads for graceful shutdown
- Configurable intervals (300s for NFL, 600s for NBA)
- Sleep interval management for responsive shutdown

### 3. Database Layer

**Purpose**: Persistent storage and data management

**Location**: `src/core/database.py`

**Key Features**:
- SQLite database with connection context managers
- Normalized schema (games, odds tables)
- Connection pooling and error handling
- Foreign key constraints for data integrity

**Schema Design**:
```
games (sport, game_id, home_team, away_team, start_time)
   |
   | (Foreign Key)
   v
odds (game_id, provider, market, odds)
```

**Connection Pattern**:
```python
with get_connection() as conn:
    # Database operations
    # Auto-connection cleanup
```

### 4. Orchestration Layer

**Purpose**: Coordinate provider execution and data persistence

**Location**: `src/core/orchestration.py`

**Key Features**:
- Parallel execution of providers via threading
- Result aggregation and deduplication
- Database persistence coordination
- Error handling and logging

**Orchestration Flow**:
```
Scheduler Trigger -> Provider Discovery -> Parallel Fetch -> Data Merge -> DB Storage
```

### 5. API Layer

**Purpose**: Expose data via REST endpoints

**Location**: `src/api/`

**Key Components**:
- Flask application factory
- Blueprint-based route organization
- JSON serialization and error handling
- CORS support (future enhancement)

**API Endpoints**:
- `GET /api/v1/games`: List all games
- `GET /api/v1/arbitrage`: Placeholder for arbitrage detection
- `GET /api/v1/status`: AI-powered system health

### 6. Monitoring Layer

**Purpose**: System health monitoring and AI assistance

**Location**: `src/llm/monitor.py`

**Key Features**:
- Log analysis and pattern recognition
- Database statistics collection
- LLM-powered status reporting
- Failure analysis and remediation suggestions

**Monitoring Flow**:
```
System State -> Data Collection -> LLM Analysis -> Status Report
```

## Data Flow Architecture

### Primary Data Flow

```
1. Scheduler triggers data collection
   │
   ├─── reads config.yaml for intervals
   ├─── creates background thread per provider/sport
   └─── starts thread execution

2. Provider execution begins
   │
   ├─── BaseProvider.fetch_odds() called
   ├─── Provider-specific API calls
   ├─── Raw data parsing and normalization
   └─── Returns List[StandardizedGame]

3. Orchestration coordinates results
   │
   ├─── Parallel provider execution via threading
   ├─── Result aggregation
   ├─── Deduplication by sport/game_id
   └─── Database persistence

4. Database storage
   │
   ├─── Games table: INSERT OR IGNORE
   ├─── Odds table: Bulk INSERT
   └─── Transaction commit

5. API serves data
   │
   ├─── GET /api/v1/games queries database
   ├─── JSON serialization
   └─── HTTP response to client
```

### Error Handling Flow

```
Provider Error
    │
    ├─── Exception caught and logged
    ├─── Continue with other providers
    ├─── Scheduler thread continues
    └─── Log error details for monitoring

Database Error
    │
    ├─── Connection context manager cleanup
    ├─── Rollback transaction if needed
    ├─── Log error with context
    └─── Continue with next operation

API Error
    │
    ├─── JSON error response
    ├─── Appropriate HTTP status code
    ├─── Log error details
    └─── Return to client
```

## Threading Model

### Thread Architecture

```
Main Thread (run.py)
    │
    ├─── Start Scheduler (background threads)
    │    ├─── NFL Thread → DraftKings (300s interval)
    │    ├─── NFL Thread → FanDuel (300s interval)
    │    ├─── NBA Thread → DraftKings (600s interval)
    │    └─── [Additional sport/provider combinations]
    │
    ├─── Start Flask API Server (main thread)
    │    ├─── Request handling
    │    ├─── Database queries
    │    └─── Response generation
    │
    └─── Graceful shutdown handling
         ├─── Stop scheduler
         ├─── Join threads
         └─── Clean shutdown
```

### Thread Safety Considerations

1. **Database Connections**: Context managers ensure thread-safe connections
2. **Shared Data**: Explicit locking for shared state
3. **Provider Execution**: Each provider runs in isolation
4. **File Access**: Log files use proper locking mechanisms

### Locking Strategy

```python
# Example from orchestration.py
import threading

results = []
results_lock = threading.Lock()

def run_provider(provider, sport_id, results):
    try:
        odds = provider.fetch_odds(sport_id)
        with results_lock:
            results.extend(odds)
    except Exception as e:
        log.error(f"Provider failed: {e}")
```

## Configuration Architecture

### Configuration Hierarchy

```
1. Default Configuration (hardcoded)
2. config.yaml file
3. Environment variables
4. Runtime overrides (future)
```

### Configuration Flow

```
Environment Variables → config.yaml → Application Settings
```

### Key Configuration Areas

1. **Scheduling**: `config.yaml` intervals
2. **Database**: `DB_PATH` environment variable
3. **Logging**: `LOG_LEVEL`, `LOG_DIR` environment variables
4. **API**: `API_PORT` environment variable

## Scalability Considerations

### Current Architecture Limits

- **Database**: SQLite file-based (suitable for small-medium datasets)
- **Threading**: Python GIL limits (consider process-based scaling)
- **Memory**: All data in memory during provider execution
- **Storage**: Single file database (no horizontal scaling)

### Scaling Strategies

#### Horizontal Scaling (Future)

```
Load Balancer
    ├─── API Server Instance 1
    ├─── API Server Instance 2
    └─── API Server Instance N

         ├─── Shared Database (PostgreSQL)
         ├─── Message Queue (Redis/RabbitMQ)
         └─── Distributed Caching (Redis)
```

#### Vertical Scaling

- Increase worker threads for provider execution
- Optimize database indexes and queries
- Add connection pooling
- Implement data archiving strategies

#### Caching Strategies

```
Provider Cache (5-minute TTL)
    │
    ├─── Reduces API calls
    ├─── Improves response time
    └─── Handles provider downtime

API Response Cache
    │
    ├─── Caches database queries
    ├─── Reduces database load
    └─── Improves concurrent access
```

## Deployment Architecture

### Development Environment

```
Local Development
    ├─── Single process
    ├─── SQLite database
    ├─── File-based logs
    └─── Local provider testing
```

### Production Environment

```
Containerized Deployment
    ├─── Docker container
    ├─── Volume-mounted database
    ├─── Centralized logging
    ├─── Health check endpoints
    └─── Graceful shutdown handling
```

### Infrastructure Components

```
┌─────────────────────────────────────────────┐
│              Production Stack               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │           Application Container          │ │
│  │  ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │  Scheduler  │ │     API Server      │ │ │
│  │  │   Threads   │ │   (Waitress)        │ │ │
│  │  └─────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │         Persistent Storage               │ │
│  │  ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │ SQLite DB   │ │   Log Files         │ │ │
│  │  │ betting_    │ │   (log rotation)    │ │ │
│  │  │ markets.db  │ │                     │ │ │
│  │  └─────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│ ─┐ │
│  │           External ┌──────────────────────────────────────── Dependencies          │ │
│  │  ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │ DraftKings  │ │   FanDuel API       │ │ │
│  │  │    API      │ │                     │ │ │
│  │  └─────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

## Security Architecture

### Current Security Measures

1. **No Authentication**: Currently open API (suitable for internal use)
2. **Input Validation**: Parameterized database queries
3. **Error Handling**: No sensitive data in error messages
4. **Logging**: Structured logging without sensitive data

### Security Recommendations

1. **API Authentication**: API keys or JWT tokens
2. **Rate Limiting**: Prevent abuse of API endpoints
3. **HTTPS/TLS**: Encrypt data in transit
4. **CORS Policy**: Restrict cross-origin requests
5. **Input Sanitization**: Validate all API inputs
6. **Secret Management**: Environment variables for API keys

### Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| API Abuse | High | Rate limiting, authentication |
| Data Injection | High | Parameterized queries |
| Provider API Blocking | Medium | Respectful rate limiting |
| Database Corruption | High | Connection management, backups |
| Information Disclosure | Medium | Error message sanitization |

## Monitoring and Observability

### Logging Architecture

```
Application Logs
    │
    ├─── Structured logging via get_logger()
    ├─── Log rotation (5MB files)
    ├─── Log levels (DEBUG, INFO, WARNING, ERROR)
    └─── Context-rich messages

Log Flow
    │
    ├─── Application → log/app.log
    ├─── Rotation → log/app.log.1, .2, etc.
    ├─── Monitoring → LLM analysis
    └─── Alerting → (future enhancement)
```

### Health Monitoring

1. **System Status**: `/api/v1/status` endpoint
2. **Database Health**: Connection and query monitoring
3. **Provider Health**: Success/failure rates
4. **API Performance**: Response time tracking
5. **Resource Usage**: Memory and CPU monitoring

### Metrics and Alerting (Future)

```
Application Metrics
    │
    ├─── Provider fetch success rates
    ├─── API response times
    ├─── Database query performance
    ├─── Error rates by component
    └─── Data freshness indicators

Alerting Triggers
    │
    ├─── High provider failure rates
    ├─── Database connection issues
    ├─── API response time degradation
    └─── Unusual error patterns
```

## Development Architecture

### Code Organization

```
src/
├── api/              # REST API layer
├── core/             # Core services
│   ├── database.py   # Database layer
│   ├── scheduler.py  # Scheduling service
│   ├── orchestration.py # Provider coordination
│   ├── logger.py     # Logging configuration
│   ├── models.py     # Data models
│   └── schemas.py    # Pydantic schemas
├── providers/        # Provider implementations
│   ├── base.py       # Abstract provider
│   ├── draftkings/   # DraftKings implementation
│   └── [other providers]/
├── llm/              # AI monitoring
└── [test directories]
```

### Development Workflow

1. **Provider Development**: Follow BaseProvider interface
2. **Testing Strategy**: Unit tests → Integration tests → API tests
3. **Configuration Management**: Environment variables and config files
4. **Documentation**: Inline code docs and separate guides

### Testing Architecture

```
Test Strategy
    │
    ├─── Unit Tests: Individual components
    ├─── Integration Tests: Component interactions
    ├─── API Tests: Endpoint functionality
    ├─── Provider Tests: Real API integration
    └─── End-to-End Tests: Full system testing

Test Data
    │
    ├─── Mock data for unit tests
    ├─── Real data for integration tests
    ├─── Test database for API tests
    └─── Staging environment for E2E tests
```

This architecture provides a solid foundation for understanding how the betting markets aggregator system works and how to extend it with new features and providers.