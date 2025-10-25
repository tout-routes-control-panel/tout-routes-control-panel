import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from src.models.admin_models import db
from src.routes.admin_auth import admin_auth_bp
from src.routes.captain_routes import captain_bp
from src.routes.user_routes import user_routes_bp
from src.routes.booking_routes import booking_bp
from src.routes.financial_routes import financial_bp
from src.routes.dashboard_routes import dashboard_bp
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for frontend
CORS(app)

# Register all blueprints with specific API prefixes
app.register_blueprint(admin_auth_bp, url_prefix='/api/admin')
app.register_blueprint(captain_bp, url_prefix='/api/captains')
app.register_blueprint(user_routes_bp, url_prefix='/api/users')
app.register_blueprint(booking_bp, url_prefix='/api/bookings')
app.register_blueprint(financial_bp, url_prefix='/api/financials')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# This route must be placed AFTER all API blueprint registrations
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

