from flask import Flask
from routes.auth import auth_bp
from routes.detection import detection_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(detection_bp, url_prefix='/detect')

if __name__ == '__main__':
    app.run(debug=True)
