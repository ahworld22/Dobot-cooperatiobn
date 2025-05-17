'''lzy
'''
from gettext import install

import speech_recognition as sr

# 初始化识别器
r = sr.Recognizer()

# 使用默认麦克风作为音频来源
with sr.Microphone() as source:
    print("请说些什么吧...")
    audio = r.listen(source)

    try:
        # 使用Google Web Speech API进行识别
        print("Google Speech Recognition thinks you said:")
        text = r.recognize_google(audio, language='zh-CN')  # 根据需要设置语言
        print(text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")