import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from PIL import Image, ImageTk
import os
import random
from datetime import datetime
import colorsys
import time

class AdvancedGestureDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Gesture Drawing App")
        self.root.geometry("1280x720")
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize drawing parameters
        self.prev_point = None
        self.drawing_color = (0, 0, 255)  # Red (BGR format)
        self.brush_thickness = 5
        self.is_drawing = False
        self.clear_gesture_active = False
        self.color_change_active = False
        self.brush_size_active = False
        self.initial_pinky_y = None  # For pinky-based brush size control
        self.shape_start_point = None
        self.mode_change_active = False
        
        # For color wheel selection
        self.color_select_active = False
        self.color_select_start_pos = None
        self.hue = 0  # Initial hue (red)
        
        # Predefined colors palette
        self.color_palette = [
            (0, 0, 255),    # Red
            (0, 127, 255),  # Orange
            (0, 255, 255),  # Yellow
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (255, 0, 127),  # Purple
            (255, 255, 255),# White
            (0, 0, 0)       # Black
        ]
        self.current_color_index = 0
        
        # Drawing modes
        self.MODES = {
            'FREESTYLE': 0,
            'LINE': 1,
            'RECTANGLE': 2,
            'CIRCLE': 3,
            'ERASER': 4,
            'PATTERN': 5
        }
        self.current_mode = self.MODES['FREESTYLE']
        self.mode_names = {v: k for k, v in self.MODES.items()}
        
        # For shape drawing
        self.temp_canvas = None
        
        # Initialize canvas
        self.canvas_width = 640
        self.canvas_height = 480
        self.canvas = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        
        # FPS tracking
        self.last_frame_time = time.time()
        self.fps = 0
        self.frame_times = []
        self.target_fps = 30
        self.frame_interval = 1.0 / self.target_fps
        
        # Create UI
        self.setup_ui()
        
        # Start video capture
        self.cap = cv2.VideoCapture(0)
        self.update_frame()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video frame and canvas
        self.video_frame = ttk.Label(main_frame)
        self.video_frame.pack(side=tk.LEFT, padx=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Mode selection
        ttk.Label(control_frame, text="Drawing Mode:", font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        self.mode_var = tk.StringVar(value="FREESTYLE")
        for mode_name in self.MODES.keys():
            ttk.Radiobutton(
                control_frame, 
                text=mode_name.capitalize(), 
                value=mode_name, 
                variable=self.mode_var,
                command=self.change_mode
            ).pack(anchor=tk.W)
        
        ttk.Separator(control_frame).pack(fill=tk.X, pady=10)
        
        # Color picker button
        ttk.Label(control_frame, text="Controls:", font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        color_btn = ttk.Button(control_frame, text="Choose Color", command=self.choose_color)
        color_btn.pack(pady=5, fill=tk.X)
        
        # Brush size slider
        ttk.Label(control_frame, text="Brush Size:").pack(pady=5, anchor=tk.W)
        self.brush_size_slider = ttk.Scale(control_frame, from_=1, to=30, orient=tk.HORIZONTAL, value=self.brush_thickness)
        self.brush_size_slider.pack(fill=tk.X, pady=5)
        self.brush_size_slider.bind("<ButtonRelease-1>", self.update_brush_size)
        
        # Clear canvas button
        clear_btn = ttk.Button(control_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_btn.pack(pady=5, fill=tk.X)
        
        # Save drawing button
        save_btn = ttk.Button(control_frame, text="Save Drawing", command=self.save_drawing)
        save_btn.pack(pady=5, fill=tk.X)
        
        # Current color indicator
        ttk.Label(control_frame, text="Current Color:").pack(pady=5, anchor=tk.W)
        self.color_indicator = tk.Canvas(control_frame, width=50, height=30)
        self.color_indicator.pack(pady=5, anchor=tk.W)
        self.update_color_indicator()
        
        # Color palette 
        ttk.Label(control_frame, text="Color Palette:").pack(pady=5, anchor=tk.W)
        palette_frame = ttk.Frame(control_frame)
        palette_frame.pack(pady=5)
        
        # Create the color swatches
        self.color_swatches = []
        for i, color in enumerate(self.color_palette):
            # Convert BGR to RGB for tkinter
            rgb_color = f'#{color[2]:02x}{color[1]:02x}{color[0]:02x}'
            swatch = tk.Canvas(palette_frame, width=20, height=20, bg=rgb_color, highlightthickness=1)
            swatch.grid(row=i//4, column=i%4, padx=2, pady=2)
            swatch.bind("<Button-1>", lambda event, idx=i: self.select_palette_color(idx))
            self.color_swatches.append(swatch)
        
        # Highlight current color
        self.update_palette_highlight()
        
        # Gesture instructions
        ttk.Separator(control_frame).pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Gesture Instructions:", font=("Arial", 12, "bold")).pack(pady=5, anchor=tk.W)
        
        instructions = """
        • Index finger up: Draw
        • Index + middle fingers up: Stop drawing
        • Closed fist: Cycle through colors
        • "OK" gesture: Enter color selection mode
          (move finger left/right to change hue)
        • Pinky finger up: Adjust brush size
          (move pinky up/down)
        • Open palm: Clear canvas
        • Thumb up: Change drawing mode
        """
        ttk.Label(control_frame, text=instructions).pack(pady=5, anchor=tk.W)
    
    def select_palette_color(self, index):
        self.current_color_index = index
        self.drawing_color = self.color_palette[index]
        self.update_color_indicator()
        self.update_palette_highlight()
    
    def update_palette_highlight(self):
        for i, swatch in enumerate(self.color_swatches):
            if i == self.current_color_index:
                swatch.config(highlightbackground="gold", highlightthickness=2)
            else:
                swatch.config(highlightbackground="gray", highlightthickness=1)
    
    def change_mode(self):
        mode_name = self.mode_var.get()
        self.current_mode = self.MODES[mode_name]
        
        # Reset points if mode changes
        self.prev_point = None
        self.shape_start_point = None
    
    def update_color_indicator(self):
        # Convert BGR to RGB for tkinter
        rgb_color = f'#{self.drawing_color[2]:02x}{self.drawing_color[1]:02x}{self.drawing_color[0]:02x}'
        self.color_indicator.configure(bg=rgb_color)
        self.color_indicator.create_rectangle(0, 0, 50, 30, fill=rgb_color, outline="")
    
    def choose_color(self):
        color = colorchooser.askcolor(initialcolor="#ff0000")[0]
        if color:
            # Convert RGB to BGR for OpenCV
            self.drawing_color = (int(color[2]), int(color[1]), int(color[0]))
            self.update_color_indicator()
            
            # Add to palette if not already there
            if self.drawing_color not in self.color_palette:
                self.color_palette[-1] = self.drawing_color  # Replace last color
                self.current_color_index = len(self.color_palette) - 1
                self.update_palette_highlight()
    
    def update_brush_size(self, event=None):
        self.brush_thickness = int(self.brush_size_slider.get())
        # Update UI slider to match
        self.brush_size_slider.set(self.brush_thickness)
    
    def clear_canvas(self):
        self.canvas = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        self.prev_point = None
        self.shape_start_point = None
    
    def save_drawing(self):
        # Create drawings directory if it doesn't exist
        if not os.path.exists("drawings"):
            os.makedirs("drawings")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"drawings/drawing_{timestamp}.png"
        
        # Open file dialog
        filename = filedialog.asksaveasfilename(
            initialdir="./drawings",
            initialfile=f"drawing_{timestamp}.png",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filename:
            # Save the canvas as an image file
            cv2.imwrite(filename, self.canvas)
            # Show confirmation
            confirmation = tk.Toplevel(self.root)
            confirmation.title("Success")
            ttk.Label(confirmation, text=f"Drawing saved to {filename}").pack(padx=20, pady=20)
            ttk.Button(confirmation, text="OK", command=confirmation.destroy).pack(pady=10)
    
    def hsv_to_bgr(self, h, s=1.0, v=1.0):
        """Convert HSV color to BGR color (what OpenCV uses)"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(b * 255), int(g * 255), int(r * 255))
    
    def draw_pattern(self, canvas, start_point, end_point, color, thickness):
        # Draw a pattern between two points (example: dotted line)
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        distance = max(1, int(np.sqrt(dx*dx + dy*dy)))
        
        for i in range(0, distance, 10):  # Adjust spacing
            # Calculate point position
            x = int(start_point[0] + dx * i / distance)
            y = int(start_point[1] + dy * i / distance)
            
            # Draw pattern element (circle in this case)
            cv2.circle(canvas, (x, y), thickness, color, -1)
            
            # Add some randomness for artistic effect
            if random.random() > 0.7:  # 30% chance for extra dot
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                cv2.circle(canvas, (x + offset_x, y + offset_y), 
                          thickness // 2, color, -1)
    
    def detect_gestures(self, hand_landmarks):
        # Get landmark positions
        landmarks = [(int(lm.x * self.canvas_width), int(lm.y * self.canvas_height)) 
                     for lm in hand_landmarks.landmark]
        
        # Index finger tip (drawing pointer)
        index_tip = landmarks[8]
        
        # Drawing control (index + middle finger up = not drawing)
        index_up = landmarks[8][1] < landmarks[6][1]  # Index finger up
        middle_up = landmarks[12][1] < landmarks[10][1]  # Middle finger up
        
        if index_up and middle_up:
            self.is_drawing = False
            # For shape modes, complete the shape when fingers are raised
            if self.current_mode in [self.MODES['LINE'], self.MODES['RECTANGLE'], self.MODES['CIRCLE']] and self.shape_start_point is not None:
                self.complete_shape()
            self.prev_point = None
            self.shape_start_point = None
        elif index_up:
            self.is_drawing = True
            # If starting to draw in shape mode, set start point
            if self.current_mode in [self.MODES['LINE'], self.MODES['RECTANGLE'], self.MODES['CIRCLE']] and self.shape_start_point is None:
                self.shape_start_point = index_tip
        else:
            self.is_drawing = False
        
        # Color change gesture (closed fist)
        thumb_tip = landmarks[4]
        pinky_tip = landmarks[20]
        distance_thumb_pinky = np.sqrt((thumb_tip[0] - pinky_tip[0])**2 + (thumb_tip[1] - pinky_tip[1])**2)
        
        # Check if fingers are curled (fist)
        all_fingers_down = all([
            landmarks[8][1] > landmarks[6][1],   # Index down
            landmarks[12][1] > landmarks[10][1], # Middle down
            landmarks[16][1] > landmarks[14][1], # Ring down
            landmarks[20][1] > landmarks[18][1]  # Pinky down
        ])
        
        # Closed fist gesture (cycle through preset colors)
        if distance_thumb_pinky < 50 and all_fingers_down and not self.color_change_active:
            self.color_change_active = True
            # Cycle through preset color palette
            self.current_color_index = (self.current_color_index + 1) % len(self.color_palette)
            self.drawing_color = self.color_palette[self.current_color_index]
            self.update_color_indicator()
            self.update_palette_highlight()
        elif distance_thumb_pinky >= 50 or not all_fingers_down:
            self.color_change_active = False
        
        # OK gesture for color selection mode (thumb and index finger form a circle)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance_thumb_index = np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
        
        # Other fingers up for OK gesture
        other_fingers_up = all([
            landmarks[12][1] < landmarks[10][1],  # Middle up
            landmarks[16][1] < landmarks[14][1],  # Ring up
            landmarks[20][1] < landmarks[18][1]   # Pinky up
        ])
        
        # OK gesture (thumb and index touch, other fingers up)
        is_ok_gesture = distance_thumb_index < 30 and other_fingers_up
        
        if is_ok_gesture and not self.color_select_active:
            # Enter color selection mode
            self.color_select_active = True
            self.color_select_start_pos = index_tip[0]
        elif self.color_select_active and is_ok_gesture:
            # In color selection mode, move left/right to change hue
            movement = (index_tip[0] - self.color_select_start_pos) / self.canvas_width
            # Update hue based on horizontal position (wrap around 0-1)
            self.hue = (self.hue + movement) % 1.0
            self.color_select_start_pos = index_tip[0]
            
            # Convert HSV to BGR and update color
            self.drawing_color = self.hsv_to_bgr(self.hue, 1.0, 1.0)
            self.update_color_indicator()
        elif not is_ok_gesture:
            self.color_select_active = False
        
        # Brush size adjustment (pinky finger)
        pinky_tip = landmarks[20]
        pinky_up = landmarks[20][1] < landmarks[18][1]  # Pinky finger up
        other_fingers_down = all([
            landmarks[8][1] > landmarks[6][1],   # Index down
            landmarks[12][1] > landmarks[10][1], # Middle down
            landmarks[16][1] > landmarks[14][1]  # Ring down
        ])
        
        # First time raising pinky
        if pinky_up and other_fingers_down and not self.brush_size_active:
            self.brush_size_active = True
            self.initial_pinky_y = pinky_tip[1]
        # Continuing to adjust with pinky
        elif pinky_up and other_fingers_down and self.brush_size_active:
            if self.initial_pinky_y is not None:
                # Calculate vertical movement
                delta_y = self.initial_pinky_y - pinky_tip[1]
                # Map vertical position to brush size (1-30)
                # Moving up increases size, moving down decreases
                new_size = int(self.brush_thickness + (delta_y / 100))  # Adjust sensitivity
                new_size = max(1, min(30, new_size))  # Clamp between 1 and 30
                
                if abs(new_size - self.brush_thickness) > 0:
                    self.brush_thickness = new_size
                    self.update_brush_size()
                    self.initial_pinky_y = pinky_tip[1]  # Update reference point
        # Released pinky
        elif not pinky_up and self.brush_size_active:
            self.brush_size_active = False
            self.initial_pinky_y = None
        
        # Clear canvas gesture (open palm)
        all_fingers_up = all([
            landmarks[4][1] < landmarks[3][1],   # Thumb up
            landmarks[8][1] < landmarks[6][1],   # Index up
            landmarks[12][1] < landmarks[10][1], # Middle up
            landmarks[16][1] < landmarks[14][1], # Ring up
            landmarks[20][1] < landmarks[18][1]  # Pinky up
        ])
        
        if all_fingers_up and not self.clear_gesture_active:
            self.clear_gesture_active = True
            self.clear_canvas()
        elif not all_fingers_up:
            self.clear_gesture_active = False
        
        # Thumb up gesture to change mode
        thumb_up = landmarks[4][1] < landmarks[3][1] and landmarks[4][1] < landmarks[9][1]
        other_fingers_down = all([
            landmarks[8][1] > landmarks[6][1],  # Index down
            landmarks[12][1] > landmarks[10][1],  # Middle down
            landmarks[16][1] > landmarks[14][1],  # Ring down
            landmarks[20][1] > landmarks[18][1]   # Pinky down
        ])
        
        if thumb_up and other_fingers_down and not self.mode_change_active:
            self.mode_change_active = True
            # Cycle through drawing modes
            self.current_mode = (self.current_mode + 1) % len(self.MODES)
            # Update the radio button in UI
            self.mode_var.set(self.mode_names[self.current_mode])
            self.prev_point = None
            self.shape_start_point = None
        elif not (thumb_up and other_fingers_down):
            self.mode_change_active = False
        
        return index_tip
    
    def complete_shape(self):
        if self.shape_start_point is not None and self.prev_point is not None:
            if self.current_mode == self.MODES['LINE']:
                cv2.line(self.canvas, self.shape_start_point, self.prev_point, 
                         self.drawing_color, self.brush_thickness)
            
            elif self.current_mode == self.MODES['RECTANGLE']:
                cv2.rectangle(self.canvas, self.shape_start_point, self.prev_point, 
                             self.drawing_color, self.brush_thickness)
            
            elif self.current_mode == self.MODES['CIRCLE']:
                # Calculate radius from the distance between points
                dx = self.prev_point[0] - self.shape_start_point[0]
                dy = self.prev_point[1] - self.shape_start_point[1]
                radius = int(np.sqrt(dx*dx + dy*dy))
                cv2.circle(self.canvas, self.shape_start_point, radius, 
                          self.drawing_color, self.brush_thickness)
    
    def update_frame(self):
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        # Calculate FPS
        self.frame_times.append(elapsed)
        if len(self.frame_times) > 30:  # Keep last 30 frames for average
            self.frame_times.pop(0)
        self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally for a more intuitive mirroring effect
            frame = cv2.flip(frame, 1)
            
            # Resize frame to fit our canvas dimensions
            frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
            
            # Convert the image to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(rgb_frame)
            
            # Create a temporary canvas for shape preview
            if self.current_mode in [self.MODES['LINE'], self.MODES['RECTANGLE'], self.MODES['CIRCLE']]:
                self.temp_canvas = self.canvas.copy()
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on the frame
                    self.mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Detect gestures and get current pointer position
                    pointer_pos = self.detect_gestures(hand_landmarks)
                    
                    # Draw based on the current mode
                    if self.is_drawing:
                        # Freestyle drawing
                        if self.current_mode == self.MODES['FREESTYLE']:
                            if self.prev_point is None:
                                self.prev_point = pointer_pos
                            else:
                                cv2.line(self.canvas, self.prev_point, pointer_pos, 
                                        self.drawing_color, self.brush_thickness)
                                self.prev_point = pointer_pos
                        
                        # Eraser mode
                        elif self.current_mode == self.MODES['ERASER']:
                            if self.prev_point is None:
                                self.prev_point = pointer_pos
                            else:
                                # Draw with black (background color)
                                cv2.line(self.canvas, self.prev_point, pointer_pos, 
                                        (0, 0, 0), self.brush_thickness * 2)  # Make eraser larger
                                self.prev_point = pointer_pos
                        
                        # Pattern brush
                        elif self.current_mode == self.MODES['PATTERN']:
                            if self.prev_point is None:
                                self.prev_point = pointer_pos
                            else:
                                self.draw_pattern(self.canvas, self.prev_point, pointer_pos, 
                                                 self.drawing_color, self.brush_thickness)
                                self.prev_point = pointer_pos
                        
                        # Shape drawing (preview)
                        elif self.current_mode in [self.MODES['LINE'], self.MODES['RECTANGLE'], self.MODES['CIRCLE']]:
                            if self.shape_start_point is not None:
                                self.prev_point = pointer_pos
                                
                                # Create a temporary canvas for preview
                                temp_canvas = self.canvas.copy()
                                
                                if self.current_mode == self.MODES['LINE']:
                                    cv2.line(temp_canvas, self.shape_start_point, pointer_pos, 
                                            self.drawing_color, self.brush_thickness)
                                
                                elif self.current_mode == self.MODES['RECTANGLE']:
                                    cv2.rectangle(temp_canvas, self.shape_start_point, pointer_pos, 
                                                self.drawing_color, self.brush_thickness)
                                
                                elif self.current_mode == self.MODES['CIRCLE']:
                                    # Calculate radius from the distance between points
                                    dx = pointer_pos[0] - self.shape_start_point[0]
                                    dy = pointer_pos[1] - self.shape_start_point[1]
                                    radius = int(np.sqrt(dx*dx + dy*dy))
                                    cv2.circle(temp_canvas, self.shape_start_point, radius, 
                                            self.drawing_color, self.brush_thickness)
                                
                                # Use the temporary canvas for display
                                combined_img = cv2.addWeighted(frame, 0.7, temp_canvas, 0.7, 0)
                                
                                # Convert to RGB for tkinter
                                rgb_img = cv2.cvtColor(combined_img, cv2.COLOR_BGR2RGB)
                                
                                # Convert to ImageTk format
                                img = Image.fromarray(rgb_img)
                                imgtk = ImageTk.PhotoImage(image=img)
                                
                                # Update the UI
                                self.video_frame.imgtk = imgtk
                                self.video_frame.configure(image=imgtk)
                                
                                # Skip the rest of the update to avoid overwriting our preview
                                self.root.after(33, self.update_frame)
                                return
                    else:
                        # Draw a circle at the pointer position
                        cv2.circle(frame, pointer_pos, 10, self.drawing_color, -1)
            else:
                self.prev_point = None
            
            # Show mode indicators
            if self.color_select_active:
                cv2.putText(frame, "Color Selection Mode", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Draw color wheel indicator
                wheel_center = (self.canvas_width - 50, 50)
                wheel_radius = 30
                cv2.circle(frame, wheel_center, wheel_radius, (255, 255, 255), 2)
                
                # Draw current hue marker
                angle = self.hue * 2 * np.pi
                marker_x = int(wheel_center[0] + wheel_radius * np.cos(angle))
                marker_y = int(wheel_center[1] + wheel_radius * np.sin(angle))
                cv2.circle(frame, (marker_x, marker_y), 5, self.drawing_color, -1)
            
            # Draw current brush size indicator
            cv2.circle(frame, (30, 30), self.brush_thickness, self.drawing_color, -1)
            
            # Display current mode
            mode_text = f"Mode: {self.mode_names[self.current_mode]}"
            cv2.putText(frame, mode_text, (50, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display FPS
            cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Combine canvas with frame
            combined_img = cv2.addWeighted(frame, 0.7, self.canvas, 0.7, 0)
            
            # Convert to RGB for tkinter
            rgb_img = cv2.cvtColor(combined_img, cv2.COLOR_BGR2RGB)
            
            # Convert to ImageTk format
            img = Image.fromarray(rgb_img)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update the UI
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        
        # Calculate next frame delay to maintain target FPS
        frame_time = time.time() - current_time
        delay = max(1, int((self.frame_interval - frame_time) * 1000))
        self.last_frame_time = current_time
        
        # Schedule next frame
        self.root.after(delay, self.update_frame)
    
    def on_closing(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedGestureDrawingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 