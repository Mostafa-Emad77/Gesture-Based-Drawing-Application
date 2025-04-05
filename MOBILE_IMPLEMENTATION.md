# Mobile Implementation Guide

## Android Implementation

### Requirements
```gradle
// build.gradle
dependencies {
    implementation 'com.google.mediapipe:mediapipe:0.10.0'
    implementation 'org.opencv:opencv-android:4.8.0'
    implementation 'androidx.camera:camera-core:1.3.0'
    implementation 'androidx.camera:camera-camera2:1.3.0'
    implementation 'androidx.camera:camera-lifecycle:1.3.0'
}
```

### Project Structure
```
app/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/gesturedrawing/
│   │   │       ├── MainActivity.kt
│   │   │       ├── DrawingView.kt
│   │   │       ├── HandTrackingProcessor.kt
│   │   │       └── GestureRecognizer.kt
│   │   └── res/
│   │       ├── layout/
│   │       │   ├── activity_main.xml
│   │       │   └── drawing_controls.xml
│   │       └── values/
│   │           └── colors.xml
└── build.gradle
```

### Key Components

1. **MainActivity.kt**
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var cameraProvider: ProcessCameraProvider
    private lateinit var drawingView: DrawingView
    private lateinit var handTracker: HandTrackingProcessor
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize camera and MediaPipe
        setupCamera()
        // Initialize drawing view
        setupDrawingView()
        // Setup gesture recognition
        setupGestureRecognition()
    }
}
```

2. **DrawingView.kt**
```kotlin
class DrawingView(context: Context) : View(context) {
    private val paint = Paint()
    private val path = Path()
    
    // Drawing implementation
    // Gesture handling
    // Color and brush size management
}
```

## iOS Implementation

### Requirements
```ruby
# Podfile
pod 'MediaPipeTasksVision'
pod 'OpenCV'
```

### Project Structure
```
GestureDrawing/
├── Sources/
│   ├── AppDelegate.swift
│   ├── ViewControllers/
│   │   └── MainViewController.swift
│   ├── Views/
│   │   ├── DrawingView.swift
│   │   └── ControlsView.swift
│   └── Handlers/
│       ├── HandTrackingHandler.swift
│       └── GestureRecognizer.swift
└── Resources/
    └── Assets.xcassets
```

### Key Components

1. **MainViewController.swift**
```swift
class MainViewController: UIViewController {
    private var cameraSession: AVCaptureSession?
    private var drawingView: DrawingView!
    private var handTracker: HandTrackingHandler!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
        setupDrawingView()
        setupGestureRecognition()
    }
}
```

2. **DrawingView.swift**
```swift
class DrawingView: UIView {
    private var path = UIBezierPath()
    private var strokeColor = UIColor.black
    private var strokeWidth: CGFloat = 5.0
    
    // Drawing implementation
    // Gesture handling
    // Color and brush size management
}
```

## Common Implementation Details

### Gesture Recognition
- Use MediaPipe Hand Landmarker for both platforms
- Implement platform-specific camera handling
- Maintain 30 FPS target with mobile optimization

### Drawing Features
1. **Basic Controls**
   - Index finger for drawing
   - Pinky movement for brush size
   - Fist for color cycling
   - Palm for canvas clear

2. **UI Adaptations**
   - Touch-friendly color picker
   - Gesture indicator overlay
   - FPS counter
   - Mobile-optimized controls

### Performance Optimization
1. **Camera**
   - Reduced resolution for processing
   - Hardware acceleration
   - Frame dropping when necessary

2. **Drawing**
   - Path optimization
   - Layer-based rendering
   - Memory management

3. **Hand Tracking**
   - Reduced landmark count
   - Optimized detection intervals
   - ROI-based tracking

## Platform-Specific Considerations

### Android
1. **Performance**
   - Use Kotlin coroutines for async operations
   - Hardware-accelerated canvas
   - OpenGL ES for complex rendering

2. **Compatibility**
   - Support Android 8.0+ (API 26)
   - Handle different screen sizes
   - Camera2 API implementation

### iOS
1. **Performance**
   - Use Metal for rendering
   - Core Image for processing
   - GCD for concurrent operations

2. **Compatibility**
   - Support iOS 14.0+
   - Handle notch/dynamic island
   - Privacy permissions

## Building and Testing

### Android
```bash
# Build
./gradlew assembleDebug

# Run tests
./gradlew test
```

### iOS
```bash
# Build
xcodebuild -scheme GestureDrawing -configuration Debug

# Run tests
xcodebuild test -scheme GestureDrawing
```

## Distribution

### Android
1. Generate signed APK
2. Publish to Google Play Store
3. Handle app signing and versioning

### iOS
1. Archive application
2. Submit to App Store
3. Handle certificates and provisioning

## Troubleshooting

### Common Issues
1. **Camera Access**
   - Request permissions at runtime
   - Handle denial cases
   - Provide clear usage descriptions

2. **Performance**
   - Monitor CPU/GPU usage
   - Implement frame dropping
   - Optimize drawing operations

3. **Memory**
   - Implement proper cleanup
   - Handle low memory warnings
   - Cache management

## Resources

- [MediaPipe Mobile Documentation](https://developers.google.com/mediapipe)
- [Android Camera2 API Guide](https://developer.android.com/training/camera2)
- [iOS AVFoundation Guide](https://developer.apple.com/av-foundation/)
- [OpenCV Mobile Guide](https://docs.opencv.org/4.x/) 