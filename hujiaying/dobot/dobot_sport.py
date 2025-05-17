#第一版机械臂运动控制4.29
import socket
import time

def check_coordinates(x, y, z, rx, ry, rz):
    """
    检查坐标是否在机械臂运动范围内
    这里的范围是示例，需要根据实际机械臂手册修改
    """
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
    # 使能机器人指令
    enable_cmd = "EnableRobot()\n"
    dashboard_socket.send(enable_cmd.encode('utf-8'))
    response = dashboard_socket.recv(1024).decode('utf-8')
    print(f"使能机器人响应: {response}")


def set_global_speed(dashboard_socket):
    # 设置全局速度比例为 30%
    speed_cmd = "SpeedFactor(30)\n"
    dashboard_socket.send(speed_cmd.encode('utf-8'))
    response = dashboard_socket.recv(1024).decode('utf-8')
    print(f"设置全局速度响应: {response}")


def move_robot(movement_socket, x, y, z, rx, ry, rz):
    # 发送Sync指令确保队列清空
    sync_cmd = "Sync()\n"
    movement_socket.send(sync_cmd.encode('utf-8'))
    time.sleep(0.5)  # 适当增加等待时间

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
    """
    设置末端数字输出端口状态（队列指令）
    :param movement_socket: 已建立的运动指令端口连接
    :param index: 末端DO端子的编号 (int)
    :param status: DO端子的状态 (0或1)
    """
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


if __name__ == "__main__":
    # 集中定义点位参数（坐标 + 延时）
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

    # 连接Dashboard端口
    dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dashboard_socket.connect(('192.168.101.13', 29999))

    # 连接运动指令端口
    movement_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    movement_socket.connect(('192.168.101.13', 30003))

    # 使能机械臂
    enable_robot(dashboard_socket)

    # 设置全局速度为 30%
    set_global_speed(dashboard_socket)

    # ---------- 移动到 P1起始位置 ----------
    move_robot(movement_socket, *P1)
    # ---------- 移动到 吸车底盘 ----------
    move_robot(movement_socket, *P2)
    move_robot(movement_socket, *P3)
    ToolDO(movement_socket, 1, 1)  # 触发末端DO1信号
    time.sleep(2)  # 使用time.sleep实现延时
    move_robot(movement_socket, *P4)
    move_robot(movement_socket, *P5)  # 传递到人工区域
    time.sleep(2)
    ToolDO(movement_socket, 1, 0)  # 吸盘放气
    ToolDO(movement_socket, 2, 1)
    time.sleep(2)
    ToolDO(movement_socket, 2, 0)

    # ---------- 移动到 吸车架 ----------
    move_robot(movement_socket, *P1)  # 回到初始点P1
    move_robot(movement_socket, *P6)
    move_robot(movement_socket, *P7)
    ToolDO(movement_socket, 1, 1)  # 触发末端DO1信号
    time.sleep(2)
    move_robot(movement_socket, *P6)
    move_robot(movement_socket, *P5)  # 传递到人工区域
    time.sleep(2)
    ToolDO(movement_socket, 1, 0)  # 吸盘放气
    ToolDO(movement_socket, 2, 1)
    time.sleep(2)
    ToolDO(movement_socket, 2, 0)

    # ---------- 移动到 吸车前盖 ----------
    move_robot(movement_socket, *P1)  # 回到初始点P1
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P9)
    ToolDO(movement_socket, 1, 1)  # 触发末端DO1信号
    time.sleep(2)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P5)  # 传递到人工区域
    time.sleep(2)
    ToolDO(movement_socket, 1, 0)  # 吸盘放气
    ToolDO(movement_socket, 2, 1)
    time.sleep(2)
    ToolDO(movement_socket, 2, 0)

    # ---------- 移动到 吸右门 ----------
    move_robot(movement_socket, *P1)  # 回到初始点P1
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P10)
    ToolDO(movement_socket, 1, 1)  # 触发末端DO1信号
    time.sleep(2)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P5)  # 传递到人工区域
    time.sleep(2)
    ToolDO(movement_socket, 1, 0)  # 吸盘放气
    ToolDO(movement_socket, 2, 1)
    time.sleep(2)
    ToolDO(movement_socket, 2, 0)

    # ---------- 移动到 吸左门 ----------
    move_robot(movement_socket, *P1)  # 回到初始点P1
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P11)
    ToolDO(movement_socket, 1, 1)  # 触发末端DO1信号
    time.sleep(2)
    move_robot(movement_socket, *P8)
    move_robot(movement_socket, *P5)  # 传递到人工区域
    time.sleep(2)
    ToolDO(movement_socket, 1, 0)  # 吸盘放气
    ToolDO(movement_socket, 2, 1)
    time.sleep(2)
    ToolDO(movement_socket, 2, 0)
    move_robot(movement_socket, *P1)  # 回到初始点P1

    # 关闭连接
    movement_socket.close()
    dashboard_socket.close()
