from app import create_app

app = create_app()

if __name__ == "__main__":
    # For local dev only. In Docker we'll run via gunicorn.
    app.run(host="0.0.0.0", port=8000)
