import requests
import hashlib
from pathlib import Path
from config import Config


class TTSManager:
    def __init__(self):
        self.audio_dir = Path("audio_cache")
        self.audio_dir.mkdir(exist_ok=True)
        self.api_key = Config.AZURE_TTS_KEY
        self.region = Config.AZURE_TTS_REGION
        self.endpoint = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"

    def generate_audio(self, text, voice_name, speech_rate=1.0):
        """生成音频文件"""
        # 生成唯一文件名
        key = f"{text}_{voice_name}_{speech_rate}"
        filename = hashlib.md5(key.encode()).hexdigest() + ".mp3"
        audio_path = self.audio_dir / filename

        # 如果已存在，直接返回
        if audio_path.exists():
            return str(audio_path)

        try:
            rate_percent = int((speech_rate - 1.0) * 100)
            rate_str = f"{rate_percent:+d}%" if rate_percent != 0 else "0%"

            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
            }

            ssml = f"""
            <speak version='1.0' xml:lang='en-US'>
                <voice xml:lang='en-US' name='{voice_name}'>
                    <prosody rate='{rate_str}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """

            response = requests.post(
                self.endpoint,
                headers=headers,
                data=ssml.encode('utf-8'),
                timeout=10
            )

            if response.status_code == 200:
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                return str(audio_path)
            else:
                print(f"TTS API错误: {response.status_code}")
                return None

        except Exception as e:
            print(f"生成音频出错: {e}")
            return None


