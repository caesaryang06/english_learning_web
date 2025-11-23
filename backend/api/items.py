from flask import Blueprint, request, jsonify
from models.database import DatabaseManager

bp = Blueprint('items', __name__)
db = DatabaseManager()


@bp.route('/list', methods=['GET'])
def get_items():
    """获取学习内容列表"""
    item_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 50))
    items = db.get_items_for_learning(limit, item_type)
    return jsonify({'success': True, 'data': items})


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    stats = db.get_statistics()
    return jsonify({'success': True, 'data': stats})


@bp.route('/import', methods=['POST'])
def import_items():
    """导入学习内容"""
    data = request.json
    item_type = data.get('type')
    items = data.get('items', [])

    count = 0
    for item in items:
        success = db.add_item(
            item_type,
            item.get('english'),
            item.get('chinese'),
            item.get('pronunciation', ''),
            item.get('example_en', ''),
            item.get('example_zh', '')
        )
        if success:
            count += 1

    return jsonify({'success': True, 'count': count})


@bp.route('/test', methods=['GET'])
def get_test_items():
    """获取测试内容"""
    limit = int(request.args.get('limit', 20))
    items = db.get_items_for_test(limit)
    return jsonify({'success': True, 'data': items})
