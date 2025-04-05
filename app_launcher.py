import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Drawing App Launcher")
        self.root.geometry("500x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Gesture Drawing Application", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Description
        description = """
        Choose which version of the gesture drawing app you want to launch:
        
        • Standard: Main application with all core features
        • Advanced: Extended version with shapes and pattern tools
        """
        desc_label = ttk.Label(main_frame, text=description, justify=tk.LEFT)
        desc_label.pack(pady=10, anchor=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # App buttons
        standard_btn = ttk.Button(
            button_frame, 
            text="Launch Standard App", 
            width=25,
            command=self.launch_standard
        )
        standard_btn.pack(pady=5)
        
        advanced_btn = ttk.Button(
            button_frame, 
            text="Launch Advanced App", 
            width=25,
            command=self.launch_advanced
        )
        advanced_btn.pack(pady=5)
        
        # Check dependencies button
        check_btn = ttk.Button(
            main_frame, 
            text="Check Dependencies", 
            command=self.check_dependencies
        )
        check_btn.pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to launch")
        status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            font=("Arial", 10, "italic")
        )
        status_label.pack(pady=10)
    
    def launch_standard(self):
        self.status_var.set("Launching standard application...")
        self.root.update()
        self.launch_script("gesture_drawing_app.py")
    
    def launch_advanced(self):
        self.status_var.set("Launching advanced application...")
        self.root.update()
        self.launch_script("advanced_gesture_drawing.py")
    
    def launch_script(self, script_name):
        try:
            if not os.path.exists(script_name):
                self.status_var.set(f"Error: {script_name} not found!")
                return
            
            # Use Python executable from sys.executable to ensure we use the same environment
            python_exe = sys.executable
            subprocess.Popen([python_exe, script_name])
            self.status_var.set(f"Launched {script_name} successfully")
        except Exception as e:
            self.status_var.set(f"Error launching app: {str(e)}")
    
    def check_dependencies(self):
        self.status_var.set("Checking dependencies...")
        self.root.update()
        
        try:
            # Create a popup to show dependency status
            popup = tk.Toplevel(self.root)
            popup.title("Dependency Check")
            popup.geometry("400x300")
            
            # Create a text widget to display results
            result_text = tk.Text(popup, wrap=tk.WORD, padx=10, pady=10)
            result_text.pack(fill=tk.BOTH, expand=True)
            
            # Check for each dependency
            dependencies = {
                "OpenCV": "cv2",
                "MediaPipe": "mediapipe",
                "NumPy": "numpy",
                "Pillow": "PIL",
                "Tkinter": "tkinter"
            }
            
            for name, module in dependencies.items():
                try:
                    __import__(module)
                    result_text.insert(tk.END, f"✅ {name}: Installed\n")
                except ImportError:
                    result_text.insert(tk.END, f"❌ {name}: Not installed\n")
            
            # Add a close button
            close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=10)
            
            self.status_var.set("Dependency check complete")
        except Exception as e:
            self.status_var.set(f"Error checking dependencies: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop() 