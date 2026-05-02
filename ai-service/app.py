from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Basic route
    @app.route('/')
    def home():
        return jsonify({"message": "AI Service Running 🚀"})

    # Health check route (important for later)
    @app.route('/health')
    def health():
        return jsonify({
            "status": "UP",
            "service": "AI Service",
        })

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)