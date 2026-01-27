from flask import Flask

app = Flask(__name__)

<<<<<<< Updated upstream
@app.route('/')
def home():
    return "Hello from Sarjil's Python Project!"

if __name__ == "__main__":
    app.run(debug=True)
=======
# This file is kept for backward compatibility
# All hotel manager code has been moved to hotel_manager/ folder
# Use app.py as the main entry point instead

if __name__ == "__main__":
    print("Please run app.py instead")
    print("Usage: python app.py")
>>>>>>> Stashed changes
