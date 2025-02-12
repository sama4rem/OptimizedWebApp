from app import create_app
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Set a secret key for sessions (best practice: use environment variable)
    app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key")

    # Get the port from Render (default to 10000 if not found)
    port = int(os.environ.get("PORT", 10000))

    # Run the app on 0.0.0.0 to accept external requests
    app.run(host="0.0.0.0", port=port)
