"""
Training Wizard for Custom Beverage Detection Models
Provides step-by-step UI for training custom YOLO models
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import threading
import os
from PIL import Image, ImageTk
from config.settings import LOGO_PATH

class TrainingWizard:
    """Wizard interface for training custom beverage detection models"""
    
    def __init__(self, parent=None):
        """Initialize training wizard"""
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Tangent Connect - Model Training Wizard")
        self.window.geometry("800x600")
        
        self.current_step = 0
        self.data_source = tk.StringVar(value="folder")
        self.data_path = tk.StringVar()
        self.model_name = tk.StringVar(value="custom_beverage_model")
        self.epochs = tk.IntVar(value=50)
        self.batch_size = tk.IntVar(value=16)
        self.image_size = tk.IntVar(value=640)
        
        # Load logo for icon
        try:
            self.logo_img = Image.open(LOGO_PATH)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.window.iconphoto(True, self.logo_photo)
        except Exception:
            self.logo_photo = None
            
        self._build_ui()
        
    def _build_ui(self):
        """Build wizard UI"""
        # Header
        header = ttk.Frame(self.window, padding=10)
        header.pack(fill=tk.X)
        
        ttk.Label(
            header, 
            text="Tangent Connect AI Vision",
            font=('Arial', 16, 'bold')
        ).pack()
        
        ttk.Label(
            header,
            text="Model Training Wizard",
            font=('Arial', 12)
        ).pack()
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.window, padding=10)
        self.progress_frame.pack(fill=tk.X)
        
        self.steps = ["Data Source", "Label Images", "Configure", "Train"]
        self.step_labels = []
        
        for i, step in enumerate(self.steps):
            frame = ttk.Frame(self.progress_frame)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            
            label = ttk.Label(frame, text=f"{i+1}. {step}", font=('Arial', 9))
            label.pack()
            self.step_labels.append(label)
        
        # Content area
        self.content_frame = ttk.Frame(self.window, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.window, padding=10)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.back_btn = ttk.Button(nav_frame, text="← Back", command=self._prev_step)
        self.back_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self._next_step)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_btn = ttk.Button(nav_frame, text="Cancel", command=self.window.destroy)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Show first step
        self._show_step()
    
    def _show_step(self):
        """Display current step"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update step labels
        for i, label in enumerate(self.step_labels):
            if i == self.current_step:
                label.config(font=('Arial', 9, 'bold'), foreground='blue')
            elif i < self.current_step:
                label.config(font=('Arial', 9), foreground='green')
            else:
                label.config(font=('Arial', 9), foreground='gray')
        
        # Show step content
        if self.current_step == 0:
            self._show_data_source_step()
        elif self.current_step == 1:
            self._show_labeling_step()
        elif self.current_step == 2:
            self._show_configuration_step()
        elif self.current_step == 3:
            self._show_training_step()
        
        # Update navigation buttons
        self.back_btn.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_btn.config(text="Finish" if self.current_step == 3 else "Next →")
    
    def _show_data_source_step(self):
        """Step 1: Choose data source"""
        ttk.Label(
            self.content_frame,
            text="Step 1: Choose Your Data Source",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        ttk.Label(
            self.content_frame,
            text="Select where your training images are located:"
        ).pack(pady=5)
        
        # Data source options
        options_frame = ttk.LabelFrame(self.content_frame, text="Data Source", padding=20)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        ttk.Radiobutton(
            options_frame,
            text="📁 Local Folder - I have a folder with images",
            variable=self.data_source,
            value="folder"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            options_frame,
            text="📷 Camera Capture - Capture images from camera",
            variable=self.data_source,
            value="camera"
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(
            options_frame,
            text="🌐 Web Download - Download from URL",
            variable=self.data_source,
            value="web"
        ).pack(anchor=tk.W, pady=5)
        
        # Path selection
        path_frame = ttk.Frame(self.content_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="Data Location:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(path_frame, textvariable=self.data_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Browse...", command=self._browse_data_path).pack(side=tk.LEFT)
    
    def _show_labeling_step(self):
        """Step 2: Label images"""
        ttk.Label(
            self.content_frame,
            text="Step 2: Label Your Images",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        info_text = """
This step helps you label beverages in your images.

For each image:
1. Draw bounding boxes around beverages
2. Select the beverage type (alcoholic/non-alcoholic)
3. Choose the specific beverage class

Recommended tools:
• LabelImg (Built-in, will open automatically)
• CVAT (Online tool)
• Roboflow (Cloud-based)
        """
        
        text_widget = tk.Text(self.content_frame, height=12, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=10)
        text_widget.insert('1.0', info_text)
        text_widget.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="🏷️ Open Labeling Tool",
            command=self._open_labeling_tool
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📝 Manual YAML Configuration",
            command=self._configure_yaml
        ).pack(side=tk.LEFT, padx=5)
    
    def _show_configuration_step(self):
        """Step 3: Configure training parameters"""
        ttk.Label(
            self.content_frame,
            text="Step 3: Configure Training Parameters",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Model name
        name_frame = ttk.Frame(self.content_frame)
        name_frame.pack(fill=tk.X, pady=10)
        ttk.Label(name_frame, text="Model Name:", width=20).pack(side=tk.LEFT)
        ttk.Entry(name_frame, textvariable=self.model_name, width=40).pack(side=tk.LEFT)
        
        # Training parameters
        params_frame = ttk.LabelFrame(self.content_frame, text="Training Parameters", padding=20)
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Epochs
        epoch_frame = ttk.Frame(params_frame)
        epoch_frame.pack(fill=tk.X, pady=5)
        ttk.Label(epoch_frame, text="Epochs:", width=20).pack(side=tk.LEFT)
        ttk.Spinbox(epoch_frame, from_=10, to=300, textvariable=self.epochs, width=10).pack(side=tk.LEFT)
        ttk.Label(epoch_frame, text="(Recommended: 50-100)").pack(side=tk.LEFT, padx=10)
        
        # Batch size
        batch_frame = ttk.Frame(params_frame)
        batch_frame.pack(fill=tk.X, pady=5)
        ttk.Label(batch_frame, text="Batch Size:", width=20).pack(side=tk.LEFT)
        ttk.Spinbox(batch_frame, from_=4, to=64, textvariable=self.batch_size, width=10).pack(side=tk.LEFT)
        ttk.Label(batch_frame, text="(Recommended: 16)").pack(side=tk.LEFT, padx=10)
        
        # Image size
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="Image Size:", width=20).pack(side=tk.LEFT)
        ttk.Combobox(
            size_frame,
            textvariable=self.image_size,
            values=[320, 416, 512, 640, 1280],
            width=10,
            state='readonly'
        ).pack(side=tk.LEFT)
        ttk.Label(size_frame, text="(Recommended: 640)").pack(side=tk.LEFT, padx=10)
    
    def _show_training_step(self):
        """Step 4: Start training"""
        ttk.Label(
            self.content_frame,
            text="Step 4: Train Your Model",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        info_frame = ttk.LabelFrame(self.content_frame, text="Training Configuration", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        configs = [
            ("Model Name:", self.model_name.get()),
            ("Data Path:", self.data_path.get()),
            ("Epochs:", str(self.epochs.get())),
            ("Batch Size:", str(self.batch_size.get())),
            ("Image Size:", f"{self.image_size.get()}x{self.image_size.get()}")
        ]
        
        for label, value in configs:
            frame = ttk.Frame(info_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label, width=15, font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
            ttk.Label(frame, text=value).pack(side=tk.LEFT)
        
        # Progress
        progress_frame = ttk.LabelFrame(self.content_frame, text="Training Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.training_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.training_progress.pack(fill=tk.X, pady=5)
        
        self.training_log = tk.Text(progress_frame, height=10, state=tk.DISABLED)
        self.training_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Start button
        self.start_training_btn = ttk.Button(
            self.content_frame,
            text="🚀 Start Training",
            command=self._start_training
        )
        self.start_training_btn.pack(pady=10)
    
    def _browse_data_path(self):
        """Browse for data path"""
        if self.data_source.get() == "folder":
            path = filedialog.askdirectory(title="Select Image Folder")
            if path:
                self.data_path.set(path)
    
    def _open_labeling_tool(self):
        """Open image labeling tool"""
        import subprocess
        try:
            # Try to launch labelImg if installed as a package
            subprocess.Popen(['labelImg'])
        except FileNotFoundError:
            messagebox.showinfo(
                "Labeling Tool",
                "To label your images, we recommend installing 'labelImg':\n\n"
                "1. Run: pip install labelImg\n"
                "2. Then run 'labelImg' from your terminal\n\n"
                "Alternative Online Tools:\n"
                "• CVAT: https://cvat.org\n"
                "• Roboflow: https://roboflow.com\n\n"
                "Important: Export labels in YOLO format!"
            )
    
    def _configure_yaml(self):
        """Configure dataset YAML"""
        yaml_content = f"""# Beverage Detection Dataset Configuration
# Path to dataset
path: {self.data_path.get() or './data'}

# Train/Val/Test splits
train: images/train
val: images/val
test: images/test

# Classes
nc: 10  # number of classes
names: ['beer_bottle', 'wine_bottle', 'vodka_bottle', 'whiskey_bottle', 'beer_can',
        'soda_bottle', 'soda_can', 'water_bottle', 'juice_bottle', 'energy_drink']
"""
        
        yaml_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if yaml_path:
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            messagebox.showinfo("Success", f"Dataset configuration saved to:\n{yaml_path}")
    
    def _start_training(self):
        """Start model training"""
        data_path = Path(self.data_path.get())
        if not data_path.exists():
            messagebox.showerror("Error", f"Data path does not exist:\n{data_path}")
            return
            
        # Check for required structure
        required_dirs = [data_path / "images/train", data_path / "images/val"]
        missing = [str(d) for d in required_dirs if not d.exists()]
        if missing:
            messagebox.showwarning("Incomplete Dataset", 
                "The following folders are missing from your data path:\n" + 
                "\n".join(missing) + 
                "\n\nPlease ensure your dataset follows the YOLO structure:\n"
                "data_path/\n  images/\n    train/\n    val/\n  labels/\n    train/\n    val/")
            return

        self.start_training_btn.config(state=tk.DISABLED)
        self.training_progress.start()
        
        def train():
            try:
                self._log_training("Starting training process...")
                self._log_training(f"Model: {self.model_name.get()}")
                self._log_training(f"Epochs: {self.epochs.get()}")
                self._log_training(f"Batch Size: {self.batch_size.get()}")
                self._log_training("")
                
                # Check if ultralytics is available
                try:
                    from ultralytics import YOLO
                    
                    # Create dataset YAML if needed
                    data_yaml = Path("data/beverage_dataset.yaml")
                    if not data_yaml.exists():
                        self._log_training("Creating dataset configuration...")
                        data_yaml.parent.mkdir(parents=True, exist_ok=True)
                        with open(data_yaml, 'w') as f:
                            f.write(f"""path: {self.data_path.get() or './data'}
train: images/train
val: images/val
nc: 10
names: ['beer_bottle', 'wine_bottle', 'vodka_bottle', 'whiskey_bottle', 'beer_can',
        'soda_bottle', 'soda_can', 'water_bottle', 'juice_bottle', 'energy_drink']
""")
                    
                    self._log_training("Initializing YOLO model...")
                    model = YOLO('yolov8n.pt')
                    
                    self._log_training("Training started... This may take a while.")
                    self._log_training("Check console for detailed progress.")
                    
                    # Train the model
                    results = model.train(
                        data=str(data_yaml),
                        epochs=self.epochs.get(),
                        batch=self.batch_size.get(),
                        imgsz=self.image_size.get(),
                        name=self.model_name.get(),
                        patience=10,
                        save=True,
                        plots=True
                    )
                    
                    self._log_training("")
                    self._log_training("✓ Training completed successfully!")
                    self._log_training(f"Model saved to: runs/detect/{self.model_name.get()}/weights/best.pt")
                    
                    self.window.after(100, lambda: messagebox.showinfo(
                        "Training Complete",
                        f"Model training finished!\n\n"
                        f"Model saved to:\nruns/detect/{self.model_name.get()}/weights/best.pt\n\n"
                        f"You can now load this model in the main application."
                    ))
                    
                except ImportError:
                    self._log_training("⚠ Ultralytics not installed!")
                    self._log_training("Please install: pip install ultralytics")
                    
            except Exception as e:
                self._log_training(f"✗ Training error: {str(e)}")
                
            finally:
                self.window.after(100, lambda: self.training_progress.stop())
                self.window.after(100, lambda: self.start_training_btn.config(state=tk.NORMAL))
        
        threading.Thread(target=train, daemon=True).start()
    
    def _log_training(self, message):
        """Log training message"""
        def update():
            self.training_log.config(state=tk.NORMAL)
            self.training_log.insert(tk.END, message + "\n")
            self.training_log.see(tk.END)
            self.training_log.config(state=tk.DISABLED)
        
        self.window.after(0, update)
    
    def _next_step(self):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._show_step()
        else:
            self.window.destroy()
    
    def _prev_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_step()
    
    def run(self):
        """Run the wizard"""
        self.window.mainloop()


if __name__ == "__main__":
    wizard = TrainingWizard()
    wizard.run()
