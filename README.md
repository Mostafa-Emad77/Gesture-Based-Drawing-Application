# Gesture-Based Drawing Application

An interactive drawing application that allows you to create artwork using hand gestures. The application uses computer vision to track your hand movements and translate them into drawing actions.

## Platforms

- **Desktop**: Windows, macOS, Linux
- **Mobile**: Android (8.0+), iOS (14.0+)

## Features

### Core Features
- Real-time hand tracking using MediaPipe
- Gesture-based drawing controls
- Dynamic brush size adjustment using pinky finger
- Advanced color selection with HSV color wheel
- Optimized 30 FPS performance
- Save drawings as PNG/JPG files
- Cross-platform support (Desktop and Mobile)

### Drawing Controls
- Draw with index finger
- Adjust brush size with pinky finger movement
- Change colors using gestures or GUI
- Clear canvas with open palm
- Multiple drawing modes (Advanced version)

### Color Management
- Predefined color palette
- HSV color wheel selection
- Custom color picker
- Real-time color preview
- Save custom colors to palette

### Advanced Version Features
- Multiple drawing modes:
  - Freestyle drawing
  - Line tool
  - Rectangle tool
  - Circle tool
  - Pattern brush
  - Eraser tool
- Shape preview while drawing
- Mode switching with thumb gesture
- Enhanced UI with mode indicators

## Requirements

### Desktop
```
python >= 3.8
opencv-python >= 4.8.0
mediapipe >= 0.10.0
numpy >= 1.24.0
Pillow >= 10.0.0
```

### Android
```gradle
// Minimum SDK: 26 (Android 8.0)
implementation 'com.google.mediapipe:mediapipe:0.10.0'
implementation 'org.opencv:opencv-android:4.8.0'
implementation 'androidx.camera:camera-core:1.3.0'
```

### iOS
```ruby
# Minimum iOS: 14.0
pod 'MediaPipeTasksVision'
pod 'OpenCV'
```

## Installation

### Desktop
1. Clone the repository:
```bash
git clone https://github.com/Mostafa-Emad77/gesture-drawing-app.git
cd gesture-drawing-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Mobile
See [MOBILE_IMPLEMENTATION.md](MOBILE_IMPLEMENTATION.md) for detailed mobile setup instructions.

## Usage

### Desktop
1. Launch the application chooser:
```bash
python app_launcher.py
```

2. Select your preferred version:
- Standard Version: For basic drawing features
- Advanced Version: For additional tools and modes

### Mobile
2. Grant camera permissions
3. Follow on-screen tutorial for gesture controls

## Key Gestures

- **Index finger up**: Draw
- **Index + middle fingers up**: Stop drawing
- **Closed fist**: Cycle through colors
- **"OK" gesture**: Enter color selection mode
- **Pinky finger up**: Adjust brush size
- **Open palm**: Clear canvas
- **Thumb up**: Change mode (Advanced version)

## Performance

- Target frame rate: 30 FPS
- Adaptive frame timing
- Real-time performance monitoring
- Optimized hand tracking
- Smooth gesture recognition
- Mobile-optimized processing

## Customization

You can customize various aspects of the application:

### Drawing Parameters
- Brush size range (1-30 by default)
- Color palette presets
- Canvas dimensions
- Frame rate target

### Hand Tracking
- Detection confidence threshold
- Tracking confidence threshold
- Maximum number of hands

### UI Elements
- Window size
- Control panel layout
- Color swatches
- Gesture indicators
- Mobile-responsive design

## Mobile-Specific Features

### Android
- Hardware-accelerated rendering
- Camera2 API support
- Kotlin coroutines for async operations
- Android gesture navigation support

### iOS
- Metal rendering support
- Core Image processing
- Dynamic Island compatibility
- Haptic feedback

For detailed mobile implementation instructions, see [MOBILE_IMPLEMENTATION.md](MOBILE_IMPLEMENTATION.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- MediaPipe for hand tracking
- OpenCV for image processing
- Tkinter/UIKit/Android UI toolkit
- NumPy for numerical operations 
