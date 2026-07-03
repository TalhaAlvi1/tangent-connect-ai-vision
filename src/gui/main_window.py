"""Main Application GUI"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading, time, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.camera import CameraManager
from src.detection import BeverageDetector
from src.tracking import BeverageCounter
from src.database import DatabaseManager
from config.settings import *

class BeverageDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.camera = None
        self.detector = BeverageDetector()
        self.counter = BeverageCounter()
        self.database = DatabaseManager()
        self.is_processing = False
        self.session_id = None
        self.current_frame = None
        
        # Load logo
        try:
            self.logo_img = Image.open(LOGO_PATH)
            # Resize logo to fit the sidebar width (approx 400px)
            aspect_ratio = self.logo_img.width / self.logo_img.height
            new_width = 350
            new_height = int(new_width / aspect_ratio)
            self.logo_img = self.logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            
            # Set window icon
            self.root.iconphoto(True, self.logo_photo)
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_photo = None

        self._build_ui()
        self._update_display()
    
    def _build_ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Model menu
        model_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Model", menu=model_menu)
        model_menu.add_command(label="Train New Model", command=self._open_training_wizard)
        model_menu.add_command(label="Load Custom Model", command=self._load_custom_model)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        video_frame = ttk.LabelFrame(main, text="Live Feed", padding=5)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        ctrl = ttk.Frame(main, width=int(WINDOW_WIDTH*0.3))
        ctrl.pack(side=tk.RIGHT, fill=tk.BOTH)
        ctrl.pack_propagate(False)
        
        # Logo Display
        if self.logo_photo:
            logo_label = ttk.Label(ctrl, image=self.logo_photo)
            logo_label.pack(pady=20)
        
        conn = ttk.LabelFrame(ctrl, text="Camera", padding=10)
        conn.pack(fill=tk.X, pady=(0,10))
        
        # Camera source selection
        source_frame = ttk.Frame(conn)
        source_frame.pack(fill=tk.X, pady=2)
        ttk.Label(source_frame, text="Source:").pack(side=tk.LEFT, padx=(0,5))
        
        self.camera_source = tk.StringVar(value="webcam")
        ttk.Radiobutton(source_frame, text="Webcam", variable=self.camera_source, 
                       value="webcam", command=self._update_camera_url).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(source_frame, text="Demo", variable=self.camera_source, 
                       value="demo", command=self._update_camera_url).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(source_frame, text="RTSP", variable=self.camera_source, 
                       value="rtsp", command=self._update_camera_url).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(source_frame, text="Video File", variable=self.camera_source, 
                       value="file", command=self._update_camera_url).pack(side=tk.LEFT, padx=2)
        
        # URL/Path entry
        url_frame = ttk.Frame(conn)
        url_frame.pack(fill=tk.X, pady=5)
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.insert(0, DEFAULT_RTSP_URL)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.browse_btn = ttk.Button(url_frame, text="...", width=3, command=self._browse_file)
        self.browse_btn.pack(side=tk.LEFT)
        
        # Connection buttons
        btn_frame = ttk.Frame(conn)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # Connection buttons
        btn_frame = ttk.Frame(conn)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="Connect", command=self._connect)
        self.connect_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.disconnect_btn = ttk.Button(btn_frame, text="Disconnect", command=self._disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        proc = ttk.LabelFrame(ctrl, text="Controls", padding=10)
        proc.pack(fill=tk.X, pady=(0,10))
        self.start_btn = ttk.Button(proc, text="▶ Start", command=self._start, state=tk.DISABLED)
        self.start_btn.pack(fill=tk.X, pady=2)
        self.stop_btn = ttk.Button(proc, text="■ Stop", command=self._stop, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)
        ttk.Button(proc, text="Reset", command=lambda: self.counter.reset()).pack(fill=tk.X, pady=2)
        
        stats = ttk.LabelFrame(ctrl, text="Statistics", padding=10)
        stats.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        
        # Enhanced count display with better formatting
        count_display = ttk.Frame(stats)
        count_display.pack(fill=tk.X, pady=5)
        
        # Total count with larger font and better styling
        total_frame = ttk.Frame(count_display)
        total_frame.pack(fill=tk.X, pady=2)
        ttk.Label(total_frame, text="TOTAL", font=('Arial', 8, 'bold')).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="0", font=('Arial', 16, 'bold'), 
                                   anchor=tk.E, width=10)
        self.total_label.pack(side=tk.RIGHT)
        
        # Alcoholic count with icon-style display
        alc_frame = ttk.Frame(count_display)
        alc_frame.pack(fill=tk.X, pady=2)
        ttk.Label(alc_frame, text="🍺 ALCOHOLIC", foreground='red', 
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.alc_label = ttk.Label(alc_frame, text="0", foreground='red', 
                                 font=('Arial', 12, 'bold'), anchor=tk.E, width=10)
        self.alc_label.pack(side=tk.RIGHT)
        
        # Non-alcoholic count with icon-style display
        non_alc_frame = ttk.Frame(count_display)
        non_alc_frame.pack(fill=tk.X, pady=2)
        ttk.Label(non_alc_frame, text="🥤 NON-ALC", foreground='green', 
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.non_alc_label = ttk.Label(non_alc_frame, text="0", foreground='green', 
                                     font=('Arial', 12, 'bold'), anchor=tk.E, width=10)
        self.non_alc_label.pack(side=tk.RIGHT)
        
        # Count adjustment controls with better styling
        adjust_frame = ttk.LabelFrame(stats, text="Manual Adjust", padding=5)
        adjust_frame.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(adjust_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="−1", width=4, style='danger.Outline.TButton',
                  command=lambda: self._adjust_count(-1)).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="+1", width=4, style='success.Outline.TButton',
                  command=lambda: self._adjust_count(1)).pack(side=tk.LEFT, padx=3)
        
        # Enhanced detection list with better headers
        list_frame = ttk.LabelFrame(stats, text="Detected Items", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(list_frame, columns=('Type','Count'), show='headings', height=6)
        self.tree.heading('Type', text=' Beverage Type ')
        self.tree.heading('Count', text=' Count ')
        self.tree.column('Type', width=120, anchor=tk.W)
        self.tree.column('Count', width=60, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Enhanced count settings with better layout
        settings_frame = ttk.LabelFrame(stats, text="Tracking Settings", padding=8)
        settings_frame.pack(fill=tk.X, pady=5)
        
        # Debounce setting with better styling
        debounce_row = ttk.Frame(settings_frame)
        debounce_row.pack(fill=tk.X, pady=2)
        ttk.Label(debounce_row, text="Count Delay:", width=12).pack(side=tk.LEFT)
        self.debounce_var = tk.IntVar(value=10)
        debounce_scale = ttk.Scale(debounce_row, from_=5, to=50, variable=self.debounce_var, 
                                 orient=tk.HORIZONTAL, command=self._update_debounce)
        debounce_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.debounce_label = ttk.Label(debounce_row, text="10 frames", width=10)
        self.debounce_label.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Ready - Select camera source and click Connect")
        
        # Initialize counter with debounce setting
        self.counter = BeverageCounter(debounce_frames=self.debounce_var.get())
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)
    
    def _update_camera_url(self):
        """Update camera URL based on selected source"""
        source = self.camera_source.get()
        self.url_entry.delete(0, tk.END)
        
        if source == "webcam":
            self.url_entry.insert(0, "0")
            self.browse_btn.config(state=tk.DISABLED)
        elif source == "demo":
            self.url_entry.insert(0, "demo")
            self.browse_btn.config(state=tk.DISABLED)
        elif source == "rtsp":
            self.url_entry.insert(0, "rtsp://")
            self.browse_btn.config(state=tk.DISABLED)
        elif source == "file":
            self.url_entry.insert(0, "")
            self.browse_btn.config(state=tk.NORMAL)
    
    def _browse_file(self):
        """Browse for video file"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )
        if filename:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, filename)
    
    def _connect(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("No Source", "Please enter a camera URL or select webcam")
            return
        
        self.status_var.set("Connecting... Please wait...")
        self.connect_btn.config(state=tk.DISABLED)
        
        def do_connect():
            try:
                # Initialize camera with improved settings
                self.camera = CameraManager(url, buffer_size=5, timeout=15)
                if self.camera.start():
                    self.root.after(100, lambda: (
                        self.status_var.set(f"✓ Connected - Ready to detect (Source: {url})"),
                        self.start_btn.config(state=tk.NORMAL),
                        self.disconnect_btn.config(state=tk.NORMAL),
                        self.connect_btn.config(state=tk.DISABLED)
                    ))
                else:
                    error_msg = self.camera.get_error() if self.camera else "Unknown error"
                    self.root.after(100, lambda: (
                        self.status_var.set(f"✗ Connection Failed: {error_msg}"),
                        self.connect_btn.config(state=tk.NORMAL),
                        messagebox.showerror("Connection Failed", 
                            f"Could not connect to camera.\n\nError: {error_msg}\n\n"
                            "Troubleshooting:\n"
                            "- For Webcam: Make sure camera is connected and not in use\n"
                            "- For RTSP: Check URL format and network connection\n"
                            "- For Video File: Verify file exists and is a valid video\n\n"
                            "Try: Webcam (enter '0') or Demo mode")
                    ))
            except Exception as e:
                self.root.after(100, lambda: (
                    self.status_var.set(f"✗ Error: {str(e)}"),
                    self.connect_btn.config(state=tk.NORMAL),
                    messagebox.showerror("Connection Error", f"Error: {str(e)}")
                ))
        
        threading.Thread(target=do_connect, daemon=True).start()
    
    def _disconnect(self):
        if self.is_processing: self._stop()
        if self.camera: self.camera.stop()
        self.camera = None
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("Disconnected")
    
    def _start(self):
        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.session_id = self.database.create_session(self.url_entry.get())
        threading.Thread(target=self._process_loop, daemon=True).start()
    
    def _stop(self):
        self.is_processing = False
        if self.session_id:
            self.database.end_session(self.session_id, self.counter.get_statistics())
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def _process_loop(self):
        """Main processing loop with improved error handling"""
        frame_skip_counter = 0
        frame_skip_rate = 2  # Process every 2nd frame to reduce CPU load
        
        while self.is_processing and self.camera:
            try:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    # Camera connection issue
                    time.sleep(0.033)  # ~30 FPS wait
                    continue
                
                # Frame skipping for performance
                frame_skip_counter = (frame_skip_counter + 1) % frame_skip_rate
                if frame_skip_counter != 0:
                    self.current_frame = frame  # Show raw frame
                    time.sleep(0.01)
                    continue
                
                # Run detection
                detections = self.detector.detect(frame)
                stats, new_items = self.counter.update(detections)
                self.current_frame = self.detector.draw_detections(frame, detections)
                
                # Save to database
                if self.session_id:
                    self.database.update_counts(self.session_id, stats['counts'])
                    # Save individual detection events
                    for item in new_items:
                        self.database.save_detection(self.session_id, item)
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                print(f"Processing error: {e}")
                time.sleep(0.1)  # Longer delay on error
                continue
    
    def _update_display(self):
        # Update video display
        if self.current_frame is not None:
            try:
                frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]
                scale = min((WINDOW_WIDTH*0.7-20)/w, (WINDOW_HEIGHT-100)/h)
                frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
                photo = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.config(image=photo)
                self.video_label.image = photo
            except Exception as e:
                print(f"Display update error: {e}")
        
        # Update statistics display
        self._update_statistics()
        
        # Update status with FPS if camera is running
        if self.camera and self.camera.is_connected():
            fps = self.camera.get_fps()
            if fps > 0:
                current_status = self.status_var.get()
                if "FPS" not in current_status:
                    self.status_var.set(f"{current_status} | FPS: {fps:.1f}")
        
        self.root.after(33, self._update_display)
    
    def _export_data(self):
        if not self.session_id: return
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if f:
            self.database.export_to_csv(self.session_id, f)
            messagebox.showinfo("Success", "Exported!")
    
    def _open_training_wizard(self):
        """Open the training wizard"""
        try:
            from training_wizard import TrainingWizard
            wizard = TrainingWizard(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open training wizard:\n{str(e)}")
    
    def _load_custom_model(self):
        """Load a custom trained model"""
        model_path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("PyTorch Model", "*.pt"), ("All Files", "*.*")]
        )
        if model_path:
            try:
                self.detector.load_model(model_path)
                messagebox.showinfo("Success", f"Model loaded successfully:\n{model_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Tangent Connect - AI Vision Beverage System v1.0\n\n"
            "Professional AI-powered real-time beverage identification and counting\n\n"
            "Features:\n"
            "• RTSP camera support\n"
            "• Real-time detection with YOLOv8\n"
            "• Alcoholic/Non-alcoholic classification\n"
            "• Custom model training\n"
            "• Data export and analysis\n\n"
            "© 2024 Tangent Connect - MIT License"
        )
    
    def _adjust_count(self, adjustment: int):
        """Manually adjust the count"""
        if hasattr(self, 'counter'):
            # Adjust totals
            if adjustment > 0:
                self.counter.total_alcoholic += adjustment
            else:
                # Decrease from alcoholic first, then non-alcoholic
                if self.counter.total_alcoholic > 0:
                    self.counter.total_alcoholic = max(0, self.counter.total_alcoholic + adjustment)
                else:
                    self.counter.total_non_alcoholic = max(0, self.counter.total_non_alcoholic + adjustment)
            
            self._update_statistics()
            logger.info(f"Manual count adjustment: {adjustment:+d}")
    
    def _update_debounce(self, value):
        """Update debounce frames setting"""
        frames = int(float(value))
        self.debounce_label.config(text=f"{frames} frames")
        # Update the counter's debounce setting
        if hasattr(self, 'counter'):
            self.counter.tracker.debounce_frames = frames
    
    def _update_statistics(self):
        """Update statistics display"""
        if hasattr(self, 'counter'):
            stats = self.counter.get_statistics()
            self.total_label.config(text=f"Total: {stats['total_beverages']}")
            self.alc_label.config(text=f"Alcoholic: {stats['total_alcoholic']}")
            self.non_alc_label.config(text=f"Non-Alcoholic: {stats['total_non_alcoholic']}")
            
            # Update detection list
            self.tree.delete(*self.tree.get_children())
            for bev, cnt in sorted(stats['counts'].items()):
                self.tree.insert('', tk.END, values=(bev, cnt))
    
    def on_closing(self):
        if self.is_processing: self._stop()
        if self.camera: self.camera.stop()
        self.database.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BeverageDetectionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
