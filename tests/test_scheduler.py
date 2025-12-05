# tests/test_scheduler.py
import time
import threading
from unittest.mock import patch, MagicMock
from src.core.scheduler import Scheduler

def test_scheduler_starts_threads():
    # Mock config load to return a known config
    with patch.object(Scheduler, 'load_config') as mock_load:
        mock_load.return_value = {
            "intervals": {
                "TEST_SPORT": {
                    "TEST_PROVIDER": 1
                }
            }
        }
        
        # Mock orchestrate to track calls
        with patch('src.core.scheduler.orchestrate') as mock_orchestrate:
            scheduler = Scheduler()
            scheduler.start()
            
            # Allow some time for the thread to run and trigger orchestrate
            time.sleep(1.5)
            
            scheduler.stop()
            
            # Verify orchestrate was called
            assert mock_orchestrate.called
            # Verify it was called with the correct sport
            mock_orchestrate.assert_called_with(sport_id="TEST_SPORT")
            
            # Verify thread count
            assert len(scheduler.threads) == 1
