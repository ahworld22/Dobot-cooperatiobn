# MediaPipe Hands测试版，电脑自带摄像头
import cv2
import mediapipe as mp
import math

# 初始化MediaPipe手部模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)  # 最多检测2只手
mp_drawing = mp.solutions.drawing_utils

def is_thumb_up(landmarks, handedness):
    """判断是否为点赞手势（拇指伸直，其他四指弯曲）"""
    # 关键点索引
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]   # 拇指指根关节
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    # 拇指伸直条件（y坐标更小表示向上）
    thumb_straight = thumb_tip.y < thumb_ip.y - 0.05  # 调整阈值避免误判

    # 其他四指弯曲条件（指尖y坐标大于中间关节）
    fingers_bent = all([
        index_tip.y > landmarks[6].y,
        middle_tip.y > landmarks[10].y,
        ring_tip.y > landmarks[14].y,
        pinky_tip.y > landmarks[18].y
    ])

    return thumb_straight and fingers_bent

def is_scissors(landmarks):
    """判断是否为剪刀手（食指、中指伸直，其余弯曲）"""
    # 食指和中指伸直
    index_straight = landmarks[8].y < landmarks[6].y
    middle_straight = landmarks[12].y < landmarks[10].y
    # 其他手指弯曲
    thumb_bent = landmarks[4].y > landmarks[3].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y

    return index_straight and middle_straight and thumb_bent and ring_bent and pinky_bent

# 打开摄像头
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # 转换为RGB格式并处理
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    gesture = "No Gesture"  # 默认无手势

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            landmarks = hand_landmarks.landmark
            hand_type = handedness.classification[0].label  # Left 或 Right

            # 判断手势
            if is_thumb_up(landmarks, hand_type):
                if hand_type == "Right":
                    gesture = "Right Door "
                else:
                    gesture = "Left Door "
            elif is_scissors(landmarks):
                gesture = "Hood Open "

            # 绘制关键点
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 显示手势结果
    cv2.putText(image, gesture, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Vehicle Control by Gesture', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()