import random
import sys
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pygame

from .tracker import HandTracker


class HandTrackingGame:
    """A game where players use hand tracking to catch targets."""

    def __init__(self, width: int = 1920, height: int = 1080):
        """Initialize the game."""
        self.width = width
        self.height = height
        self.camera_width = 640
        self.camera_height = 480
        self.frame_count = 0

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Hand Tracking Game - Catch the Targets!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize hand tracker
        self.tracker = HandTracker(
            max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7
        )

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)

        # if not self.cap.isOpened():
        #     print("Error: Could not open camera")
        #     sys.exit(1)

        # Game state
        self.score = 0
        self.targets: List[dict] = []
        self.game_time = 10  # seconds
        self.start_time = pygame.time.get_ticks()
        self.game_active = True
        self.spawn_timer = 0
        self.target_radius = 30

        # Colors
        self.colors = {
            "background": (25, 25, 50),
            "text": (255, 255, 255),
            "target": (255, 100, 100),
            "target_captured": (100, 255, 100),
            "hand": (100, 200, 255),
            "ui_bg": (0, 0, 0, 128),
        }

    def spawn_target(self):
        """Spawn a new target at a random position."""
        target = {
            "x": random.randint(
                self.target_radius + 100, self.width - self.target_radius - 100
            ),
            "y": random.randint(
                self.target_radius + 100, self.height - self.target_radius - 100
            ),
            "radius": self.target_radius,
            "captured": False,
            "capture_time": 0,
            "color": self.colors["target"],
        }
        self.targets.append(target)

    def update_targets(self, hand_pos: Optional[Tuple[int, int]]):
        """Update target states and check for captures."""
        current_time = pygame.time.get_ticks()

        for target in self.targets[:]:
            if hand_pos and not target["captured"]:
                # Check if hand is over target
                distance = (
                    (hand_pos[0] - target["x"]) ** 2 + (hand_pos[1] - target["y"]) ** 2
                ) ** 0.5

                if distance < target["radius"]:
                    target["captured"] = True
                    target["capture_time"] = current_time
                    target["color"] = self.colors["target_captured"]
                    self.score += 10

            # Remove captured targets after a short delay
            if target["captured"] and current_time - target["capture_time"] > 500:
                self.targets.remove(target)

    def draw_ui(self):
        """Draw the game UI."""
        # Calculate remaining time
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        remaining_time = max(0, self.game_time - elapsed_time)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.colors["text"])
        self.screen.blit(score_text, (10, 10))

        # Draw timer
        time_text = self.font.render(
            f"Time: {remaining_time}s", True, self.colors["text"]
        )
        self.screen.blit(time_text, (self.width - 150, 10))

        # Draw instructions
        instructions = [
            "Cover the red circles with your hand to capture them!",
            "Move your hand in front of the camera to play.",
            f"Target radius: {self.target_radius}px",
        ]

        for i, instruction in enumerate(instructions):
            instr_text = self.small_font.render(instruction, True, self.colors["text"])
            self.screen.blit(instr_text, (10, self.height - 80 + i * 25))

    def draw_camera_feed(self, camera_surface: pygame.Surface):
        """Draw the camera feed in the corner."""
        # Scale camera feed to fit in corner
        scaled_camera = pygame.transform.scale(camera_surface, (200, 150))
        self.screen.blit(scaled_camera, (self.width - 210, self.height - 160))

        # Draw border around camera feed
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (self.width - 212, self.height - 162, 204, 154),
            2,
        )

    def convert_camera_to_screen(
        self, camera_x: float, camera_y: float
    ) -> Tuple[int, int]:
        """Convert camera coordinates to screen coordinates."""
        # Flip x-axis and scale to screen size
        screen_x = int((1 - camera_x / self.camera_width) * self.width)
        screen_y = int((camera_y / self.camera_height) * self.height)

        # Clamp to screen boundaries
        screen_x = max(0, min(self.width, screen_x))
        screen_y = max(0, min(self.height, screen_y))

        return screen_x, screen_y

    def run(self, mouse_enabled):
        """Run the main game loop."""
        print("Starting Hand Tracking Game!")
        print("Cover the red circles with your hand to score points!")
        print("Press 'ESC' to quit, 'R' to restart")

        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cleanup()
                        return
                    elif event.key == pygame.K_r:
                        self.restart_game()

            if not mouse_enabled:
                # Read camera frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read camera frame")
                    break
                # Process frame with hand tracker
                hand_data = self.tracker.get_hand_data(frame)

                # Add tracking overlay
                processed_frame = self.tracker.process_frame(frame)

                # Convert camera frame to Pygame surface
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                frame_rgb = np.rot90(frame_rgb)  # Rotate to correct orientation
                camera_surface = pygame.surfarray.make_surface(frame_rgb)

                # Get hand position for game logic
                hand_pos = None
                if hand_data:
                    # Use the first detected hand's palm center
                    palm_x, palm_y = hand_data[0]["palm_center"]
                    hand_pos = self.convert_camera_to_screen(palm_x, palm_y)
            else:
                camera_surface = pygame.Surface([640, 480], pygame.SRCALPHA, 32)
                camera_surface = camera_surface.convert_alpha()
                hand_pos = pygame.mouse.get_pos()

            # Update game state
            current_time = pygame.time.get_ticks()

            # Spawn new targets periodically
            if self.game_active:
                self.spawn_timer += self.clock.get_time()
                if (
                    self.spawn_timer >= 2000 and len(self.targets) < 5
                ):  # Spawn every 2 seconds, max 5 targets
                    self.spawn_target()
                    self.spawn_timer = 0
                self.frame_count += 1

            # Update targets
            self.update_targets(hand_pos)

            # Check game over condition, set final score if game is over
            elapsed_time = (current_time - self.start_time) // 1000
            if elapsed_time >= self.game_time and self.game_active:
                self.game_active = False
                self.final_score = self.score

            # Draw everything
            self.screen.fill(self.colors["background"])

            # Draw targets
            for target in self.targets:
                pygame.draw.circle(
                    self.screen,
                    target["color"],
                    (target["x"], target["y"]),
                    target["radius"],
                )
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (target["x"], target["y"]),
                    target["radius"],
                    2,
                )

            # Draw hand position if available
            if hand_pos:
                pygame.draw.circle(self.screen, self.colors["hand"], hand_pos, 20)
                pygame.draw.circle(self.screen, (255, 255, 255), hand_pos, 20, 2)

                # Draw hand trail effect
                for i in range(1, 5):
                    radius = 20 - i * 3
                    if radius > 0:
                        alpha = 100 - i * 20
                        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(
                            s,
                            (*self.colors["hand"][:3], alpha),
                            (radius, radius),
                            radius,
                        )
                        self.screen.blit(
                            s, (hand_pos[0] - radius, hand_pos[1] - radius)
                        )

            # Draw UI
            self.draw_ui()
            if not mouse_enabled:
                self.draw_camera_feed(camera_surface)

            # Draw game over screen
            if not self.game_active:
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0, 0))

                game_over_text = self.font.render("GAME OVER!", True, (255, 255, 255))
                final_score_text = self.font.render(
                    f"Final Score: {self.final_score}", True, (255, 255, 255)
                )
                restart_text = self.small_font.render(
                    "Press 'R' to restart", True, (255, 255, 255)
                )

                self.screen.blit(
                    game_over_text,
                    (
                        self.width // 2 - game_over_text.get_width() // 2,
                        self.height // 2 - 50,
                    ),
                )
                self.screen.blit(
                    final_score_text,
                    (
                        self.width // 2 - final_score_text.get_width() // 2,
                        self.height // 2,
                    ),
                )
                self.screen.blit(
                    restart_text,
                    (
                        self.width // 2 - restart_text.get_width() // 2,
                        self.height // 2 + 50,
                    ),
                )

            pygame.display.flip()
            self.clock.tick(60)

    def restart_game(self):
        """Restart the game with initial state."""
        self.score = 0
        self.targets.clear()
        self.start_time = pygame.time.get_ticks()
        self.game_active = True
        self.spawn_timer = 0
        self.frame_count = 0

    def cleanup(self):
        """Clean up resources."""
        self.tracker.close()
        self.cap.release()
        print(self.frame_count)
        pygame.quit()
        print("Game closed.")


def main():
    """Main function to run the hand tracking game."""
    mouse_enabled = False
    game = HandTrackingGame()
    game.run(mouse_enabled)


def main_mouse():
    mouse_enabled = True
    game = HandTrackingGame()
    game.run(mouse_enabled)


if __name__ == "__main__":
    main()

if __name__ == "__main_mouse__":
    main()
