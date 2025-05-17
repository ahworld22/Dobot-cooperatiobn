import time, ctypes


# 提供类方法，获取时间差
class SingleTimer(object):
    __freq = None
    __beginCount = 0
    __endCount = 0

    @classmethod
    def counter(cls):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(freq))
        return freq.value

    @classmethod
    def beginCount(cls):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        cls.__freq = freq.value
        cls.__beginCount = cls.counter()
        # 时间差，精确到微秒

    @classmethod
    def secondsDiff(cls):
        cls.__endCount = cls.counter()
        return (cls.__endCount - cls.__beginCount) / (cls.__freq + 0.)


# 提供实例方法，获取时间差
class Timer(object):
    def __init__(self):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        self.__freq = freq.value
        self.__beginCount = self.counter()

    def counter(self):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(freq))
        # print(ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq)))
        return freq.value

    def beginCount(self):
        self.__beginCount = self.counter()
        # 时间差，精确到微秒

    def secondsDiff(self):
        self.__endCount = self.counter()
        return (self.__endCount - self.__beginCount) / (self.__freq + 0.)


if __name__ == '__main__':
    r = Timer()
    for i in range(10):
        time.sleep(1)
        print(r.secondsDiff())
