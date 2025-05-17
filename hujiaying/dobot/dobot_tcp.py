#测试版机械臂控制4.27
import socket
import time


def check_coordinates(x, y, z, rx, ry, rz):
    """
    检查坐标是否在机械臂运动范围内
    这里的范围是示例，需要根据实际机械臂手册修改
    """
    x_min, x_max = -500, 500
    y_min, y_max = -500, 500
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


def enable_robot():
    # 连接Dashboard端口
    dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dashboard_socket.connect(('192.168.101.13', 29999))

    # 使能机器人指令
    enable_cmd = "EnableRobot()\n"
    dashboard_socket.send(enable_cmd.encode('utf - 8'))
    response = dashboard_socket.recv(1024).decode('utf - 8')
    print(f"使能机器人响应: {response}")

    # 关闭Dashboard端口连接
    dashboard_socket.close()


def move_robot(x, y, z, rx, ry, rz):
    # 连接运动指令端口
    movement_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    movement_socket.connect(('192.168.101.13', 30003))

    # 发送Sync指令确保队列清空
    sync_cmd = "Sync()\n"
    movement_socket.send(sync_cmd.encode('utf - 8'))
    time.sleep(0.1)  # 等待指令执行

    # 检查坐标范围
    if not check_coordinates(x, y, z, rx, ry, rz):
        print("目标坐标超出机械臂运动范围，无法发送运动指令")
        movement_socket.close()
        return

    # 获取机械臂状态
    status_cmd = "RobotMode()\n"
    movement_socket.send(status_cmd.encode('utf - 8'))
    status_response = movement_socket.recv(1024).decode('utf - 8')
    if status_response.startswith("0,"):
        status = status_response.split(",")[1].strip("{}")
        if status == "9":  # 9表示有未清除的报警
            print("机械臂存在报警，无法运动，请先处理报警")
        else:
            # 发送直线运动指令，设置速度为50%，加速度为50%
            move_cmd = f"MovL({x},{y},{z},{rx},{ry},{rz},SpeedL = 50,AccL = 50)\n"
            movement_socket.send(move_cmd.encode('utf - 8'))
            print(f"已发送运动指令到坐标: ({x}, {y}, {z}, {rx}, {ry}, {rz})")
    else:
        print(f"获取机械臂状态失败: {status_response}")

    # 关闭运动指令端口连接
    movement_socket.close()


if __name__ == "__main__":
    enable_robot()
    # 示例目标坐标，根据实际情况修改
    x = 200
    y = -50
    z = 450
    rx = 143
    ry = 0
    rz = -80
    move_robot(x, y, z, rx, ry, rz)
