from flask import Blueprint, request, jsonify
from models.database import DatabaseManager

bp = Blueprint('learning', __name__)
db = DatabaseManager()


@bp.route('/record', methods=['POST'])
def record_learning():
    """记录学习"""
    data = request.json
    item_id = data.get('item_id')
    is_correct = data.get('is_correct', False)

    success = db.record_learning(item_id, is_correct)

    return jsonify({
        'success': success,
        'message': '记录成功' if success else '记录失败'
    })


@bp.route('/review/add', methods=['POST'])
def add_to_review():
    """添加到复习库"""
    data = request.json
    items = data.get('items', [])

    success = db.add_to_review(items)

    return jsonify({
        'success': success,
        'message': f'已添加 {len(items)} 项到复习库' if success else '添加失败'
    })


@bp.route('/review/list', methods=['GET'])
def get_review_list():
    """获取复习列表"""
    limit = int(request.args.get('limit', 50))
    items = db.get_review_items(limit)

    return jsonify({
        'success': True,
        'data': items
    })


@bp.route('/review/mark', methods=['POST'])
def mark_reviewed():
    """标记为已复习"""
    data = request.json
    item_id = data.get('item_id')

    success = db.mark_as_reviewed(item_id)

    return jsonify({
        'success': success,
        'message': '标记成功' if success else '标记失败'
    })


@bp.route('/history', methods=['GET'])
def get_learning_history():
    """获取学习历史"""
    days = int(request.args.get('days', 7))
    history = db.get_learning_history(days)

    return jsonify({
        'success': True,
        'data': history
    })


@bp.route('/statistics/detail', methods=['GET'])
def get_detailed_statistics():
    """获取详细统计"""
    stats = db.get_detailed_statistics()

    return jsonify({
        'success': True,
        'data': stats
    })


@bp.route('/progress/today', methods=['GET'])
def get_today_progress():
    """获取今日进度"""
    progress = db.get_today_progress()

    return jsonify({
        'success': True,
        'data': progress
    })


@bp.route('/streak', methods=['GET'])
def get_learning_streak():
    """获取连续学习天数"""
    streak = db.get_learning_streak()

    return jsonify({
        'success': True,
        'data': {
            'streak_days': streak,
            'message': f'已连续学习 {streak} 天'
        }
    })
