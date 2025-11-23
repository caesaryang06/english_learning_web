from flask import Blueprint, request, jsonify, send_file
from utils.tts import TTSManager
import os

bp = Blueprint('audio', __name__)
tts = TTSManager()


@bp.route('/generate', methods=['POST'])
def generate_audio():
    """生成语音"""
    data = request.json
    text = data.get('text')
    voice_name = data.get('voice_name', 'en-US-JennyNeural')
    speech_rate = data.get('speech_rate', 1.0)

    audio_path = tts.generate_audio(text, voice_name, speech_rate)

    if audio_path and os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        return jsonify({'success': False, 'error': 'Failed to generate audio'}), 500


@bp.route('/voices', methods=['GET'])
def get_voices():
    """获取可用发音人列表"""
    voices = {
        "Jenny (女声-自然)": "en-US-JennyNeural",
        "Guy (男声-自然)": "en-US-GuyNeural",
        "Aria (女声-活泼)": "en-US-AriaNeural",
        "Davis (男声-沉稳)": "en-US-DavisNeural",
        "Jane (女声-优雅)": "en-US-JaneNeural",
        "Jason (男声-专业)": "en-US-JasonNeural",
        "Sara (女声-温柔)": "en-US-SaraNeural",
        "Tony (男声-友好)": "en-US-TonyNeural",
    }
    return jsonify({'success': True, 'data': voices})
