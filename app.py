import os
import sys
from flask import Flask
from config import Config
from extensions import db, login_manager
from routes.auth import bp as auth_bp
from routes.main import bp as main_bp
from routes.trip import bp as trip_bp
from routes.itinerary import bp as itinerary_bp
from routes.expense import bp as expense_bp
from routes.packing import bp as packing_bp
from routes.explorer import bp as explorer_bp

app = Flask(__name__)
if __name__ == "__main__":
    sys.modules["app"] = sys.modules[__name__]
app.config.from_object(Config)

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "images")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.config["SESSION_COOKIE_HTTPONLY"] = True

# Initialize extensions
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

from models import *  # noqa: F401,F403

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(trip_bp)
app.register_blueprint(itinerary_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(packing_bp)
app.register_blueprint(explorer_bp)

with app.app_context():
    from migrate import run_migrations
    run_migrations()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
