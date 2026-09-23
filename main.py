import cv2
import mediapipe as mp
import time

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

fps = 20.0

points = 0
last_hand_state = "NONE"
reward_ready = False
success_message_until = 0

BIN_WIDTH = 420
BIN_HEIGHT = 420
SUCCESS_MESSAGE_SECONDS = 1.5
HAND_BOX_PADDING = 20

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

        if now < success_message_until:
            status_text = "Trash disposed! +10"
            status_color = (0, 255, 0)
            bin_color = (0, 255, 0)
        else:
            status_text = "Show hand"
            status_color = (0, 200, 255)
            bin_color = (0, 255, 0)

        cv2.rectangle(frame, (bin_x1, bin_y1), (bin_x2, bin_y2), bin_color, 3)
        cv2.putText(
            frame,
            "BIN ZONE",
            (bin_x1, bin_y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            bin_color,
            2,
            cv2.LINE_AA
        )

        current_hand_state = "NONE"
        handedness_label = "Unknown"

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            if results.multi_handedness:
                handedness_label = results.multi_handedness[0].classification[0].label

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            wrist = hand_landmarks.landmark[0]
            index_tip = hand_landmarks.landmark[8]

            wrist_x = int(wrist.x * w)
            wrist_y = int(wrist.y * h)
            index_x = int(index_tip.x * w)
            index_y = int(index_tip.y * h)

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

            hand_box_color = (255, 0, 0)
            if hand_fits_in_bin:
                hand_box_color = (0, 255, 0)

            cv2.rectangle(frame, (hand_x1, hand_y1), (hand_x2, hand_y2), hand_box_color, 2)
            cv2.circle(frame, (index_x, index_y), 10, (0, 0, 255), -1)

            if current_hand_state == "FIST":
                reward_ready = True
                if now >= success_message_until:
                    status_text = "Holding trash"

            elif reward_ready and last_hand_state == "FIST" and current_hand_state == "OPEN" and hand_fits_in_bin:
                points += 10
                reward_ready = False
                success_message_until = time.time() + SUCCESS_MESSAGE_SECONDS
                status_text = "Trash disposed! +10"
                status_color = (0, 255, 0)

            elif reward_ready and current_hand_state == "OPEN" and not hand_fits_in_bin:
                if now >= success_message_until:
                    status_text = "Fit whole hand inside bin"

            elif reward_ready:
                if now >= success_message_until:
                    status_text = "Move hand into bin and open"

            else:
                if now >= success_message_until:
                    status_text = "Make a fist first"

            cv2.putText(
                frame,
                f"Wrist: ({wrist_x}, {wrist_y})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                f"Index Tip: ({index_x}, {index_y})",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                f"Handedness: {handedness_label}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 200, 0),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                f"Hand State: {current_hand_state}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                f"Hand In Bin: {hand_fits_in_bin}",
                (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                hand_box_color,
                2,
                cv2.LINE_AA
            )

            last_hand_state = current_hand_state

        else:
            last_hand_state = "NONE"
            if now >= success_message_until:
                status_text = "No hand detected"

        cv2.putText(
            frame,
            f"Status: {status_text}",
            (10, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            status_color,
            2,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            f"Points: {points}",
            (10, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            f"Reward ready: {reward_ready}",
            (10, 265),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 255, 200),
            2,
            cv2.LINE_AA
        )

        cv2.imshow("Bin-go Hand Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
