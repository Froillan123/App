from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes.auth import auth  
from routes.main import main  
from models import * 
from os import system

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the db instance with the app
migrate = Migrate(app, db)


with app.app_context():
    db.create_all()  # Create tables based on the models

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
