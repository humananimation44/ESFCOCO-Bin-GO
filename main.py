# Welcome to our camera
import cv2
import mediapipe as mp
import time
# For the entrance screen don't tamper with the code it can break stuff mitt and hector.
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if frame_width == 0 or frame_height == 0:
    frame_width = 640
    frame_height = 480

points = 0
last_hand_state = "NONE"
reward_ready = False
success_message_until = 0

BIN_WIDTH = 420
BIN_HEIGHT = 420
SUCCESS_MESSAGE_SECONDS = 1.5
HAND_BOX_PADDING = 15

def show_intro_screen():
    splash_width = 1250
    splash_height = 720

    splash = np.zeros((splash_height, splash_width, 3), dtype=np.uint8)
    splash[:] = (30, 25, 20)

    cv2.rectangle(splash, (80, 80), (1200, 640), (50, 120, 80), 4)
    cv2.rectangle(splash, (110, 110), (1170, 610), (20, 40, 30), -1)

    cv2.putText(
        splash,
        "Welcome to Bin-GO! By Neel, Hector and Mitt.",
        (250, 260),
        cv2.FONT_HERSHEY_DUPLEX,
        2.0,
        (255, 255, 255),
        3,
        cv2.LINE_AA
    )

    cv2.putText(
        splash,
        "A demo to our recycling start-up, and how we plan to execute it.",
        (245, 340),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (180, 255, 200),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        splash,
        "Bring your hand into the screen, not too close.",
        (275, 410),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (220, 220, 220),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        splash,
        "The camera is now booting up",
        (460, 520),
        cv2.FONT_HERSHEY_DUPLEX,
        1.0,
        (0, 255, 180),
        2,
        cv2.LINE_AA
    )

    cv2.imshow("BIN-GO!/Bingo?", splash)
    cv2.waitKey(4000)

def count_extended_fingers(hand_landmarks, handedness_label):
    fingers_up = 0

    finger_tip_ids = [8, 12, 16, 20]
    finger_pip_ids = [6, 10, 14, 18]

    for tip_id, pip_id in zip(finger_tip_ids, finger_pip_ids):
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[pip_id]
        if tip.y < pip.y:
            fingers_up += 1

    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]

    if handedness_label == "Right":
        if thumb_tip.x < thumb_ip.x:
            fingers_up += 1
    else:
        if thumb_tip.x > thumb_ip.x:
            fingers_up += 1

    return fingers_up

def get_hand_state(hand_landmarks, handedness_label):
    fingers_up = count_extended_fingers(hand_landmarks, handedness_label)

    if fingers_up <= 1:
        return "FIST"
    elif fingers_up >= 4:
        return "OPEN"
    else:
        return "PARTIAL"

def get_hand_bounding_box(hand_landmarks, frame_width, frame_height, padding=0):
    x_coords = [int(lm.x * frame_width) for lm in hand_landmarks.landmark]
    y_coords = [int(lm.y * frame_height) for lm in hand_landmarks.landmark]

    x_min = max(min(x_coords) - padding, 0)
    y_min = max(min(y_coords) - padding, 0)
    x_max = min(max(x_coords) + padding, frame_width)
    y_max = min(max(y_coords) + padding, frame_height)

    return x_min, y_min, x_max, y_max

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    while True:
        success, frame = cap.read()
        if not success:
            print("ERROR: Failed to read webcam frame.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        h, w, _ = frame.shape
        now = time.time()

        bin_x1 = w - BIN_WIDTH - 40
        bin_y1 = h - BIN_HEIGHT - 40
        bin_x2 = w - 40
        bin_y2 = h - 40

        bin_color = (0, 220, 120)
        status_text = "Show your hand to start"
        status_color = (255, 255, 255)

        if now < success_message_until:
            status_text = "Nice! +10"
            status_color = (0, 255, 0)
            bin_color = (0, 255, 0)

        cv2.rectangle(frame, (bin_x1, bin_y1), (bin_x2, bin_y2), bin_color, 4)
        cv2.putText(
            frame,
            "DROP HERE",
            (bin_x1 + 20, bin_y1 + 45),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            bin_color,
            2,
            cv2.LINE_AA
        )

        current_hand_state = "NONE"

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness_label = "Unknown"

            if results.multi_handedness:
                handedness_label = results.multi_handedness[0].classification[0].label

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            current_hand_state = get_hand_state(hand_landmarks, handedness_label)

            hand_x1, hand_y1, hand_x2, hand_y2 = get_hand_bounding_box(
                hand_landmarks, w, h, HAND_BOX_PADDING
            )

            hand_fits_in_bin = (
                hand_x1 >= bin_x1 and
                hand_y1 >= bin_y1 and
                hand_x2 <= bin_x2 and
                hand_y2 <= bin_y2
            )

            hand_box_color = (255, 80, 80)
            if hand_fits_in_bin:
                hand_box_color = (0, 255, 0)

            cv2.rectangle(frame, (hand_x1, hand_y1), (hand_x2, hand_y2), hand_box_color, 2)

            if current_hand_state == "FIST":
                reward_ready = True
                if now >= success_message_until:
                    status_text = "Nice, now move to the bin"

            elif reward_ready and last_hand_state == "FIST" and current_hand_state == "OPEN" and hand_fits_in_bin:
                points += 10
                reward_ready = False
                success_message_until = time.time() + SUCCESS_MESSAGE_SECONDS
                status_text = "Nice! +10"
                status_color = (0, 255, 0)

            elif reward_ready and current_hand_state == "OPEN" and not hand_fits_in_bin:
                if now >= success_message_until:
                    status_text = "Move a bit more into the bin"

            elif reward_ready:
                if now >= success_message_until:
                    status_text = "Open your hand to drop it"

            else:
                if now >= success_message_until:
                    status_text = "Make a fist to grab the item"

            last_hand_state = current_hand_state

        else:
            last_hand_state = "NONE"
            if now >= success_message_until:
                status_text = "Show your hand to start"

        cv2.putText(
            frame,
            status_text,
            (20, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            status_color,
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            f"Score: {points}",
            (20, 85),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            (255, 255, 0),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "Press R to reset | Q to quit",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA
        )

        cv2.imshow("Bin-Go", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("r"):
            points = 0
            reward_ready = False
            last_hand_state = "NONE"
            success_message_until = 0

cap.release()
cv2.destroyAllWindows()
