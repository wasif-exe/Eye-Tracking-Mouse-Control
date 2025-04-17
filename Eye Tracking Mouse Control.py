import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

RIGHT_EYE = {
    "left": 33,
    "right": 133,
    "top": 159,
    "bottom": 145,
    "iris": 468
}
LEFT_EYE = {
    "left": 362,
    "right": 263,
    "top": 386,
    "bottom": 374,
    "iris": 473
}

center_gaze = [0.5, 0.5]
calibrated = False
last_move_time = time.time()
last_click_time = time.time()
move_interval = 0.5
click_interval = 1.0
pyautogui.FAILSAFE = False

EAR_THRESHOLD = 0.2
EAR_CONSEC_FRAMES = 3
blink_counter = 0

def get_point(index, landmarks, w, h):
    return np.array([int(landmarks[index].x * w), int(landmarks[index].y * h)])

def get_eccentricity(iris, left, right, top, bottom):
    eye_width = np.linalg.norm(right - left)
    eye_height = np.linalg.norm(bottom - top)
    x_rel = np.dot(iris - left, (right - left)) / (eye_width ** 2)
    y_rel = np.dot(iris - top, (bottom - top)) / (eye_height ** 2)
    return np.clip(x_rel, 0, 1), np.clip(y_rel, 0, 1)

def calculate_eye_aspect_ratio(eye, landmarks, w, h):
    left = get_point(eye["left"], landmarks, w, h)
    right = get_point(eye["right"], landmarks, w, h)
    top = get_point(eye["top"], landmarks, w, h)
    bottom = get_point(eye["bottom"], landmarks, w, h)
    horizontal_distance = np.linalg.norm(left - right)
    vertical_distance_1 = np.linalg.norm(top - left)
    vertical_distance_2 = np.linalg.norm(bottom - right)
    ear = (vertical_distance_1 + vertical_distance_2) / (2.0 * horizontal_distance)
    return ear

def process_eye(eye, lm, w, h):
    left = get_point(eye["left"], lm, w, h)
    right = get_point(eye["right"], lm, w, h)
    top = get_point(eye["top"], lm, w, h)
    bottom = get_point(eye["bottom"], lm, w, h)
    try:
        iris = get_point(eye["iris"], lm, w, h)
        gaze_x, gaze_y = get_eccentricity(iris, left, right, top, bottom)
    except Exception:
        gaze_x, gaze_y = 0.5, 0.5
        iris = (left + right) // 2
    return gaze_x, gaze_y, iris

def determine_direction(gx, gy, center_x, center_y):
    dx = gx - center_x
    dy = gy - center_y
    dy = -dy
    threshold = 0.05
    if dx < -threshold and dy < -threshold:
        return "Top Left"
    elif dx > threshold and dy < -threshold:
        return "Top Right"
    elif dx < -threshold and dy > threshold:
        return "Bottom Left"
    elif dx > threshold and dy > threshold:
        return "Bottom Right"
    elif dx < -threshold:
        return "Left"
    elif dx > threshold:
        return "Right"
    elif dy < -threshold:
        return "Up"
    elif dy > threshold:
        return "Down"
    else:
        return "Center"

def move_mouse(direction):
    x, y = pyautogui.position()
    offset = 100
    if direction == "Up":
        pyautogui.moveTo(x, y - offset)
    elif direction == "Down":
        pyautogui.moveTo(x, y + offset)
    elif direction == "Left":
        pyautogui.moveTo(x - offset, y)
    elif direction == "Right":
        pyautogui.moveTo(x + offset, y)
    elif direction == "Top Left":
        pyautogui.moveTo(x - offset, y - offset)
    elif direction == "Top Right":
        pyautogui.moveTo(x + offset, y - offset)
    elif direction == "Bottom Left":
        pyautogui.moveTo(x - offset, y + offset)
    elif direction == "Bottom Right":
        pyautogui.moveTo(x + offset, y + offset)
    elif direction == "Center":
        pyautogui.moveTo(screen_w // 2, screen_h // 2)

def click_mouse():
    print("Mouse Clicked!")
    pyautogui.click()

print("Please look at the center of the screen for calibration...")
time.sleep(2)
samples = []
while len(samples) < 30:
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        gx_r, gy_r, _ = process_eye(RIGHT_EYE, landmarks, w, h)
        gx_l, gy_l, _ = process_eye(LEFT_EYE, landmarks, w, h)
        samples.append([(gx_r + gx_l) / 2, (gy_r + gy_l) / 2])

    cv2.putText(frame, "Calibrating... Keep looking at the center", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow("Calibration", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if samples:
    center_gaze = np.mean(samples, axis=0)
    print(f"Calibration complete. Center gaze: {center_gaze}")
cv2.destroyWindow("Calibration")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        gx_r, gy_r, iris_r = process_eye(RIGHT_EYE, landmarks, w, h)
        gx_l, gy_l, iris_l = process_eye(LEFT_EYE, landmarks, w, h)

        gaze_x = (gx_r + gx_l) / 2
        gaze_y = (gy_r + gy_l) / 2

        direction = determine_direction(gaze_x, gaze_y, center_gaze[0], center_gaze[1])

        ear_r = calculate_eye_aspect_ratio(RIGHT_EYE, landmarks, w, h)
        ear_l = calculate_eye_aspect_ratio(LEFT_EYE, landmarks, w, h)
        ear = (ear_r + ear_l) / 2

        if ear < EAR_THRESHOLD:
            blink_counter += 1
            if blink_counter >= EAR_CONSEC_FRAMES:
                print("Blink detected! Clicking...")
                click_mouse()
                blink_counter = 0
        else:
            blink_counter = 0

        if direction != "Center" and time.time() - last_move_time > move_interval:
            move_mouse(direction)
            last_move_time = time.time()

        cv2.circle(frame, tuple(iris_r), 3, (0, 255, 0), -1)
        cv2.circle(frame, tuple(iris_l), 3, (0, 255, 0), -1)
        cv2.putText(frame, f'Gaze: ({gaze_x:.2f}, {gaze_y:.2f})', (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        cv2.putText(frame, f'Direction: {direction}', (10, 100),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    cv2.imshow("Eye Direction Mouse Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
