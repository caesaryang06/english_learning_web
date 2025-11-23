from flask import Blueprint, request, jsonify, session
from models.database import DatabaseManager
import hashlib
import secrets
from functools import wraps

bp = Blueprint('auth', __name__)
db = DatabaseManager()


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 验证输入
    if not username or len(username) < 3:
        return jsonify({'success': False, 'error': '用户名至少3个字符'})

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': '请输入有效的邮箱'})

    if not password or len(password) < 6:
        return jsonify({'success': False, 'error': '密码至少6个字符'})

    # 检查用户名是否已存在
    if db.get_user_by_username(username):
        return jsonify({'success': False, 'error': '用户名已存在'})

    # 检查邮箱是否已存在
    if db.get_user_by_email(email):
        return jsonify({'success': False, 'error': '邮箱已被注册'})

    # 创建用户
    hashed_password = hash_password(password)
    user_id = db.create_user(username, email, hashed_password)

    if user_id:
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user_id': user_id
        })
    else:
        return jsonify({'success': False, 'error': '注册失败'})


@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'})

    # 验证用户
    user = db.get_user_by_username(username)
    if not user:
        return jsonify({'success': False, 'error': '用户名或密码错误'})

    hashed_password = hash_password(password)
    if user['password'] != hashed_password:
        return jsonify({'success': False, 'error': '用户名或密码错误'})

    # 设置 session
    session['user_id'] = user['id']
    session['username'] = user['username']

    # 生成 token
    token = secrets.token_hex(32)
    db.update_user_token(user['id'], token)

    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'avatar': user.get('avatar'),
            'token': token
        }
    })


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    user_id = session.get('user_id')
    if user_id:
        db.clear_user_token(user_id)

    session.clear()
    return jsonify({'success': True, 'message': '已登出'})


@bp.route('/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': '未登录'})

    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'})

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'avatar': user.get('avatar'),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None
        }
    })


@bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户资料"""
    user_id = session.get('user_id')
    data = request.json

    email = data.get('email')
    avatar = data.get('avatar')

    success = db.update_user_profile(user_id, email, avatar)

    if success:
        return jsonify({'success': True, 'message': '更新成功'})
    else:
        return jsonify({'success': False, 'error': '更新失败'})


@bp.route('/password', methods=['PUT'])
@login_required
def change_password():
    """修改密码"""
    user_id = session.get('user_id')
    data = request.json

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'success': False, 'error': '密码不能为空'})

    if len(new_password) < 6:
        return jsonify({'success': False, 'error': '新密码至少6个字符'})

    # 验证旧密码
    user = db.get_user_by_id(user_id)
    if hash_password(old_password) != user['password']:
        return jsonify({'success': False, 'error': '旧密码错误'})

    # 更新密码
    new_hashed = hash_password(new_password)
    success = db.update_user_password(user_id, new_hashed)

    if success:
        return jsonify({'success': True, 'message': '密码修改成功'})
    else:
        return jsonify({'success': False, 'error': '密码修改失败'})
