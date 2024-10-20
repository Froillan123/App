from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO



db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    
    # Database setup
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and migration
    db.init_app(app)
    Migrate(app, db)

    # Import Blueprints and register them
    from routes.auth import auth
    from routes.main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # Initialize socketio with the app
    socketio.init_app(app)

    return app
