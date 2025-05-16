import cv2
import mediapipe as mp
import time
import numpy as np
import pickle
import asyncio
from websocket_server import send_command  # async WebSocket sender

# ------------------ Configuration ------------------
CAM_INDEX      = 0
FRAME_WIDTH    = 1280
FRAME_HEIGHT   = 720
PIP_SIZE       = (320, 240)
COOLDOWN_TIME  = 1.0  # seconds between same-gesture commands

# ------------------ Gesture Definitions ------------------
try:
    with open('custom_gestures.pkl', 'rb') as f:
        CUSTOM_GESTURES = pickle.load(f)
except FileNotFoundError:
    CUSTOM_GESTURES = {}

GESTURES = {
    'play':       [True,  True,  True,  True,  True],
    'pause':      [False, False, False, False, False],
    'vol_up':     [False, True,  True,  False, False],
    'vol_down':   [False, False, False, True,  True ],
    'next_video': [False, False, False, False, True ],
    'prev_video': [False, True,  True,  True,  False],
}

last_action_time = {
    **{g: 0 for g in GESTURES},
    **{g: 0 for g in CUSTOM_GESTURES}
}

# ------------------ MediaPipe Setup ------------------
mp_hands         = mp.solutions.hands
mp_drawing       = mp.solutions.drawing_utils
mp_drawing_styles= mp.solutions.drawing_styles
hands            = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ------------------ Helpers ------------------
def get_finger_states(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    states = []
    for i, tip_idx in enumerate(tips):
        pip_idx = tip_idx - 2
        tip = hand_landmarks.landmark[tip_idx]
        pip = hand_landmarks.landmark[pip_idx]
        if i == 0:
            states.append(tip.x < pip.x)
        else:
            states.append(tip.y < pip.y)
    return states

def extract_landmarks(hand_landmarks):
    return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()

# ------------------ Main Loop ------------------
cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

recording = False
recorded_landmarks = []
new_gesture_name = ""

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    pip_frame = None
    gesture_name = None

    if results.multi_hand_landmarks:
        hld = results.multi_hand_landmarks[0]
        pip_frame = frame.copy()
        mp_drawing.draw_landmarks(
            pip_frame, hld, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )

        states = get_finger_states(hld)
        for name, pattern in GESTURES.items():
            if states == pattern:
                gesture_name = name
                break

        # custom gestures
        vec = extract_landmarks(hld)
        for name, ref in CUSTOM_GESTURES.items():
            if np.linalg.norm(vec - ref) < 0.1:
                gesture_name = name
                break

        now = time.time()
        if gesture_name and now - last_action_time[gesture_name] > COOLDOWN_TIME:
            asyncio.run(send_command(gesture_name))
            last_action_time[gesture_name] = now
            cv2.putText(frame, f"Action: {gesture_name}",
                        (10, FRAME_HEIGHT-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        if recording:
            recorded_landmarks.append(vec)
            cv2.putText(frame, f"Recording: {new_gesture_name}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # PiP overlay
    if pip_frame is not None:
        small = cv2.resize(pip_frame, PIP_SIZE)
        frame[0:PIP_SIZE[1], 0:PIP_SIZE[0]] = small

    cv2.imshow("YouTube Gesture Controller", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        new_gesture_name = input("Enter gesture name: ")
        recording = True
        recorded_landmarks = []
    elif key == ord('s') and recording:
        if recorded_landmarks:
            avg = np.mean(recorded_landmarks, axis=0)
            CUSTOM_GESTURES[new_gesture_name] = avg
            last_action_time[new_gesture_name] = 0
            with open('custom_gestures.pkl', 'wb') as f:
                pickle.dump(CUSTOM_GESTURES, f)
            print(f"Saved new gesture: {new_gesture_name}")
        recording = False

cap.release()
cv2.destroyAllWindows()
