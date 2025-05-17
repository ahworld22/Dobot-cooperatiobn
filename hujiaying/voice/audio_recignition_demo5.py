'''csw版本'''
import time
import threading
from queue import Queue
import speech_recognition as sr
from pynput import keyboard

# 全局变量
voice_queue = Queue(maxsize=1)    # 语音指令队列
voice_recognizer = sr.Recognizer()
is_recording = False             # 录音状态
audio_source = None              # 麦克风源
audio_data = None                # 录音数据

def toggle_recording():
    """切换录音状态（按空格键触发）"""
    global is_recording, audio_source, audio_data

    if not is_recording:
        # 开始录音
        print("\n录音开始... (再次按空格键结束)")
        is_recording = True
        audio_source = sr.Microphone()

        def record_audio():
            global audio_data
            with audio_source as source:
                print("正在录音...")
                audio_data = voice_recognizer.listen(source, timeout=5)  # 最长5秒
                print("录音完成")

        # 在后台录音
        threading.Thread(target=record_audio, daemon=True).start()
    else:
        # 结束录音并识别
        is_recording = False
        time.sleep(0.5)  # 等待录音线程结束

        if audio_data:
            try:
                text = voice_recognizer.recognize_google(audio_data, language='zh-CN')
                print(f"识别结果: {text}")
                if not voice_queue.full():
                    voice_queue.put(text.lower())  # 存入队列
            except sr.UnknownValueError:
                print("无法识别音频")
            except Exception as e:
                print(f"语音识别错误: {e}")

        # 重置
        audio_source = None
        audio_data = None


print("语音控制已启动（按空格键开始/结束录音）")
with keyboard.Listener(on_press=lambda key: toggle_recording() if key == keyboard.Key.space else None) as listener:
       listener.join()