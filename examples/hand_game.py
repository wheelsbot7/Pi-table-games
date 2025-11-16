#!/usr/bin/env python3
"""
Hand Tracking Game Example
Run this file to play the hand tracking game.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hand_tracker.game import HandTrackingGame

if __name__ == "__main__":
    game = HandTrackingGame()
    game.run()
