# Eye Tracking Mouse Control

This project uses computer vision and gaze tracking to control the mouse pointer using eye movements. By leveraging facial landmarks detected via **MediaPipe**, the system maps the user's gaze direction to screen coordinates for intuitive mouse control.

## Features

- **Gaze-Based Mouse Movement**: Move the mouse pointer by looking at different parts of the screen.
- **Blink Detection for Clicks**: Detect blinks to simulate mouse clicks.
- **Dynamic Calibration**: Adjusts to the user's gaze for accurate mapping.
- **Real-Time Feedback**: Visualize iris positions and gaze direction on the webcam feed.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [How It Works](#how-it-works)
5. [Calibration](#calibration)
6. [Eye Landmarks](#eye-landmarks)
7. [Contributing](#contributing)
8. [License](#license)

---

## Requirements

To run this project, you need the following:

- Python 3.8 or higher
- A webcam (preferably positioned above the screen for optimal results)
- The following Python libraries:
  - `opencv-python`
  - `mediapipe`
  - `pyautogui`
  - `numpy`

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/wasif-exe/eye-tracking-mouse.git
   cd eye-tracking-mouse
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python eye_tracking_mouse.py
   ```

---

## Usage

1. Run the script and follow the on-screen instructions for calibration.
2. After calibration, move your eyes to control the mouse pointer.
3. Blink to simulate a mouse click.

---

## How It Works

The system uses **MediaPipe's Face Mesh** to detect facial landmarks, including the eyes and iris positions. The gaze direction is calculated based on the relative position of the iris within the eye bounding box. The system then maps this gaze direction to the screen coordinates for mouse movement.

### Key Components:

- **Iris Position**: The position of the iris is used to determine the gaze direction.
- **Blink Detection**: The Eye Aspect Ratio (EAR) is calculated to detect blinks, which trigger mouse clicks.
- **Dynamic Sensitivity**: The sensitivity adjusts dynamically based on the distance between the eyes.

---

## Calibration

During calibration, the system collects gaze data while the user looks at predefined points on the screen. These points are defined as follows:

```python
calibration_points = {
    "Top Left": (0.1, 0.1), "Top Center": (0.5, 0.1), "Top Right": (0.9, 0.1),
    "Middle Left": (0.1, 0.5), "Center": (0.5, 0.5), "Middle Right": (0.9, 0.5),
    "Bottom Left": (0.1, 0.9), "Bottom Center": (0.5, 0.9), "Bottom Right": (0.9, 0.9)
}
```

The calibration ensures that the system accurately maps the user's gaze to screen coordinates.

---

## Eye Landmarks

The system uses specific facial landmarks to track the eyes and iris positions. The indices for these landmarks are defined as follows:

```python
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
```

These landmarks are part of MediaPipe's face mesh model, which provides precise tracking of facial features.

### Coordinate System

The gaze direction is mapped to a normalized coordinate system:

- **Top-left corner**: `[0, 0]`
- **Top-right corner**: `[1, 0]`
- **Bottom-left corner**: `[0, 1]`
- **Bottom-right corner**: `[1, 1]`

For example, an iris position of `(x=0.6, y=0.4)` corresponds to the center-right area of the screen.

---

## Contributing

Contributions are welcome! If you'd like to improve this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
