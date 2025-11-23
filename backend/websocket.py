from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 在线用户
online_users = {}


@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in online_users:
        del online_users[request.sid]


@socketio.on('join_study_room')
def handle_join_room(data):
    """加入学习室"""
    room = data.get('room', 'default')
    username = data.get('username', 'Anonymous')

    join_room(room)
    online_users[request.sid] = {
        'username': username,
        'room': room
    }

    # 通知房间其他用户
    emit('user_joined', {
        'username': username,
        'user_count': len([u for u in online_users.values() if u['room'] == room])
    }, room=room)


@socketio.on('leave_study_room')
def handle_leave_room(data):
    """离开学习室"""
    room = data.get('room', 'default')
    leave_room(room)

    if request.sid in online_users:
        username = online_users[request.sid]['username']
        del online_users[request.sid]

        # 通知房间其他用户
        emit('user_left', {
            'username': username,
            'user_count': len([u for u in online_users.values() if u['room'] == room])
        }, room=room)


@socketio.on('sync_progress')
def handle_sync_progress(data):
    """同步学习进度"""
    room = data.get('room')
    progress = data.get('progress')

    # 广播给房间所有用户
    emit('progress_updated', {
        'user': online_users[request.sid]['username'],
        'progress': progress
    }, room=room, include_self=False)


@socketio.on('send_message')
def handle_message(data):
    """发送消息"""
    room = data.get('room')
    message = data.get('message')

    emit('receive_message', {
        'user': online_users[request.sid]['username'],
        'message': message,
        'timestamp': datetime.now().isoformat()
    }, room=room)


@socketio.on('request_help')
def handle_help_request(data):
    """请求帮助"""
    room = data.get('room')
    word = data.get('word')

    emit('help_requested', {
        'user': online_users[request.sid]['username'],
        'word': word
    }, room=room, include_self=False)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
