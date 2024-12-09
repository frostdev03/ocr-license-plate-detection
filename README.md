# Vehicle License Plate Character Detection

This is a Python-based application for detecting characters on vehicle license plates using **Tkinter**, **OpenCV**, **EasyOCR**, and **ttkbootstrap**. The application enables real-time processing of camera feeds or static images and displays recognized characters with confidence levels.

---

## Features

- **Real-Time Camera Feed**: Display live video feed from the camera.
- **Character Recognition**: Detect and identify text on license plates using EasyOCR.
- **Image Processing**: Apply thresholding, noise removal, dilation, and erosion to enhance image quality.
- **Confidence Display**: Shows OCR accuracy and overlays the recognized text on the image.
- **Reset Options**: Reset sliders or return to live camera mode for quick adjustments.

---

## Prerequisites

- Python 3.8 or later
- Required libraries:
  - `ttkbootstrap`
  - `Pillow`
  - `OpenCV` (`cv2`)
  - `numpy`
  - `EasyOCR`

Install the dependencies via pip:

```bash
pip install ttkbootstrap pillow opencv-python-headless numpy easyocr
```

---

## Usage

1. **Run the Application**:
   ```bash
   python license-detection-easy-ocr.py
   ```

2. **Application Interface**:
   - **Live Camera Feed**: The application starts in camera mode, displaying the live feed.
   - **Capture Image**: Click the **Capture** button to freeze the current camera frame.
   - **Image Processing**: Use sliders to adjust thresholding, noise removal, dilation, and erosion to enhance the image.
   - **OCR**: Click the **Identify** button to detect characters on the processed image.
   - **Reset**: Reset the image or return to live camera mode as needed.

3. **OCR Results**:
   - The recognized text is displayed on the image along with its confidence level.
   - If date patterns are detected, the expiration status is calculated and displayed.

---


## Screenshots

![WhatsApp Image 2024-12-08 at 2 50 46 PM](https://github.com/user-attachments/assets/c30a0f7c-346f-4b65-970f-461dddeb6bdf)

---

## Troubleshooting

- **Camera Issues**: Ensure your device camera is functional and accessible.
- **Text Detection Errors**: Adjust sliders to improve text visibility for OCR.
- **Font Path Error**: Update the `font_path` variable in the script to match your system.

---

## Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition.
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/) for the stylish user interface.
- [OpenCV](https://opencv.org/) for image processing.
```
Cheers
