'''最终使用版本'''
import speech_recognition as sr
from pynput import keyboard
import threading

def record_and_recognize():
    """按下空格键开始录音，按下Enter键结束录音并识别"""
    r = sr.Recognizer()
    recording = False
    stop_recording = False
    audio_data = None

    def on_press(key):
        nonlocal recording, stop_recording
        try:
            if key == keyboard.Key.space and not recording:
                recording = True
                print("录音中... (按Enter键结束)")
            elif key == keyboard.Key.enter and recording:
                stop_recording = True
                return False  # 停止监听
        except AttributeError:
            pass  # 忽略特殊键

    print("按下空格键开始录音，按Enter键结束...")

    # 启动键盘监听
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    with sr.Microphone() as source:
        # 等待开始录音
        while not recording and not stop_recording:
            pass

        if recording:
            # 开始录音
            audio_data = r.listen(source, phrase_time_limit=10)  # 最长10秒录音

    # 识别语音
    if audio_data:
        try:
            text = r.recognize_google(audio_data, language='zh-CN')
            print(f"识别结果: {text}")
            return text
        except sr.UnknownValueError:
            print("无法识别音频内容")
            return None
        except sr.RequestError as e:
            print(f"请求错误: {e}")
            return None
    else:
        print("未录制到音频")
        return None

if __name__ == "__main__":
    record_and_recognize()