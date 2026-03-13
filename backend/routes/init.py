from .auth_routes import auth_bp
from .sos_routes import sos_bp
from .helpline_routes import helpline_bp
from .user_routes import user_bp

def register_routes(app):
    """Register all blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(sos_bp, url_prefix='/api/sos')
    app.register_blueprint(helpline_bp, url_prefix='/api/helplines')
    app.register_blueprint(user_bp, url_prefix='/api/users')