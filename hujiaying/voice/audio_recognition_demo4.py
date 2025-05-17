'''
ssy
https://blog.csdn.net/u014164303/article/details/145665843'''
import speech_recognition as sr

# 创建一个 Recognizer 对象
r = sr.Recognizer()

# 使用麦克风作为音频输入
with sr.Microphone() as source:
    print("请说话...")
    # 调整环境噪音
    r.adjust_for_ambient_noise(source)
    # 录制音频
    audio = r.listen(source)

try:
    # 使用 Google 语音识别服务进行识别
    text = r.recognize_google(audio, language='zh-CN')
    print("识别结果: " + text)
except sr.UnknownValueError:
    print("无法识别音频内容")
except sr.RequestError as e:
    print(f"请求错误; {e}")
