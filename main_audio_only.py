'''语音识别人机协作'''
import speech_recognition as sr
import socket
import time

# -------------------- 机械臂配置 --------------------
ROBOT_IP = '192.168.101.13'
DASHBOARD_PORT = 29999
MOVEMENT_PORT = 30003

# 点位参数（保持原定义）
P1 = (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157)
P2 = (249.4592, -230.2950, 276.5416, 176.6571, -0.3319, -108.0424)
P3 = (252.2934, -234.5704, 223.9143, 171.5326, -0.4312, -108.5486)
P4 = (222.0454, -224.5562, 440.8731, 179.3882, -0.4435, -108.6372)
P5 = (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509)
P6 = (230.0501, -376.7870, 412.6622, 175.2946, -0.4393, -129.8244)
P7 = (232.8893, -359.9239, 257.8296, 172.8682, -0.4384, -127.7273)
P8 = (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241)
P9 = (190.1676, -493.1779, 195.7462, 173.8494, -0.2792, -143.3572)
P10 = (262.1892, -470.9985, 189.2697, 179.1859, -0.2883, -135.6751)
P11 = (332.4647, -475.4962, 195.3145, -179.9835, -0.2912, -130.9234)


# -------------------- 机械臂控制函数 --------------------
def check_coordinates(x, y, z, rx, ry, rz):
    """坐标范围检查（保持原逻辑）"""
    x_min, x_max = -700, 700
    y_min, y_max = -700, 700
    z_min, z_max = 0, 1000
    return (x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max)


def connect_robot():
    """建立机器人连接"""
    dashboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    movement = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dashboard.connect((ROBOT_IP, DASHBOARD_PORT))
    movement.connect((ROBOT_IP, MOVEMENT_PORT))
    return dashboard, movement


def enable_robot(dashboard):
    """使能机器人（保持原逻辑）"""
    dashboard.send("EnableRobot()\n".encode())
    print("机器人已使能")


def set_speed(dashboard):
    """设置速度（保持原逻辑）"""
    dashboard.send("SpeedFactor(25)\n".encode())
    print("速度设置为30%")


# 封装各部件操作函数
def handle_chassis_operation():
    """处理车底盘抓取流程"""
    move_robot(movement_socket, *P1)
    move_robot(movement_socket, *P2)
    move_robot(movement_socket, *P3)
    ToolDO(movement_socket, 1, 1)
    time.sleep(5)
    move_robot(movement_socket, *P4)
    move_robot(movement_socket, *P5)
    time.sleep(5)
    ToolDO(movement_socket, 1, 0)
    ToolDO(movement_socket, 2, 1)
    time.sleep(5)
    ToolDO(movement_socket, 2, 0)


def handle_frame_operation():
    """处理车架抓取流程"""
    move_robot(movement_socket, *P1)
    move_robot(movement_socket, *P6)
    move_robot(movement_socket, *P7)
    ToolDO(movement_socket, 1, 1)
    time.sleep(5)
    move_robot(movement_socket, *P6)
    move_robot(movement_socket, *P5)
    time.sleep(5)
    ToolDO(movement_socket, 1, 0)
    ToolDO(movement_socket, 2, 1)
    time.sleep(5)
    ToolDO(movement_socket, 2, 0)


def handle_hood_operation():
    """处理车前盖抓取流程"""
    move_robot(movement_socket, *P1)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P9)
    ToolDO(movement_socket, 1, 1)
    time.sleep(5)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P5)
    time.sleep(5)
    ToolDO(movement_socket, 1, 0)
    ToolDO(movement_socket, 2, 1)
    time.sleep(5)
    ToolDO(movement_socket, 2, 0)


def handle_door_operation(side, target_point):
    """处理车门抓取流程（左右车门通用逻辑）"""
    move_robot(movement_socket, *P1)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *target_point)
    ToolDO(movement_socket, 1, 1)
    time.sleep(5)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P5)
    time.sleep(5)
    ToolDO(movement_socket, 1, 0)
    ToolDO(movement_socket, 2, 1)
    time.sleep(5)
    ToolDO(movement_socket, 2, 0)
    move_robot(movement_socket, *P1)


# 通用控制函数
def move_robot(socket, x, y, z, rx, ry, rz):
    """带坐标检查的移动函数（简化版）"""
    if not check_coordinates(x, y, z, rx, ry, rz):
        print("目标坐标超出范围！")
        return
    cmd = f"MovL({x},{y},{z},{rx},{ry},{rz},SpeedL=50,AccL=50)\n"
    socket.send(cmd.encode())
    print(f"移动到坐标: ({x}, {y}, {z})")


def ToolDO(socket, index, status):
    """末端执行器控制（简化版）"""
    cmd = f"ToolDO({index},{status})\n"
    socket.send(cmd.encode())
    print(f"DO{index}设置为{status}")


# -------------------- 语音识别配置 --------------------
TARGET_KEYWORDS = ["左车门", "右车门", "车前盖", "车架", "车底盘"]

# 关键词相似词库（更新版本，增加更多相似表达）
SYNONYM_DICT = {
    "左车门": ["左边的车门", "左侧车门", "左门", "左侧门", "左侧", "左边", "右边的车"],
    "右车门": ["右边的车门", "右侧车门", "右门", "右侧门", "右侧"],
    "车前盖": ["引擎盖", "发动机盖", "车头盖", "车前"],
    "车架": ["车身框架", "汽车骨架", "车体框架"],
    "车底盘": ["汽车底盘", "车底", "底盘"]
}

ALL_MATCH_KEYWORDS = {k: [k] + v for k, v in SYNONYM_DICT.items()}

COMMAND_MAP = {
    "左车门": lambda: handle_door_operation("左", P11),
    "右车门": lambda: handle_door_operation("右", P10),
    "车前盖": handle_hood_operation,
    "车架": handle_frame_operation,
    "车底盘": handle_chassis_operation
}


# -------------------- 语音处理函数 --------------------
def recognize_speech():
    """语音识别主函数"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("请说出部件名称（左边的车门/右边的车门/车前盖/车架/车底盘）...")
        audio = r.listen(source, timeout=5, phrase_time_limit=3)

    try:
        text = r.recognize_google(audio, language='zh-CN')
        print(f"识别结果：{text}")
        return match_keywords(text)
    except sr.UnknownValueError:
        print("无法理解音频，请清晰发音")
        return None
    except sr.RequestError as e:
        print(f"识别服务错误：{e}")
        return None


def match_keywords(text):
    """关键词匹配（支持相似词）"""
    for keyword, synonyms in ALL_MATCH_KEYWORDS.items():
        for word in synonyms:
            if word in text:
                return keyword
    return None


# -------------------- 主程序 --------------------
if __name__ == "__main__":
    # 初始化机器人连接
    dashboard_socket, movement_socket = connect_robot()
    enable_robot(dashboard_socket)
    set_speed(dashboard_socket)
    move_robot(movement_socket, *P1)  # 回到初始位置

    while True:
        try:
            # 语音识别获取指令
            command = recognize_speech()
            if command:
                print(f"执行指令：{command}")
                # 调用对应的机械臂操作
                COMMAND_MAP[command]()
                move_robot(movement_socket, *P1)  # 操作完成返回初始位置

        except KeyboardInterrupt:
            print("\n程序终止，返回初始位置")
            move_robot(movement_socket, *P1)
            break
        except Exception as e:
            print(f"操作异常：{e}")
            move_robot(movement_socket, *P1)

    # 关闭连接
    movement_socket.close()
    dashboard_socket.close()