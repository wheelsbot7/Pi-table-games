from typing import Any, Dict, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    """A class for hand tracking using MediaPipe and OpenCV."""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        """
        Initialize the hand tracker.

        Args:
            static_image_mode: Whether to treat the input images as a batch of static
                and possibly unrelated images, or a video stream.
            max_num_hands: Maximum number of hands to detect.
            model_complexity: Complexity of the hand landmark model (0, 1, or 2).
            min_detection_confidence: Minimum confidence value for hand detection.
            min_tracking_confidence: Minimum confidence value for hand tracking.
        """

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        # Landmark connections for custom drawing
        self.landmark_connections = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),  # Thumb
            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),  # Index finger
            (5, 9),
            (9, 10),
            (10, 11),
            (11, 12),  # Middle finger
            (9, 13),
            (13, 14),
            (14, 15),
            (15, 16),  # Ring finger
            (13, 17),
            (17, 18),
            (18, 19),
            (19, 20),
            (0, 17),  # Pinky and palm
        ]

    def process_frame(self, image: np.ndarray) -> np.ndarray:
        """
        Process a frame and draw hand landmarks.

        Args:
            image: Input image in BGR format.

        Returns:
            Image with hand landmarks drawn.
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Process the image
        results = self.hands.process(image_rgb)

        # Convert back to BGR
        image_rgb.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                # Get hand label (Left/Right)
                hand_label = handedness.classification[0].label

                # Draw landmarks and connections
                self._draw_custom_landmarks(image_bgr, hand_landmarks, hand_label)

                # Draw bounding box
                self._draw_bounding_box(image_bgr, hand_landmarks, hand_label)

        return image_bgr

    def _draw_custom_landmarks(
        self,
        image: np.ndarray,
        landmarks: mp.solutions.hands.HandLandmark,
        hand_label: str,
    ):
        """Draw custom hand landmarks and connections."""
        h, w, _ = image.shape

        # Draw connections
        for connection in self.landmark_connections:
            start_idx, end_idx = connection
            start_point = landmarks.landmark[start_idx]
            end_point = landmarks.landmark[end_idx]

            start_x, start_y = int(start_point.x * w), int(start_point.y * h)
            end_x, end_y = int(end_point.x * w), int(end_point.y * h)

            cv2.line(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

        # Draw landmarks
        for idx, landmark in enumerate(landmarks.landmark):
            x, y = int(landmark.x * w), int(landmark.y * h)

            # Use different colors for different parts of the hand
            if idx == 0:  # Wrist
                color = (255, 0, 0)  # Blue
                radius = 6
            elif idx in [1, 5, 9, 13, 17]:  # Base of fingers
                color = (0, 255, 255)  # Yellow
                radius = 5
            elif idx in [4, 8, 12, 16, 20]:  # Tips of fingers
                color = (0, 0, 255)  # Red
                radius = 5
            else:  # Other joints
                color = (255, 255, 255)  # White
                radius = 4

            cv2.circle(image, (x, y), radius, color, -1)

    def _draw_bounding_box(
        self,
        image: np.ndarray,
        landmarks: mp.solutions.hands.HandLandmark,
        hand_label: str,
    ):
        """Draw bounding box around the hand."""
        h, w, _ = image.shape

        # Get all landmark coordinates
        x_coords = [int(landmark.x * w) for landmark in landmarks.landmark]
        y_coords = [int(landmark.y * h) for landmark in landmarks.landmark]

        # Calculate bounding box
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        # Add padding
        padding = 15
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)

        # Draw bounding box
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 0, 255), 2)

    def get_hand_data(self, image: np.ndarray) -> Optional[List[Dict[str, Any]]]:
        """
        Get comprehensive hand data including landmarks and bounding boxes.

        Args:
            image: Input image in BGR format.

        Returns:
            List of hand data dictionaries, or None if no hands detected.
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Process the image
        results = self.hands.process(image_rgb)

        if not results.multi_hand_landmarks:
            return None

        h, w, _ = image.shape
        hands_data = []

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):
            # Get landmarks
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.append((landmark.x * w, landmark.y * h, landmark.z))

            # Calculate bounding box
            x_coords = [landmark[0] for landmark in landmarks]
            y_coords = [landmark[1] for landmark in landmarks]

            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            # Add padding
            padding = 15
            x_min = max(0, x_min - padding)
            x_max = min(w, x_max + padding)
            y_min = max(0, y_min - padding)
            y_max = min(h, y_max + padding)

            hand_data = {
                "landmarks": landmarks,
                "bounding_box": (x_min, y_min, x_max - x_min, y_max - y_min),
                "center": ((x_min + x_max) // 2, (y_min + y_max) // 2),
                "handedness": handedness.classification[0].label,
                "palm_center": (
                    landmarks[0][0],
                    landmarks[0][1],
                ),  # Use wrist as palm center
            }

            hands_data.append(hand_data)

        return hands_data

    def close(self):
        """Release resources."""
        self.hands.close()


def main():
    """Main function to run hand tracking from webcam."""
    tracker = HandTracker()

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Hand Tracking started!")
    print("Press 'q' to quit")
    print("Press 's' to save current frame")

    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Process frame
            processed_frame = tracker.process_frame(frame)

            # Add FPS counter
            frame_count += 1
            if frame_count % 30 == 0:
                fps = cap.get(cv2.CAP_PROP_FPS)
                cv2.putText(
                    processed_frame,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

            # Display the frame
            cv2.imshow("Hand Tracking", processed_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s"):
                # Save current frame
                filename = f"hand_tracking_frame_{frame_count}.jpg"
                cv2.imwrite(filename, processed_frame)
                print(f"Frame saved as {filename}")

    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        tracker.close()
        print("Hand Tracking stopped.")


if __name__ == "__main__":
    main()
