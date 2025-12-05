# run.py
"""Entry point to start the Betting Markets Flask API.

Running this script will create the Flask app using the factory and start
the development server on port 5000. In production you would use a proper
WSGI server (e.g., gunicorn) inside the Docker container.
"""

from src.api.factory import create_app

app = create_app()

if __name__ == "__main__":
    # Enable debug mode for local development; Docker will run with
    # the appropriate environment variables.
    app.run(host="0.0.0.0", port=5000, debug=True)
