from flask import Flask
from flask_socketio import SocketIO
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.secret_key = 's3cr3tK3y!@#456'  # Set your secret key here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database URI
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Optional: Set session lifetime
    return app

app = create_app()

# Initialize SocketIO with the app context
socketio = SocketIO(app)

# Import and register Blueprints after creating the app
from routes.auth import auth
from routes.main import main
app.register_blueprint(auth)
app.register_blueprint(main)

# SocketIO event to update active users
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True)
