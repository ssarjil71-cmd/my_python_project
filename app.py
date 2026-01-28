from flask import Flask, render_template
from admin.routes import admin_bp
from hotel_manager.routes import manager_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(manager_bp, url_prefix="/manager")

    @app.route("/")
    def home():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
