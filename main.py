"""
Drowsy Driver Detection System
Real-time eye drowsiness detection using webcam + Eye Aspect Ratio (EAR)
"""

import cv2
import time
import argparse
from ear_utils import calculate_ear, get_eye_landmarks
from alert import trigger_alert, stop_alert

# ─── Configuration ────────────────────────────────────────────────────────────
EAR_THRESHOLD   = 0.25   # Below this = eye is closed
CONSEC_FRAMES   = 20     # Frames eyes must stay closed to trigger alert
ALERT_COOLDOWN  = 3.0    # Seconds before alert can re-trigger


def run_detection(camera_index: int = 0, show_landmarks: bool = True):
    """Main detection loop."""
    import mediapipe as mp

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam. Check camera_index.")
        return

    print("[INFO] Drowsy Driver Detection started. Press 'q' to quit.")

    closed_frame_count = 0
    alert_active       = False
    last_alert_time    = 0.0
    fps_time           = time.time()
    frame_count        = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        frame_count += 1
        h, w = frame.shape[:2]
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        status_color = (0, 255, 0)   # Green = awake
        status_text  = "AWAKE"
        ear_display  = 0.0

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_eye, right_eye = get_eye_landmarks(landmarks, w, h)
            left_ear   = calculate_ear(left_eye)
            right_ear  = calculate_ear(right_eye)
            ear_display = (left_ear + right_ear) / 2.0

            if show_landmarks:
                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 2, (0, 200, 255), -1)

            if ear_display < EAR_THRESHOLD:
                closed_frame_count += 1
            else:
                closed_frame_count = 0
                if alert_active:
                    stop_alert()
                    alert_active = False

            # ── Drowsiness detected ──
            if closed_frame_count >= CONSEC_FRAMES:
                status_text  = "DROWSY!"
                status_color = (0, 0, 255)

                now = time.time()
                if not alert_active and (now - last_alert_time) > ALERT_COOLDOWN:
                    trigger_alert()
                    alert_active    = True
                    last_alert_time = now
        else:
            status_text  = "NO FACE"
            status_color = (0, 165, 255)

        # ── HUD overlay ──
        fps = frame_count / max(time.time() - fps_time, 1e-9)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (320, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        cv2.putText(frame, f"Status : {status_text}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(frame, f"EAR    : {ear_display:.3f}  (threshold {EAR_THRESHOLD})",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(frame, f"FPS    : {fps:.1f}",
                    (10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        # Closed-eye progress bar
        bar_max = w - 20
        bar_fill = int(bar_max * min(closed_frame_count / CONSEC_FRAMES, 1.0))
        cv2.rectangle(frame, (10, h - 25), (bar_max, h - 10), (50, 50, 50), -1)
        bar_color = (0, 255, 0) if closed_frame_count < CONSEC_FRAMES * 0.6 else \
                    (0, 165, 255) if closed_frame_count < CONSEC_FRAMES else (0, 0, 255)
        cv2.rectangle(frame, (10, h - 25), (10 + bar_fill, h - 10), bar_color, -1)
        cv2.putText(frame, "Drowsiness meter", (10, h - 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)

        cv2.imshow("Drowsy Driver Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    stop_alert()
    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()
    print("[INFO] Detection stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drowsy Driver Detection")
    parser.add_argument("--camera",    type=int,  default=0,    help="Camera index (default 0)")
    parser.add_argument("--no-landmarks", action="store_true",  help="Hide eye landmark dots")
    args = parser.parse_args()

    run_detection(camera_index=args.camera, show_landmarks=not args.no_landmarks)