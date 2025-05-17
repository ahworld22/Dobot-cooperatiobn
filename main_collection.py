# main.py - 整合Kinect手势识别与Dobot机械臂控制
import cv2
import mediapipe as mp
import math
import pykinect_azure as pykinect
import socket
import time
import threading
from queue import Queue
from hujiaying.voice.audio_recignition_test import record_and_recognize
import ctypes

# 全局变量
gesture_queue = Queue(maxsize=1)  # 用于存储识别到的手势
robot_busy = False  # 标记机械臂是否正在运动

COMMAND_MAP = {
    # 语音指令: 对应手势名称
    "车底盘": "one",
    "车架": "two",
    "车前盖": "three",
    "右车门": "six",
    "又车门": "six",
    "右边的车门": "six",
    "左边的车门": "gun",
    "左边的": "gun",
    "左边的车": "gun",
    "边的车": "gun",
    "车":"gun",
    "左": "gun",
    "车门": "gun",
    "门": "gun",
    "左边": "gun",
    "做车门": "gun",
    "坐车门": "gun",
    "锁车门": "gun"
}

# ---------------------------- Kinect手势识别部分 ----------------------------
def vector_2d_angle(v1, v2):
    '''求解二维向量的角度'''
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle_ = math.degrees(math.acos(
            (v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle_ = 65535.
    if angle_ > 180.:
        angle_ = 65535.
    return angle_


def hand_angle(hand_):
    '''获取对应手相关向量的二维角度,根据角度确定手势'''
    angle_list = []
    # 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[2][0])), (int(hand_[0][1]) - int(hand_[2][1]))),
        ((int(hand_[3][0]) - int(hand_[4][0])), (int(hand_[3][1]) - int(hand_[4][1])))
    )
    angle_list.append(angle_)
    # 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
        ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
    )
    angle_list.append(angle_)
    # 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
        ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
    )
    angle_list.append(angle_)
    # 无名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
        ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
    )
    angle_list.append(angle_)
    # 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
        ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
    )
    angle_list.append(angle_)
    return angle_list


def h_gesture(angle_list):
    '''二维约束的方法定义手势'''
    thr_angle = 65.
    thr_angle_thumb = 53.
    thr_angle_s = 49.
    gesture_str = None
    if 65535. not in angle_list:
        # if (angle_list[0] > thr_angle_thumb) and (angle_list[1] > thr_angle) and (angle_list[2] > thr_angle) and (
        #         angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
        #     gesture_str = "fist"
        # if (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
        #         angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s):
        #     gesture_str = "five"
        if (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_str = "gun"
        # elif (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
        #         angle_list[3] > thr_angle) and (angle_list[4] < thr_angle_s):
        #     gesture_str = "love"
        elif (angle_list[0] > 5) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_str = "one"
        elif (angle_list[0] < thr_angle_s) and (angle_list[1] > thr_angle) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] < thr_angle_s):
            gesture_str = "six"
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] > thr_angle):
            gesture_str = "three"
        # elif (angle_list[0] < thr_angle_s) and (angle_list[1] > thr_angle) and (angle_list[2] > thr_angle) and (
        #         angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
        #     gesture_str = "thumbUp"
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_str = "two"
        elif (angle_list[0] > thr_angle_thumb) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
                angle_list[3] < thr_angle_s) and (angle_list[4] > thr_angle):
            gesture_str = "four"
    return gesture_str


def gesture_recognition():
    """手势识别线程函数"""
    global robot_busy

    # 初始化Kinect
    pykinect.initialize_libraries()
    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1440P
    device = pykinect.start_device(config=device_config)

    # 初始化MediaPipe
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75
    )

    # 获取屏幕分辨率（Windows示例）
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    window_name = 'Kinect Hand Tracking'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # 设置窗口大小为屏幕宽度一半，高度为全屏高度
    cv2.resizeWindow(window_name, screen_width // 2, screen_height)

    # 移动窗口到屏幕右侧
    cv2.moveWindow(window_name, screen_width // 2, 0)

    while True:
        # 从Kinect获取图像
        capture = device.update()
        ret, color_image = capture.get_color_image()

        if not ret:
            continue

        # 转换颜色格式并镜像
        frame = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 手势检测
        results = hands.process(rgb_frame)
        current_gesture = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 绘制手部关键点
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 获取坐标并识别手势
                hand_local = [(lm.x * frame.shape[1], lm.y * frame.shape[0]) for lm in hand_landmarks.landmark]
                angle_list = hand_angle(hand_local)
                gesture_str = h_gesture(angle_list) or "Unknown"
                current_gesture = gesture_str
                cv2.putText(frame, gesture_str, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)

        # 显示结果
        cv2.imshow('Kinect Hand Tracking', frame)

        # 如果机械臂不忙且识别到手势，将手势加入队列
        if current_gesture and current_gesture != "Unknown" and not robot_busy:
            if gesture_queue.empty():  # 只在队列为空时添加新手势
                gesture_queue.put(current_gesture)
                robot_busy = True  # 标记机械臂为忙碌状态

        if cv2.waitKey(1) == 27:  # ESC键退出
            break

    # device.stop()
    device.close()
    cv2.destroyAllWindows()


# ---------------------------- Dobot机械臂控制部分 ----------------------------
def check_coordinates(x, y, z, rx, ry, rz):
    """检查坐标是否在机械臂运动范围内"""
    x_min, x_max = -700, 700
    y_min, y_max = -700, 700
    z_min, z_max = 0, 1000
    rx_min, rx_max = -180, 180
    ry_min, ry_max = -180, 180
    rz_min, rz_max = -180, 180
    return (x_min <= x <= x_max and
            y_min <= y <= y_max and
            z_min <= z <= z_max and
            rx_min <= rx <= rx_max and
            ry_min <= ry <= ry_max and
            rz_min <= rz <= rz_max)


def enable_robot(dashboard_socket):
    """使能机器人"""
    enable_cmd = "EnableRobot()\n"
    dashboard_socket.send(enable_cmd.encode('utf-8'))
    response = dashboard_socket.recv(1024).decode('utf-8')
    print(f"使能机器人响应: {response}")


def set_global_speed(dashboard_socket, speed=30):
    """设置全局速度比例30%"""
    speed_cmd = f"SpeedFactor({speed})\n"
    dashboard_socket.send(speed_cmd.encode('utf-8'))
    response = dashboard_socket.recv(1024).decode('utf-8')
    print(f"设置全局速度响应: {response}")


def move_robot(movement_socket, x, y, z, rx, ry, rz):
    """移动机械臂到指定位置"""
    # 发送Sync指令确保队列清空
    sync_cmd = "Sync()\n"
    movement_socket.send(sync_cmd.encode('utf-8'))
    time.sleep(0.5)

    # 检查坐标范围
    if not check_coordinates(x, y, z, rx, ry, rz):
        print("目标坐标超出机械臂运动范围，无法发送运动指令")
        return

    # 获取机械臂状态
    status_cmd = "RobotMode()\n"
    movement_socket.send(status_cmd.encode('utf-8'))
    status_response = movement_socket.recv(1024).decode('utf-8')
    if status_response.startswith("0,"):
        status = status_response.split(",")[1].strip("{}")
        if status == "9":  # 9表示有未清除的报警
            print("机械臂存在报警，无法运动，请先处理报警")
        else:
            # 发送直线运动指令，设置速度为50%，加速度为50%
            move_cmd = f"MovL({x},{y},{z},{rx},{ry},{rz},SpeedL=50,AccL=50)\n"
            movement_socket.send(move_cmd.encode('utf-8'))
            print(f"已发送运动指令到坐标: ({x}, {y}, {z}, {rx}, {ry}, {rz})")
    else:
        print(f"获取机械臂状态失败: {status_response}")


def ToolDO(movement_socket, index, status):
    """设置末端数字输出端口状态"""
    # 发送Sync指令确保队列清空
    sync_cmd = "Sync()\n"
    movement_socket.send(sync_cmd.encode('utf-8'))
    time.sleep(0.5)

    # 发送ToolDO指令
    tool_do_cmd = f"ToolDO({index},{status})\n"
    movement_socket.send(tool_do_cmd.encode('utf-8'))
    try:
        response = movement_socket.recv(1024).decode('utf-8')
        print(f"ToolDO响应: {response}")
    except Exception as e:
        print(f"ToolDO操作异常: {e}")


def execute_gesture_command(gesture, movement_socket):
    """根据手势执行相应的机械臂动作序列（支持位置、等待和工具操作）"""
    # 定义各个手势对应的机械臂动作序列
    # 每个动作可以是位置移动或工具操作
    global robot_busy
    robot_busy = True
    gesture_sequences = {
        # ---------- 移动到 吸车底盘 ----------
        "one": [
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},#1
            {"type": "move", "position": (249.4592, -230.2950, 276.5416, 176.6571, -0.3319, -108.0424), "wait": 0},#2
            {"type": "move", "position": (248.2934, -240.5704, 225.9143, -179.5326, 2.6632, -100.5486), "wait": 3},#3
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 1, "wait": 2.0},
            {"type": "move", "position": (222.0454, -224.5562, 440.8731, 179.3882, -0.4435, -108.6372), "wait": 0},#4
            {"type": "move", "position": (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509), "wait": 2.0},#5
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 0, "wait": 0.5},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 1, "wait": 2.0},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 0, "wait": 2.0}
        ],
        # ---------- 移动到 吸车架 ----------
        "two": [
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},#1
            {"type": "move", "position": (230.0501, -376.7870, 412.6622, 175.2946, -0.4393, -129.8244), "wait": 0},#6
            {"type": "move", "position": (234.8893, -365.9239, 256.8296, 177.8682, 5.4384, -129.7273), "wait": 3},#7
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 1, "wait": 2.0},
            {"type": "move", "position": (230.0501, -376.7870, 412.6622, 175.2946, -0.4393, -129.8244), "wait": 2.0},#6
            {"type": "move", "position": (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509), "wait": 2.0},#5
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 0, "wait": 0.5},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 1, "wait": 2.0},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 0, "wait": 2.0}
        ],
        # ---------- 移动到 吸车前盖 ----------
        "three": [
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},#1
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 0}, #8
            {"type": "move", "position": (187.8200, -487.7779, 194.1162, -176.9494, 0.8892, -143.2072), "wait": 3}, #9
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 1, "wait": 2.0},
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 0}, #8
            {"type": "move", "position": (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509), "wait": 2.0},#5
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 0, "wait": 0.5},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 1, "wait": 2.0},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 0, "wait": 2.0}
        ],
        # ---------- 移动到 吸右门 ----------
        "six": [
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},  #1
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 1}, #8
            {"type": "move", "position": (264.02, -479.062, 193.5245, -179.035, 0.9492, -136.4234), "wait": 3},  #10
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 1, "wait": 2.0},
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 0},#8
            {"type": "move", "position": (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509), "wait": 2.0},#5
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 0, "wait": 0.5},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 1, "wait": 2.0},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 0, "wait": 2.0}
        ],
        # ---------- 移动到 吸左门 ----------
        "gun": [
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},  #1
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 2}, #8
            {"type": "move", "position": (329.33, -477.902, 200.3545, -178.0, 2.4464, -130.7000), "wait": 3},  # 11
            {"type": "move", "position": (329.33, -477.902, 192.3545, -178.0, 2.4464, -130.7000), "wait": 3}, #11
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 1, "wait": 2.0},
            {"type": "move", "position": (239.7894, -448.8194, 378.3843, -177.6757, -0.4518, -135.7241), "wait": 0}, #8
            {"type": "move", "position": (150.7577, -535.1575, 529.3677, -172.4368, -0.4438, -149.5509), "wait": 2.0}, #5
            {"type": "tool", "command": "ToolDO", "index": 1, "status": 0, "wait": 0.5},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 1, "wait": 2.0},
            {"type": "tool", "command": "ToolDO", "index": 2, "status": 0, "wait": 2.0},
            {"type": "move", "position": (183.8339, -133.3408, 605.9380, -172.0599, -0.3282, -87.4157), "wait": 0},  #1
        ],
    }

    if gesture in gesture_sequences:
        print(f"开始执行手势命令序列: {gesture}")
        for action in gesture_sequences[gesture]:
            if action["type"] == "move":
                x, y, z, rx, ry, rz = action["position"]
                print(f"移动到位置: ({x}, {y}, {z}, {rx}, {ry}, {rz})")
                move_robot(movement_socket, x, y, z, rx, ry, rz)
                time.sleep(action["wait"])
            elif action["type"] == "tool":
                if action["command"] == "ToolDO":
                    print(f"执行工具操作: {action['command']}({action['index']}, {action['status']})")
                    ToolDO(movement_socket, action["index"], action["status"])
                    time.sleep(action["wait"])
        print(f"手势命令序列 {gesture} 执行完成")
        robot_busy = False  # 明确标记执行完成
        print("机械臂已就绪，等待新指令")  # 调试输出
    else:

        print(f"未知手势: {gesture}")

    # if gesture in gesture_sequences:
    #     print(f"执行手势命令: {gesture}")
    #     move_robot(movement_socket, *gesture_sequences[gesture])
    #     time.sleep(2)  # 等待机械臂完成动作




def robot_control():
    """机械臂控制线程函数"""
    global robot_busy

    # 连接Dashboard端口
    dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dashboard_socket.connect(('192.168.101.13', 29999))

    # 连接运动指令端口
    movement_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    movement_socket.connect(('192.168.101.13', 30003))

    # 使能机械臂
    enable_robot(dashboard_socket)

    # 设置全局速度为30%
    set_global_speed(dashboard_socket, 30)

    execution_count = 0  # 初始化执行计数器
    max_executions = 5  # 最大执行次数

    while execution_count < max_executions:
        mode = input("请选择控制模式（voice/gesture）: ").strip().lower()
        while mode not in ["voice", "gesture"]:
            print("输入无效，请重新选择")
            mode = input("请选择控制模式（voice/gesture）: ").strip().lower()
        if mode == "voice":
            while True:  # 添加循环，直到匹配成功或用户主动取消
                text = record_and_recognize()
                if not text:  # 如果识别失败（返回None）
                    print("识别失败，请重试")
                    continue  # 重新开始录音
                current_gesture_voice = COMMAND_MAP.get(text)
                if current_gesture_voice:
                    gesture_queue.put(current_gesture_voice)
                    print(f"匹配成功: {text} -> {current_gesture_voice}")
                    break  # 匹配成功，退出循环
                else:
                    print(f"未匹配指令: {text}，请重新说出指令")
        if not gesture_queue.empty():
            gesture = gesture_queue.get()
            gesture_queue.queue.clear()  # 清空可能堆积的指令
            print(f"开始执行第 {execution_count + 1} 次手势命令")
            execute_gesture_command(gesture, movement_socket)
            execution_count += 1
            robot_busy = False  # 机械臂动作完成，标记为不忙
            print(f"机械臂状态 {robot_busy} ")

    print(f"已完成 {max_executions} 次手势命令执行，停止机械臂")
    disable_cmd = "DisableRobot()\n"
    dashboard_socket.send(disable_cmd.encode('utf-8'))
    response = dashboard_socket.recv(1024).decode('utf-8')
    print(f"禁用机器人响应: {response}")

    # 关闭连接
    movement_socket.close()
    dashboard_socket.close()


if __name__ == '__main__':
    # 创建并启动手势识别线程
    gesture_thread = threading.Thread(target=gesture_recognition)
    gesture_thread.daemon = True
    gesture_thread.start()

    # 创建并启动机械臂控制线程
    robot_thread = threading.Thread(target=robot_control)
    robot_thread.daemon = True
    robot_thread.start()

    # 等待两个线程结束
    gesture_thread.join()
    robot_thread.join()