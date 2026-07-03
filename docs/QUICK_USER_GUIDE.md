# 🎯 Quick User Guide - Beverage Detection System

## 🚀 Getting Started (3 Minutes)

### Step 1: Launch the Application
**Option A (Easiest):**
```
Double-click: RUN_APP.bat
```

**Option B (Manual):**
```
python main.py
```

You should see:
```
============================================================
BEVERAGE DETECTION & COUNTING SYSTEM v1.0
============================================================
Checking dependencies...
✓ All dependencies found
✓ Using modern theme (ttkbootstrap)
Starting application...
============================================================
```

### Step 2: Application Window Opens
The GUI window will appear with:

**Left Side - Video Display:**
- Large black area for live camera feed
- Shows "Live Feed" at the top

**Right Side - Control Panel:**
- **Camera Section**: URL input box with connect/disconnect buttons
- **Controls Section**: Start, Stop, Reset buttons
- **Statistics Section**: Total counts, alcoholic/non-alcoholic breakdown
- **Details Table**: List of detected beverages with counts

**Top Menu Bar:**
- File: Export, Exit
- Model: Train New Model, Load Custom Model
- Help: About

**Bottom Status Bar:**
- Shows current status (Ready, Connected, Processing, etc.)

---

## 📹 Using the Camera

### Connect to Demo Stream (No Camera Needed)
1. The default URL is already filled in:
   ```
   rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
   ```
2. Click **"Connect"** button
3. Wait for status to show "Connected" (3-5 seconds)
4. The Start button will become enabled

### Connect to Your IP Camera
1. Clear the URL field
2. Enter your camera's RTSP URL:
   ```
   rtsp://username:password@ip-address:port/stream
   ```
   Examples:
   - `rtsp://admin:12345@192.168.1.100:554/stream1`
   - `rtsp://192.168.1.100/live`
3. Click **"Connect"**
4. Wait for connection confirmation

### Camera Not Working?
- ✅ Check if camera is powered on
- ✅ Verify you're on the same network
- ✅ Test URL in VLC Media Player first
- ✅ Check firewall settings
- ✅ Try the demo URL to verify app works

---

## 🎬 Running Detection

### Start Detection
1. Ensure camera is connected (button shows "Connected")
2. Click **"▶ Start"** button
3. You will see:
   - Live video feed appears
   - Colored boxes around detected beverages
   - Red boxes = Alcoholic drinks
   - Green boxes = Non-alcoholic drinks
   - Labels show: beverage type + confidence score
   - Statistics update in real-time on the right

### Understanding the Display

**Video Feed:**
- Bounding boxes around beverages
- Labels: `[beverage_name] (type) 0.XX`
- Example: `beer_bottle (alcoholic) 0.87`

**Statistics Panel:**
- **Total: X** - All beverages counted
- **Alcoholic: X** - Red drinks count
- **Non-Alcoholic: X** - Green drinks count

**Details Table:**
| Type | Count |
|------|-------|
| beer_bottle | 3 |
| soda_can | 5 |
| water_bottle | 2 |

### Stop Detection
1. Click **"■ Stop"** button
2. Detection pauses
3. Session data is saved to database
4. Video feed freezes on last frame

### Reset Counts
1. Click **"Reset"** button (in Controls section)
2. All counts reset to zero
3. Tracking IDs reset
4. Detection continues if running

---

## 💾 Exporting Data

### Export Current Session
1. Run detection for a while
2. Click **File → Export** from menu
3. Choose save location and filename
4. Click Save
5. CSV file created with:
   - Timestamp
   - Beverage class
   - Type (alcoholic/non-alcoholic)
   - Confidence score

### CSV Format
```csv
Timestamp,Beverage Class,Type,Confidence
2024-01-24 10:30:15,beer_bottle,alcoholic,0.89
2024-01-24 10:30:16,soda_can,non-alcoholic,0.92
...
```

---

## 🎓 Training Custom Models

### When to Train
- You have specific beverage brands to detect
- Pre-configured classes don't match your needs
- You want better accuracy for your environment
- You have 100+ labeled images

### Training Process

#### Step 1: Open Training Wizard
1. Click **Model → Train New Model**
2. New window opens: "Custom Model Training Wizard"

#### Step 2: Choose Data Source
- **📁 Local Folder**: You have images in a folder
  - Click "Browse"
  - Select folder with images
  - Images should be in subfolders: `images/train` and `images/val`

- **📷 Camera Capture**: Capture images from camera
  - Use this to collect new images
  - Take photos of beverages from different angles

- **🌐 Web Download**: Download from URL
  - For online datasets

Click **"Next →"**

#### Step 3: Label Images
1. Read the instructions in the window
2. Click **"🏷️ Open Labeling Tool"**
3. Use one of these tools (opens instructions):
   - **LabelImg** (Recommended for beginners)
   - **CVAT** (Online tool)
   - **Roboflow** (Cloud-based)

4. Draw boxes around beverages in each image
5. Assign correct class labels
6. Export in YOLO format

7. Click **"📝 Manual YAML Configuration"** to create dataset config
8. Save the YAML file

Click **"Next →"**

#### Step 4: Configure Training
Set parameters:
- **Model Name**: `my_beverage_model`
- **Epochs**: 50-100 (more = better but slower)
- **Batch Size**: 16 (reduce if out of memory)
- **Image Size**: 640 (recommended)

Click **"Next →"**

#### Step 5: Start Training
1. Review configuration
2. Click **"🚀 Start Training"**
3. Watch progress bar
4. Training takes 1-4 hours depending on:
   - Number of images
   - Epochs
   - Your computer speed
   - GPU availability

5. When complete, you'll see:
   ```
   ✓ Training completed successfully!
   Model saved to: runs/detect/my_beverage_model/weights/best.pt
   ```

### Load Your Custom Model
1. Click **Model → Load Custom Model**
2. Navigate to: `runs/detect/[your_model_name]/weights/`
3. Select `best.pt`
4. Click Open
5. Success message appears
6. Your model is now active!

---

## 🎨 User Interface Guide

### Color Coding
- **🔴 Red Boxes/Text**: Alcoholic beverages
- **🟢 Green Boxes/Text**: Non-alcoholic beverages
- **⚫ Black Background**: Video preview area
- **🔵 Blue Text**: Active/selected items

### Button States
- **Enabled (Dark)**: Can be clicked
- **Disabled (Gray)**: Cannot be clicked
- **Active (Highlighted)**: Currently processing

### Status Messages
- **"Ready"**: App started, waiting for action
- **"Connecting..."**: Attempting camera connection
- **"Connected"**: Camera ready, can start detection
- **"Processing"**: Detection is running
- **"Failed"**: Connection or operation failed
- **"Disconnected"**: Camera disconnected

---

## 📊 Reading Statistics

### Real-Time Counts
Statistics update every 33ms (30 times per second)

**What Gets Counted:**
- Each unique beverage that appears
- Tracked across frames to avoid duplicates
- Count increments when new object detected
- Count persists even if object leaves view

**What Doesn't Get Counted:**
- Same object multiple times
- Objects with very low confidence (< 0.25)
- Partially visible objects
- Non-beverage objects

### Accuracy Tips
✅ Good lighting improves accuracy
✅ Clear view of beverages (not obscured)
✅ Static camera position works best
✅ Close-up view better than far away
✅ Multiple angles during training

---

## ⚙️ Settings and Configuration

### Default Settings
Located in: `config/settings.py`

**Camera:**
- FPS Target: 30
- Buffer Size: 3

**Detection:**
- Confidence: 0.25 (25%)
- IOU Threshold: 0.45
- Model: yolov8n.pt

**Tracking:**
- Max Distance: 50 pixels
- Max Frames Lost: 30

### Change Settings
1. Open `config/settings.py` in text editor
2. Modify values
3. Save file
4. Restart application

---

## 🔍 Troubleshooting Common Issues

### Issue: No Video Appears
**Solution:**
- Check camera connection
- Verify RTSP URL is correct
- Try demo URL first
- Check if camera is accessible from browser/VLC

### Issue: Detection Not Counting
**Solution:**
- Ensure detection is started (Start button pressed)
- Check if objects are visible in frame
- Verify lighting is adequate
- Check console for error messages
- Try lowering confidence threshold in settings

### Issue: Too Many False Detections
**Solution:**
- Increase confidence threshold (e.g., 0.4 or 0.5)
- Train custom model with your specific beverages
- Improve camera angle/lighting
- Use higher resolution camera

### Issue: Application Slow/Laggy
**Solution:**
- Reduce frame rate (FPS_TARGET in settings)
- Use smaller image size (INPUT_SIZE)
- Close other applications
- Upgrade hardware
- Use GPU if available

### Issue: Training Fails
**Solution:**
- Check if images are properly labeled
- Verify YAML configuration
- Ensure sufficient disk space
- Check Python console for errors
- Reduce batch size if out of memory

---

## 💡 Best Practices

### For Best Detection Results:
1. **Lighting**: Bright, even lighting
2. **Camera Angle**: Straight-on view, not too high
3. **Distance**: 1-3 meters from beverages
4. **Background**: Plain, contrasting background
5. **Focus**: Sharp, not blurry
6. **Quantity**: Not too crowded (< 20 items in view)

### For Training:
1. **Variety**: Different angles, lighting, distances
2. **Quantity**: 100+ images per class minimum
3. **Quality**: High resolution, clear images
4. **Balance**: Similar number of images per class
5. **Validation**: 20% of data for validation

### For Performance:
1. **Close Background Apps**: Free up RAM/CPU
2. **Wired Connection**: Better than WiFi for cameras
3. **SSD Storage**: Faster than HDD
4. **GPU**: Dramatically speeds up processing
5. **Regular Updates**: Keep YOLO model updated

---

## 📱 Quick Reference

### Keyboard Shortcuts
- **Alt+F**: File menu
- **Alt+M**: Model menu
- **Alt+H**: Help menu

### Essential Workflows

**Quick Demo:**
1. Launch app
2. Click Connect (uses demo URL)
3. Click Start
4. Watch detection

**Daily Use:**
1. Launch app
2. Enter your camera URL
3. Connect
4. Start detection
5. Monitor counts
6. Stop and export at end of day

**Training Custom Model:**
1. Collect 100+ images
2. Label with LabelImg
3. Open training wizard
4. Configure and train
5. Load new model
6. Test accuracy

---

## ✅ Verification Checklist

Before starting, verify:
- [ ] Python 3.9+ installed
- [ ] Dependencies installed
- [ ] Application launches without errors
- [ ] GUI window appears
- [ ] Can connect to demo stream
- [ ] Video feed displays
- [ ] Detection works
- [ ] Counts update
- [ ] Can export data

---

## 🎯 Common Use Cases

### Retail Inventory Monitoring
1. Mount camera above shelf
2. Connect to camera
3. Start detection
4. Monitor stock levels
5. Export counts at end of day

### Warehouse Receiving
1. Set up camera at receiving dock
2. Scan incoming shipments
3. Count beverages automatically
4. Export data to inventory system

### Event Management
1. Camera at bar/beverage station
2. Track consumption in real-time
3. Monitor alcoholic vs non-alcoholic ratio
4. Generate reports for analysis

### Research Studies
1. Set up controlled environment
2. Record beverage choices
3. Track patterns over time
4. Export data for statistical analysis

---

## 📞 Getting Help

### Documentation Files
- `README.md` - Project overview
- `QUICKSTART.md` - Getting started
- `PROJECT_COMPLETION_REPORT.md` - Technical details
- This file - Detailed usage guide

### Log Files
Check `logs/app.log` for error messages

### Console Output
Watch the console window for real-time status

---

**You're all set! Start detecting beverages now! 🍺🥤**

*Last Updated: January 2025*
*Version: 1.0*
