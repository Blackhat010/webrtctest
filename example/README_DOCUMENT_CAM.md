# Document Camera for Raspberry Pi

This README provides instructions for using the `document_cam.py` script, which is optimized for reading documents with a Raspberry Pi camera.

## Features

- **Higher Resolution**: Uses 1920x1080 resolution for clearer text
- **Enhanced Sharpness**: Increased sharpness settings for better text definition
- **Adaptive Contrast**: Improved contrast for better text visibility
- **Image Processing**: Uses adaptive thresholding to enhance text readability
- **Web Interface**: Simple controls to adjust camera settings in real-time
- **High-Quality JPEG**: Uses 95% JPEG quality to reduce compression artifacts

## Installation

```bash
pip install flask picamera2 opencv-python numpy
```

## Usage

1. Run the script:
   ```bash
   python document_cam.py
   ```

2. Access the camera feed in your browser:
   ```
   http://[raspberry-pi-ip]:8000
   ```

3. Use the web interface buttons to adjust settings for optimal document readability.

## Command Line Options for WebRTC

If you want to use this with the WebRTC implementation, you can optimize camera settings with these command-line parameters:

```bash
./pi-webrtc --camera=libcamera:0 --fps=30 --width=1920 --height=1080 --sharpness=5.0 --contrast=4.0 --brightness=0.2 --saturation=1.0 --denoise=cdn_off --hw-accel
```

## Improving Document Readability

For optimal document reading quality:

1. **Lighting**: Ensure even lighting across the document to avoid shadows
2. **Camera Position**: Position the camera directly above the document
3. **Focus**: For best results, keep the document flat and at a consistent distance from the camera
4. **Resolution**: Higher resolution (1920x1080 or better) provides clearer text
5. **Processing**: The adaptive thresholding in the script helps enhance text visibility

## Troubleshooting

- If text appears blurry, try increasing the sharpness setting
- If the document has low contrast, increase the contrast setting
- If the document appears too dark or too bright, adjust the brightness setting
- For color documents, you may want to increase the saturation slightly

## Comparison with Simple Implementation

Compared to the simple implementation provided in the original query, this solution offers:

1. Higher resolution (1920x1080 vs 1280x720)
2. Optimized camera parameters for document reading
3. Advanced image processing with adaptive thresholding
4. Higher JPEG quality (95% vs default)
5. Interactive web interface for adjusting settings
6. Proper error handling and resource management