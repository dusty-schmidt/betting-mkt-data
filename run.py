# run.py
"""Entry point to start the Betting Markets Flask API.

Running this script will create the Flask app using the factory and start
the development server on port 5000. In production you would use a proper
WSGI server (e.g., gunicorn) inside the Docker container.
"""

from src.api.factory import create_app
from src.core.scheduler import Scheduler

app = create_app()

if __name__ == "__main__":
    # Start the background scheduler
    scheduler = Scheduler()
    scheduler.start()
    
    try:
        # Use waitress for production-ready serving
        # Threads=4 is a reasonable default for this workload
        from waitress import serve
        print("Starting server on 0.0.0.0:5000 via Waitress...")
        serve(app, host="0.0.0.0", port=5000, threads=4)
    finally:
        # Ensure scheduler stops when app exits
        scheduler.stop()
