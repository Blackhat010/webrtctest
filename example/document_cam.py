#!/usr/bin/env python3
"""
Document-Optimized Camera Server
------------------------------
This script creates a high-quality document camera server optimized for reading text documents.
It uses Picamera2 with settings specifically tuned for document clarity and readability.

Features:
- Higher resolution (1920x1080 or higher if supported)
- Enhanced sharpness and contrast for text readability
- Reduced compression artifacts for clearer text
- Adaptive brightness for better document visibility
- Simple web interface for viewing

Usage:
    1. Install required dependencies:
        pip install flask picamera2 opencv-python numpy
    
    2. Run the script:
        python document_cam.py
    
    3. Access the camera feed:
        http://[raspberry-pi-ip]:8000/video

Requirements:
    - Raspberry Pi with Camera Module
    - Python packages: flask, picamera2, opencv-python, numpy
"""

from flask import Flask, Response, render_template_string
from picamera2 import Picamera2, Preview
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import cv2
import numpy as np
import time
import io
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Document Camera</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; background-color: #f0f0f0; }
        h1 { color: #333; }
        .container { max-width: 1280px; margin: 0 auto; }
        .video-container { margin-top: 20px; }
        img { max-width: 100%; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .controls { margin: 20px 0; }
        button { padding: 8px 16px; margin: 0 5px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Document Camera</h1>
        <div class="video-container">
            <img src="/video" alt="Document Camera Feed">
        </div>
        <div class="controls">
            <button onclick="fetch('/adjust/sharper')">Increase Sharpness</button>
            <button onclick="fetch('/adjust/contrast')">Increase Contrast</button>
            <button onclick="fetch('/adjust/brighter')">Increase Brightness</button>
            <button onclick="fetch('/adjust/reset')">Reset Settings</button>
        </div>
    </div>
</body>
</html>
"""

class DocumentCamera:
    def __init__(self, resolution=(1920, 1080), framerate=30):
        self.resolution = resolution
        self.framerate = framerate
        self.picam2 = None
        self.output = None
        self.frame_buffer = io.BytesIO()
        self.condition = threading.Condition()
        self.running = False
        
        # Document-optimized camera settings
        self.sharpness = 3.0    # Higher sharpness for text clarity (0.0-15.99)
        self.contrast = 2.5     # Higher contrast for better text visibility (0.0-15.99)
        self.brightness = 0.2   # Slightly higher brightness for white paper (0.0-1.0)
        self.saturation = 1.0   # Lower saturation for document reading (0.0-15.99)
        
        # Initialize camera
        self.initialize_camera()
        
    def initialize_camera(self):
        try:
            self.picam2 = Picamera2()
            
            # Create a high-quality still configuration for document reading
            # Using still configuration for better quality
            config = self.picam2.create_still_configuration(
                main={"size": self.resolution, "format": "RGB888"},
                lores={"size": (640, 480)},
                display="lores",
                buffer_count=2
            )
            
            self.picam2.configure(config)
            
            # Set camera controls for document optimization
            self.update_camera_controls()
            
            logging.info(f"Camera initialized with resolution {self.resolution}")
        except Exception as e:
            logging.error(f"Failed to initialize camera: {e}")
            raise
    
    def update_camera_controls(self):
        try:
            controls = {
                "Sharpness": self.sharpness,
                "Contrast": self.contrast,
                "Brightness": self.brightness,
                "Saturation": self.saturation,
                "NoiseReductionMode": 2,  # High quality noise reduction
                "AeExposureMode": 0,      # Normal exposure
                "FrameDurationLimits": (33333, 33333)  # ~30fps
            }
            self.picam2.set_controls(controls)
            logging.info(f"Camera controls updated: Sharpness={self.sharpness}, Contrast={self.contrast}, Brightness={self.brightness}")
        except Exception as e:
            logging.error(f"Failed to update camera controls: {e}")
    
    def adjust_settings(self, setting_type):
        if setting_type == "sharper":
            self.sharpness = min(self.sharpness + 1.0, 15.0)
        elif setting_type == "contrast":
            self.contrast = min(self.contrast + 0.5, 15.0)
        elif setting_type == "brighter":
            self.brightness = min(self.brightness + 0.1, 1.0)
        elif setting_type == "reset":
            self.sharpness = 3.0
            self.contrast = 2.5
            self.brightness = 0.2
            self.saturation = 1.0
        
        self.update_camera_controls()
        return {"status": "success", "settings": {
            "sharpness": self.sharpness,
            "contrast": self.contrast,
            "brightness": self.brightness
        }}
    
    def process_frame(self, frame):
        """Apply document-optimizing processing to the frame"""
        # Convert to grayscale for document processing
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding to enhance text
        # This helps with varying lighting conditions across the document
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 21, 15
        )
        
        # Convert back to RGB for display
        enhanced = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
        
        # Blend with original for a more natural look
        # Adjust alpha to control the strength of the enhancement
        alpha = 0.7  # 0.0-1.0, higher values use more of the enhanced image
        blended = cv2.addWeighted(frame, 1-alpha, enhanced, alpha, 0)
        
        return blended
    
    def generate_frames(self):
        self.running = True
        self.picam2.start()
        
        try:
            while self.running:
                # Capture a frame
                frame = self.picam2.capture_array()
                
                # Process the frame for document optimization
                processed_frame = self.process_frame(frame)
                
                # Encode to JPEG with high quality (95%)
                ret, jpeg = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                if not ret:
                    continue
                    
                # Yield the frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                
                # Control frame rate
                time.sleep(1/self.framerate)
                
        except Exception as e:
            logging.error(f"Error in frame generation: {e}")
        finally:
            self.picam2.stop()
            self.running = False
    
    def stop(self):
        self.running = False
        if self.picam2:
            self.picam2.stop()

# Initialize Flask app
app = Flask(__name__)

# Initialize camera
document_camera = DocumentCamera(resolution=(1920, 1080), framerate=30)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video')
def video_feed():
    return Response(
        document_camera.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/adjust/<setting>')
def adjust_camera(setting):
    result = document_camera.adjust_settings(setting)
    return result

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000, threaded=True)
    except KeyboardInterrupt:
        document_camera.stop()
        logging.info("Application stopped")
    except Exception as e:
        logging.error(f"Application error: {e}")
        document_camera.stop()