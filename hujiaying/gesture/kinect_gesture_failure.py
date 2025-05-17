# 第一版测试手势+kinect，自己写的，但是检测的算法有问题，检测遇到困难
##############################################################################
# import cv2
# import mediapipe as mp
# import numpy as np
# import pykinect_azure as pykinect
# from collections import deque
#
# # 初始化Kinect
# pykinect.initialize_libraries()
# device_config = pykinect.default_configuration
# device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1440P
# device = pykinect.start_device(config=device_config)
#
# # 初始化MediaPipe
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(
#     static_image_mode=False,
#     max_num_hands=2,
#     min_detection_confidence=0.6,
#     min_tracking_confidence=0.6
# )
# mp_drawing = mp.solutions.drawing_utils
# gesture_buffer = deque(maxlen=5)  # 手势缓冲队列
#
# def is_open_palm(landmarks, handedness):
#     """判断五指张开且手心正对屏幕"""
#     # 所有手指伸直
#     fingers_straight = all([
#         landmarks[8].y < landmarks[6].y,  # 食指
#         landmarks[12].y < landmarks[10].y,  # 中指
#         landmarks[16].y < landmarks[14].y,  # 无名指
#         landmarks[20].y < landmarks[18].y,  # 小指
#         landmarks[4].y < landmarks[3].y  # 拇指
#     ])
#
#     # 手掌方向判断（通过关键点0/5/17的平面关系）
#     wrist = landmarks[0]
#     index_mcp = landmarks[5]
#     pinky_mcp = landmarks[17]
#
#     # 计算手掌平面法向量
#     vec1 = np.array([index_mcp.x - wrist.x, index_mcp.y - wrist.y])
#     vec2 = np.array([pinky_mcp.x - wrist.x, pinky_mcp.y - wrist.y])
#     cross_product = np.cross(vec1, vec2)
#
#     # 如果法向量接近垂直（手心正对摄像头）
#     return fingers_straight and abs(cross_product) < 0.01
#
#
# def is_thumbs_up(landmarks):
#     """判断点赞手势（拇指向上，其他四指弯曲）"""
#     thumb_straight = landmarks[4].y < landmarks[3].y - 0.05
#     fingers_bent = all([
#         landmarks[8].y > landmarks[6].y,
#         landmarks[12].y > landmarks[10].y,
#         landmarks[16].y > landmarks[14].y,
#         landmarks[20].y > landmarks[18].y
#     ])
#     return thumb_straight and fingers_bent
#
# def process_gestures(image):
#     """核心手势识别逻辑"""
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)  # Kinect默认输出为BGRA
#     results = hands.process(image_rgb)
#
#     current_gestures = []
#     if results.multi_hand_landmarks:
#         for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
#             landmarks = hand_landmarks.landmark
#             hand_type = results.multi_handedness[idx].classification[0].label
#
#             # 手势判断
#             if is_open_palm(landmarks, hand_type):
#                 current_gestures.append(f"{hand_type} Palm")
#             elif is_thumbs_up(landmarks):
#                 current_gestures.append(f"{hand_type} Thumb")
#
#
#             # 绘制关键点
#             mp_drawing.draw_landmarks(
#                 image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
#                 mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
#                 mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
#             )
#
#     return image, current_gestures
#
#
# def display_controls(image, final_gesture):
#     """控制指令显示"""
#     text_config = {
#         "Right Palm": ("RIGHT DOOR", (20, 100)),
#         "Left Palm": ("LEFT DOOR", (20, 150)),
#         "Right Thumb": ("HOOD", (20, 200)),
#         "Left Thumb": ("RELEASE MODE", (20, 250))
#     }
#
#     for gesture in text_config:
#         if gesture in final_gesture:
#             text, pos = text_config[gesture]
#             cv2.putText(image, text, pos,
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
#
#
# if __name__ == "__main__":
#     cv2.namedWindow('Kinect Gesture Control', cv2.WINDOW_NORMAL)
#
#     while True:
#         # 获取Kinect帧
#         capture = device.update()
#         if not capture:
#             continue
#
#         # 获取彩色图像
#         ret, color_image = capture.get_color_image()
#         if not ret:
#             continue
#
#         # 处理手势识别
#         processed_img, current_gestures = process_gestures(color_image.copy())
#
#         # 更新手势缓冲
#         gesture_buffer.append(current_gestures)
#         all_gestures = [g for gestures in gesture_buffer for g in gestures]
#
#         # 显示控制指令
#         if all_gestures:
#             final_gesture = max(set(all_gestures), key=all_gestures.count)
#             display_controls(processed_img, final_gesture)
#
#         # 显示画面
#         cv2.imshow('Kinect Gesture Control', processed_img)
#
#         # 退出控制
#         if cv2.waitKey(1) in [27, ord('q')]:  # ESC或Q退出
#             break
#
#     device.stop()
#     cv2.destroyAllWindows()
##############################################################################################
import cv2
import mediapipe as mp
import numpy as np
import pykinect_azure as pykinect
from collections import deque

# 初始化Kinect
pykinect.initialize_libraries()
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1440P
device = pykinect.start_device(config=device_config)

# 初始化MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_drawing = mp.solutions.drawing_utils
gesture_buffer = deque(maxlen=5)  # 手势缓冲队列


def is_open_palm(landmarks, hand_type):
    """判断五指张开且手心正对屏幕（用于车门控制）"""
    # 所有手指伸直
    fingers_straight = all([
        landmarks[8].y < landmarks[6].y,  # 食指
        landmarks[12].y < landmarks[10].y,  # 中指
        landmarks[16].y < landmarks[14].y,  # 无名指
        landmarks[20].y < landmarks[18].y,  # 小指
        landmarks[4].y < landmarks[3].y  # 拇指
    ])

    # 手掌方向判断
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]
    vec1 = np.array([index_mcp.x - wrist.x, index_mcp.y - wrist.y])
    vec2 = np.array([pinky_mcp.x - wrist.x, pinky_mcp.y - wrist.y])
    return fingers_straight and abs(np.cross(vec1, vec2)) < 0.01


def is_victory(landmarks):
    """判断✌️手势（用于车顶/释放控制）"""
    # 食指和中指伸直
    index_straight = landmarks[8].y < landmarks[6].y - 0.03
    middle_straight = landmarks[12].y < landmarks[10].y - 0.03

    # 其他手指弯曲
    thumb_bent = landmarks[4].y > landmarks[3].y + 0.02
    ring_bent = landmarks[16].y > landmarks[14].y + 0.02
    pinky_bent = landmarks[20].y > landmarks[18].y + 0.02

    return index_straight and middle_straight and thumb_bent and ring_bent and pinky_bent


def process_gestures(image):
    """核心手势识别逻辑"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    results = hands.process(image_rgb)

    current_gestures = []
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            landmarks = hand_landmarks.landmark
            hand_type = results.multi_handedness[idx].classification[0].label

            # 同时检测两种手势类型
            if is_open_palm(landmarks, hand_type):
                current_gestures.append(f"{hand_type} Palm")
            if is_victory(landmarks):
                current_gestures.append(f"{hand_type} Victory")

            # 绘制关键点
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
            )

    return image, current_gestures


def display_controls(image, active_gestures):
    """动态显示所有激活的控制指令"""
    y_position = 100
    text_config = {
        "Right Palm": "RIGHT DOOR",
        "Left Palm": "LEFT DOOR",
        "Right Victory": "ROOF ",
        "Left Victory": "RELEASE"
    }

    # 按优先级排序显示
    for gesture in ["Right Palm", "Left Palm", "Right Victory", "Left Victory"]:
        if gesture in active_gestures:
            cv2.putText(image, text_config[gesture], (20, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            y_position += 50


if __name__ == "__main__":
    cv2.namedWindow('Kinect Gesture Control', cv2.WINDOW_NORMAL)

    while True:
        # 获取Kinect帧
        capture = device.update()
        if not capture:
            continue

        # 获取彩色图像
        ret, color_image = capture.get_color_image()
        if not ret:
            continue

        # 处理手势识别
        processed_img, current_gestures = process_gestures(color_image.copy())

        # 更新手势缓冲并获取稳定结果
        gesture_buffer.append(current_gestures)
        all_gestures = [g for gestures in gesture_buffer for g in gestures]
        active_gestures = list(set([g for g in all_gestures if all_gestures.count(g) >= 3]))

        # 显示控制指令
        display_controls(processed_img, active_gestures)

        # 显示画面
        cv2.imshow('Kinect Gesture Control', processed_img)

        # 退出控制
        if cv2.waitKey(1) in [27, ord('q')]:
            break

    device.stop()
    cv2.destroyAllWindows()