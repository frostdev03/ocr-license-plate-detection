# License Plate Detection and OCR Application
![WhatsApp Image 2024-12-08 at 2 50 46 PM](https://github.com/user-attachments/assets/c30a0f7c-346f-4b65-970f-461dddeb6bdf)
This repository contains a Python-based GUI application for detecting characters on license plates using **image processing** and **Optical Character Recognition (OCR)**. The application is built using **Tkinter** for the interface, **OpenCV** for image processing, and **EasyOCR** for text recognition.

## Features
- **User-friendly GUI**: Built with Tkinter and TTKBootstrap for an enhanced dark-mode interface.
- **Image Processing Tools**:
  - Grayscale conversion
  - Threshold adjustment
  - Noise removal using median blur
  - Dilation and erosion
- **OCR Functionality**:
  - Recognize text on images of license plates
  - Display bounding boxes and detected text directly on the image
- **Interactive Controls**:
  - Zoom in and out
  - Real-time image adjustments with sliders
- **File Handling**:
  - Open images using a file dialog
  - Reset to original image after processing

## Technologies Used
- **Tkinter**: For creating the graphical user interface.
- **OpenCV**: For image processing operations such as grayscale conversion, thresholding, noise removal, and morphological transformations.
- **EasyOCR**: For Optical Character Recognition, supporting multiple languages.
- **Pillow**: For advanced image handling and display in the GUI.

## How to Use
1. **Install Required Libraries**:
   ```bash
   pip install opencv-python-headless easyocr pillow ttkbootstrap
   ```

2. **Run the Application**:
   ```bash
   python main.py (not final yet hehe)
   ```

3. **Usage**:
   - Click **"Get Image"** to select an image file.
   - Adjust the sliders for thresholding, noise removal, dilation, and erosion.
   - Click **"Identify"** to perform OCR and detect text.
   - Use **"Zoom In"** and **"Zoom Out"** for resizing the displayed image.
   - Click **"Reset"** to return to the original image.

## Interface Overview
- **Image Display**: Shows the loaded and processed images with bounding boxes for detected text.
- **Sliders**: Control parameters for image processing:
  - Thresholding (0-255)
  - Noise Removal (Kernel size for blur)
  - Dilation and Erosion (Kernel sizes for morphological transformations)
- **Buttons**:
  - `Get Image`: Open an image for processing.
  - `Identify`: Perform OCR and show detected text.
  - `Reset`: Revert to the original image.
  - `Zoom In` and `Zoom Out`: Adjust the image size.

## Future Enhancements
- Add support for video input (e.g., real-time OCR from a camera feed).
- Include more advanced image pre-processing techniques.
- Support additional OCR languages and fine-tune recognition accuracy.

Cheers
