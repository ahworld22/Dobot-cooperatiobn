'''基于ssy版本的升级版，添加键盘控制'''
import speech_recognition as sr
from pynput import keyboard
import threading

# 创建全局控制标志
is_recording = False
stop_flag = False
audio_data = None
r = sr.Recognizer()


def on_press(key):
    global stop_flag
    try:
        if key == keyboard.Key.space:
            if not is_recording:
                print("\n空格键按下，开始录音...")
                stop_flag = False
                threading.Thread(target=record_audio).start()
            else:
                print("\n空格键按下，停止录音")
                stop_flag = True
    except Exception as e:
        print(f"按键错误: {e}")


def record_audio():
    global is_recording, audio_data

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        is_recording = True

        # 实时读取音频流
        audio_buffer = []
        while not stop_flag:
            try:
                chunk = r.listen(source, timeout=1, phrase_time_limit=1)
                audio_buffer.append(chunk)
            except sr.WaitTimeoutError:
                continue

        # 合并音频片段
        audio_data = sr.AudioData(b''.join([a.get_raw_data() for a in audio_buffer]),
                                  source.SAMPLE_RATE,
                                  source.SAMPLE_WIDTH)
    is_recording = False


# 启动键盘监听
listener = keyboard.Listener(on_press=on_press)
listener.start()

print("=== 语音识别程序 ===")
print("按下空格键开始/停止录音")

while True:
    if audio_data and not is_recording:
        try:
            text = r.recognize_google(audio_data, language='zh-CN')
            print(f"\n识别结果: {text}")
            audio_data = None  # 清空缓存
        except sr.UnknownValueError:
            print("无法识别音频内容")
        except sr.RequestError as e:
            print(f"请求错误: {e}")