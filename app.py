from flask import Flask, render_template
from admin.routes import admin_bp
from hotel_manager import hotel_manager_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(hotel_manager_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
