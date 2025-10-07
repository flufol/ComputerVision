import subprocess
from facenet_pytorch import MTCNN
import cv2

hidden_apps = []


def get_visible_apps():
    script = '''
    tell application "System Events"
        set visibleApps to name of every process whose visible is true and name is not "Finder"
    end tell
    return visibleApps
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    apps = result.stdout.strip().split(", ")
    return [app.strip() for app in apps if app.strip()]


def hide_all_mac_windows():
    global hidden_apps
    visible_windows = get_visible_apps()
    apps = '{' + ', '.join(f'"{app}"' for app in visible_windows) + '}'

    script = f'''
            set appList to {apps}
            activate application "Finder"
            repeat with appName in appList
                try
                    tell application "System Events"
                        set visible of process appName to false
                    end tell
                end try
            end repeat
        '''

    subprocess.run(["osascript", "-e", script])
    hidden_apps = visible_windows


def show_all_mac_windows():
    global hidden_apps
    apps = '{' + ', '.join(f'"{app}"' for app in hidden_apps) + '}'

    script = f'''
                set appList to {apps}
                activate application "Finder"

                repeat with appName in appList
                    try
                        tell application "System Events"
                            set visible of process appName to true
                        end tell
                    end try
                end repeat
            '''

    subprocess.run(["osascript", "-e", script])
    hidden_apps = []


def detect_faces(frame):
    boxes, probabilities = mtcnn.detect(frame)
    if boxes is not None and probabilities is not None:
        return boxes, probabilities
    return None, None



if __name__ == '__main__':
    cam = cv2.VideoCapture(0)

    mtcnn = MTCNN()
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes, probabilities = detect_faces(frame)

        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if not hidden_apps:
                hide_all_mac_windows()
        elif hidden_apps:
            show_all_mac_windows()

        cv2.imshow("Face Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
