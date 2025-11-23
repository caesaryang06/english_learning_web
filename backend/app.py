from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from api import items, learning, audio, auth
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 配置 session
app.secret_key = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CORS(app, resources={
#     r"/api/*": {
#         "origins": ["https://your-domain.com"],
#         "methods": ["GET", "POST", "PUT", "DELETE"],
#         "allow_headers": ["Content-Type", "Authorization"]
#     }
# })

CORS(app)

CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)


# 注册蓝图
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(items.bp, url_prefix='/api/items')
app.register_blueprint(learning.bp, url_prefix='/api/learning')
app.register_blueprint(audio.bp, url_prefix='/api/audio')


@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
