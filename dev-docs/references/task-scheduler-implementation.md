# Task: Background Scheduler Implementation

**Completed:** 2025-12-05
**Description:** Implemented a background scheduler to trigger data fetching based on `config.yaml` intervals.

## Components
- **`src/core/scheduler.py`**:
    - `Scheduler` class: Manages background threads.
    - `start()`: Spawns a thread for each configured sport/provider.
    - `stop()`: Gracefully shuts down threads.
- **`run.py`**:
    - Initializes `Scheduler` before starting the Flask app.
    - Ensures scheduler stops on app exit.

## Configuration
- **`config.yaml`**: Defines intervals (in seconds) per Sport -> Provider.
  ```yaml
  intervals:
    NFL:
      DraftKings: 300
  ```

## Verification
- **Tests**: `tests/test_scheduler.py` verifies that `orchestrate` is called.
- **Run**: `python run.py` starts both the API and the scheduler. Logs will show "Starting scheduler..."

## Notes
- Uses `threading` for simplicity.
- `orchestrate(sport)` is currently triggered per provider interval, but runs for the whole sport. Future optimization: pass provider to `orchestrate`.
