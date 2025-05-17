'''语音识别
https://blog.csdn.net/m0_53253879/article/details/138686377
'''
import json
import pyaudio
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel


def SaveWave(model):
    # 设置音频参数
    FORMAT = pyaudio.paInt16  # 音频流的格式
    RATE = 44100  # 采样率，单位Hz
    CHUNK = 4000  # 单位帧
    THRESHOLDNUM = 20  # 静默时间，超过这个个数就保存文件a
    THRESHOLD = 100  # 设定停止采集阈值

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=1,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    print("开始录音...")
    count = 0
    while count < THRESHOLDNUM:
        data = stream.read(CHUNK, exception_on_overflow=False)
        np_data = np.frombuffer(data, dtype=np.int16)
        frame_energy = np.mean(np.abs(np_data))
        # print(frame_energy)
        # 如果能量低于阈值持续时间过长，则停止录音
        if frame_energy < THRESHOLD:
            count += 1
        elif count > 0:
            count -= 1

        frames.append(data)
    print("停止录音!")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    rec = KaldiRecognizer(model, RATE)
    rec.SetWords(True)
    str_ret = ""
    for data in frames:
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if 'text' in result:
                str_ret += result['text']

    result = json.loads(rec.FinalResult())
    if 'text' in result:
        str_ret += result['text']

    str_ret = "".join(str_ret.split())
    return str_ret


if __name__ == "__main__":
    model = Model(r"/weights/vosk-model-small-cn-0.22")
    SetLogLevel(-1)

    while 1:
        res = SaveWave(model)
        if res != "" and res != None:
            print(res)

