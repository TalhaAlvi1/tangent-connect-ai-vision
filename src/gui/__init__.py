"""GUI package"""
from .main_window import BeverageDetectionApp

def main():
    """Main GUI entry point"""
    import tkinter as tk
    root = tk.Tk()
    app = BeverageDetectionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

__all__ = ['BeverageDetectionApp', 'main']
