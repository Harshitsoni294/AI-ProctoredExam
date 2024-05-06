import cv2
import time
import os
import io
import numpy as np
import PySimpleGUI as sg
from eye_movement import process_eye_movement
from head_pose import process_head_pose
from mobile_detection import process_mobile_detection

# Configuration
LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

# Sample questions (replace with real test content)
QUESTIONS = [
    {"q": "What is 2 + 2?", "opts": ["1", "2", "3", "4"], "a": 4},
    {"q": "What is the capital of France?", "opts": ["Berlin", "London", "Paris", "Rome"], "a": 3},
    {"q": "Which color is a banana?", "opts": ["Red", "Blue", "Yellow", "Green"], "a": 3},
    {"q": "Which is a mammal?", "opts": ["Shark", "Dolphin", "Octopus", "Tuna"], "a": 2},
    {"q": "Sun rises from?", "opts": ["West", "East", "North", "South"], "a": 2},
    {"q": "Which is prime?", "opts": ["4", "6", "7", "8"], "a": 3},
    {"q": "5 * 6 = ?", "opts": ["11", "30", "24", "20"], "a": 2},
    {"q": "Largest planet?", "opts": ["Earth", "Mars", "Jupiter", "Venus"], "a": 3},
    {"q": "Water freezes at?", "opts": ["0 C", "100 C", "50 C", "-10 C"], "a": 1},
    {"q": "Which is a programming language?", "opts": ["HTML", "CSS", "Python", "Photoshop"], "a": 3},
]

CALIBRATION_SECONDS = 5.0
PER_QUESTION_SECONDS = 30

def to_bytes(frame, resize=None):
    if resize:
        frame = cv2.resize(frame, resize)
    _, buf = cv2.imencode('.png', frame)
    return buf.tobytes()

def save_violation(frame, reason):
    filename = os.path.join(LOG_DIR, f"violation_{reason}_{int(time.time())}.png")
    cv2.imwrite(filename, frame)
    print(f"Violation saved: {filename}")

def eye_check(cap, window, name):
    seen = set()
    # keep trying until all seen (no failure message)
    while True:
        event, values = window.read(timeout=20)
        if event == sg.WIN_CLOSED or event == 'Exit':
            return False

        ret, frame = cap.read()
        if not ret:
            continue

        frame, gaze = process_eye_movement(frame)

        if gaze == "Looking Left":
            seen.add('Left')
        elif gaze == "Looking Right":
            seen.add('Right')
        elif gaze == "Looking Center":
            seen.add('Center')

        img = to_bytes(frame, resize=(640,360))
        window['-IMAGE-'].update(data=img)
        window['-INSTR-'].update(f"Hello {name} — Eye check: Look LEFT → RIGHT → CENTER")
        window['-SEEN-'].update(', '.join(sorted(seen)) if seen else 'None')

        if {'Left','Right','Center'}.issubset(seen):
            return True

def head_check(cap, window, name):
    # Calibrate
    calib = []
    start = time.time()
    while time.time() - start < CALIBRATION_SECONDS:
        event, values = window.read(timeout=20)
        if event == sg.WIN_CLOSED or event == 'Exit':
            return False
        ret, frame = cap.read()
        if not ret:
            continue
        _, angles = process_head_pose(frame, None)
        if angles:
            calib.append(angles)
        img = to_bytes(frame, resize=(640,360))
        window['-IMAGE-'].update(data=img)
        window['-INSTR-'].update(f"Hello {name} — Calibrating head neutral position...")

    if not calib:
        # fallback: still continue and attempt checks
        calibrated = None
    else:
        calibrated = tuple(map(float, np.mean(calib, axis=0)))

    seen = set()
    while True:
        event, values = window.read(timeout=20)
        if event == sg.WIN_CLOSED or event == 'Exit':
            return False
        ret, frame = cap.read()
        if not ret:
            continue
        frame, head_dir = process_head_pose(frame, calibrated)
        if head_dir == 'Looking Up':
            seen.add('Up')
        elif head_dir == 'Looking Down':
            seen.add('Down')
        elif head_dir == 'Looking Left':
            seen.add('Left')
        elif head_dir == 'Looking Right':
            seen.add('Right')

        img = to_bytes(frame, resize=(640,360))
        window['-IMAGE-'].update(data=img)
        window['-INSTR-'].update(f"Hello {name} — Head check: Move HEAD Up / Down / Left / Right")
        window['-SEEN-'].update(', '.join(sorted(seen)) if seen else 'None')

        if {'Up','Down','Left','Right'}.issubset(seen):
            return True

def run_mcq_gui(cap, name, email):
    sg.theme('DarkBlue3')
    layout = [[sg.Text(f"Test: {name} ({email})", font=('Any', 18), justification='center', expand_x=True)] ,
              [sg.Text('', key='-Q-', font=('Any', 20), size=(60,2))],
              [sg.Button('1', key='1', size=(20,2)), sg.Button('2', key='2', size=(20,2))],
              [sg.Button('3', key='3', size=(20,2)), sg.Button('4', key='4', size=(20,2))],
              [sg.Text('Time left: ', key='-TIME-', font=('Any', 14))]]
    window = sg.Window('MCQ Test', layout, finalize=True, no_titlebar=False, resizable=True, element_justification='center', keep_on_top=True)
    window.maximize()

    answers = []
    for idx, q in enumerate(QUESTIONS):
        selected = None
        q_start = time.time()
        window['-Q-'].update(f"Q{idx+1}. {q['q']}\n\n" + '\n'.join([f"{i+1}. {o}" for i,o in enumerate(q['opts'])]))
        while True:
            remaining = int(PER_QUESTION_SECONDS - (time.time() - q_start))
            if remaining < 0:
                break
            event, values = window.read(timeout=200)
            if event == sg.WIN_CLOSED:
                window.close()
                return answers, False
            if event in ['1','2','3','4']:
                selected = int(event)
                # provide brief visual confirmation
                window['-TIME-'].update(f"Selected: {selected} — Time left: {remaining}s")
            else:
                window['-TIME-'].update(f"Time left: {remaining}s")
        answers.append(selected)

    window.close()
    return answers, True

def main():
    sg.theme('DarkAmber')
    # Start camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        sg.popup_error('Cannot open camera')
        return

    # --- Welcome / Identity form ---
    form_layout = [
        [sg.Text('AI Proctored Test', font=('Any', 26), justification='center', expand_x=True)],
        [sg.Text('Name', size=(8,1)), sg.Input(key='-NAME-')],
        [sg.Text('Email', size=(8,1)), sg.Input(key='-EMAIL-')],
        [sg.Button('Start Checks', size=(12,1)), sg.Button('Exit', size=(8,1))]
    ]

    form_win = sg.Window('Register', form_layout, finalize=True)
    while True:
        event, values = form_win.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            form_win.close()
            cap.release()
            return
        if event == 'Start Checks':
            name = values['-NAME-'].strip() or 'Candidate'
            email = values['-EMAIL-'].strip() or 'unknown@example.com'
            form_win.close()
            break

    # --- Live check window ---
    layout = [[sg.Text('', key='-INSTR-', font=('Any', 18), size=(60,2))],
              [sg.Image(filename='', key='-IMAGE-')],
              [sg.Text('Seen:', font=('Any', 12)), sg.Text('', key='-SEEN-', font=('Any', 12))],
              [sg.Button('Skip', key='Exit'), sg.Button('Next', key='Next', visible=False)]]

    win = sg.Window('Checks', layout, finalize=True, element_justification='center', resizable=True)

    # Run eye check (keeps trying until passed)
    res = eye_check(cap, win, name)
    if not res:
        win.close()
        cap.release()
        return

    # brief confirmation
    win['-INSTR-'].update('Eye check complete — preparing head check...')
    win.refresh()
    time.sleep(1.0)

    res = head_check(cap, win, name)
    if not res:
        win.close()
        cap.release()
        return

    win['-INSTR-'].update('All checks passed — ready for test')
    win['-SEEN-'].update('')
    win.refresh()
    time.sleep(1.0)
    win.close()

    # Start MCQ inside GUI
    answers, completed = run_mcq_gui(cap, name, email)
    if completed:
        sg.popup('Test finished', f'Answers: {answers}')
    else:
        sg.popup('Test ended due to a violation or window closed')

    cap.release()

if __name__ == '__main__':
    main()
import cv2
import time
import os
from eye_movement import process_eye_movement
from head_pose import process_head_pose
from mobile_detection import process_mobile_detection

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a log directory for screenshots
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Calibration for head pose
calibrated_angles = None
start_time = time.time()

# Timers for each functionality
head_misalignment_start_time = None
eye_misalignment_start_time = None
mobile_detection_start_time = None

# Previous states
previous_head_state = "Looking at Screen"
previous_eye_state = "Looking at Screen"
previous_mobile_state = False

# Initialize head_direction with a default value
head_direction = "Looking at Screen"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Process eye movement
    frame, gaze_direction = process_eye_movement(frame)
    cv2.putText(frame, f"Gaze Direction: {gaze_direction}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Process head pose
    if time.time() - start_time <= 5:  # Calibration time
        cv2.putText(frame, "Calibrating... Keep your head straight", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if calibrated_angles is None:
            _, calibrated_angles = process_head_pose(frame, None)
    else:
        frame, head_direction = process_head_pose(frame, calibrated_angles)
        cv2.putText(frame, f"Head Direction: {head_direction}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Process mobile detection
    frame, mobile_detected = process_mobile_detection(frame)
    cv2.putText(frame, f"Mobile Detected: {mobile_detected}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Check for head misalignment
    if head_direction != "Looking at Screen":
        if head_misalignment_start_time is None:
            head_misalignment_start_time = time.time()
        elif time.time() - head_misalignment_start_time >= 3:
            filename = os.path.join(log_dir, f"head_{head_direction}_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
            head_misalignment_start_time = None  # Reset timer
    else:
        head_misalignment_start_time = None  # Reset timer

    # Check for eye misalignment
    if gaze_direction != "Looking at Screen":
        if eye_misalignment_start_time is None:
            eye_misalignment_start_time = time.time()
        elif time.time() - eye_misalignment_start_time >= 3:
            filename = os.path.join(log_dir, f"eye_{gaze_direction}_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
            eye_misalignment_start_time = None  # Reset timer
    else:
        eye_misalignment_start_time = None  # Reset timer

    # Check for mobile detection
    if mobile_detected:
        if mobile_detection_start_time is None:
            mobile_detection_start_time = time.time()
        elif time.time() - mobile_detection_start_time >= 3:
            filename = os.path.join(log_dir, f"mobile_detected_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
            mobile_detection_start_time = None  # Reset timer
    else:
        mobile_detection_start_time = None  # Reset timer

    # Display the combined output
    cv2.imshow("Combined Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()