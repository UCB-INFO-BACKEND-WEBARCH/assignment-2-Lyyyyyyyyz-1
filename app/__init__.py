from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

migrate = Migrate()

def create_app():
    
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    from app.routes.tasks import tasks_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)

    @app.route("/")
    def home():
        return {"message": "Task Manager API is running"}

    return app