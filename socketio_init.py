from app import create_app, socketio, db

# Create the Flask app
app = create_app()

# Ensure the database tables are created within an app context
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, debug=True)  # Start the app using SocketIO
