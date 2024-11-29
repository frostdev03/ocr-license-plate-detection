from tkinter import *
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import cv2
import numpy as np
import easyocr
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Dark mode window
root = ttk.Window(themename="darkly")
root.geometry("1200x700")  # Initial window size
root.title("Image Processing and OCR with Camera")

# Grid configuration
root.columnconfigure(0, weight=2)  # Image display column larger
root.columnconfigure(1, weight=1)  # Slider and button column smaller
root.rowconfigure(1, weight=1)     # Main content row

font_path = "arial.ttf"
font_size = 30
font = ImageFont.truetype(font_path, font_size)

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
print(f"Default Camera resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

camera_mode = True  # Default mode is live camera

# EasyOCR Reader instance
reader = easyocr.Reader(['en', 'id'])

# Images
original_image = None
processed_image = None

# Function to display image
def display_image(image):
    image.thumbnail((800, 500))  # Adjust display size to camera resolution
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

# Function to capture and display camera frames
def show_camera():
    global processed_image
    if not camera_mode:  # If camera mode is off, stop updating frames
        return

    ret, frame = cap.read()
    if ret:
        # Convert frame BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_image = Image.fromarray(frame)
        display_image(processed_image)

    root.after(10, show_camera)  # Update every 10 ms

# Function to toggle between live camera and static image
def toggle_camera():
    global camera_mode, original_image
    camera_mode = not camera_mode
    if not camera_mode and processed_image:
        # Save the last frame from the camera to original_image
        original_image = processed_image.copy()
    if camera_mode:
        show_camera()

# Function to process the image using sliders
def update_processing():
    global original_image, processed_image
    if not original_image:
        return  # Do nothing if there's no image to process

    cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2GRAY)

    # Threshold
    _, binary_image = cv2.threshold(cv_image, int(threshold_slider.get()), 255, cv2.THRESH_BINARY)

    # Noise removal (Median Blur)
    ksize = int(noise_slider.get())
    if ksize % 2 == 0:
        ksize += 1
    noise_removed = cv2.medianBlur(binary_image, ksize)

    # Dilation and Erosion
    kernel_size = int(dilation_slider.get())
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated = cv2.dilate(noise_removed, kernel, iterations=1)

    kernel_size_erosion = int(erosion_slider.get())
    kernel_erosion = np.ones((kernel_size_erosion, kernel_size_erosion), np.uint8)
    eroded = cv2.erode(dilated, kernel_erosion, iterations=1)

    processed_image = Image.fromarray(eroded)
    display_image(processed_image)

# OCR using EasyOCR
def apply_ocr():
    global processed_image
    if processed_image:
        processed_array = np.array(processed_image.convert('RGB'))
        results = reader.readtext(processed_array)
        draw = ImageDraw.Draw(processed_image)
        for (bbox, text, confidence) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            draw.text(top_left, f"{text} ({confidence:.2f})", fill="red", font=font)
        display_image(processed_image)

# Reset image to original
def reset_image():
    global processed_image
    if original_image:
        processed_image = original_image.copy()
        display_image(processed_image)

# GUI elements
title = ttk.Label(
    root,
    text="PRAKTIK PENGOLAHAN CITRA DIGITAL\nDETEKSI KARAKTER PADA PLAT NOMOR KENDARAAN",
    style="primary.TLabel",
    font=("Helvetica", 14, "bold"),
    anchor="center",
    foreground="white"
)
title.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")  # Spanning two columns

# Image frame (no border)
image_frame = ttk.Frame(root)
image_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

# Slider and button frame (no border)
slider_frame = ttk.Frame(root)
slider_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
slider_frame.columnconfigure(0, weight=1)

# Sliders for parameters
ttk.Label(slider_frame, text="Threshold (0-255):").grid(row=0, column=0, pady=5, sticky="w")
threshold_slider = ttk.Scale(slider_frame, from_=0, to=255, orient=HORIZONTAL, command=lambda e: update_processing())
threshold_slider.set(127)
threshold_slider.grid(row=1, column=0, pady=5, sticky="ew")

ttk.Label(slider_frame, text="Noise Removal (Blur Kernel):").grid(row=2, column=0, pady=5, sticky="w")
noise_slider = ttk.Scale(slider_frame, from_=1, to=15, orient=HORIZONTAL, command=lambda e: update_processing())
noise_slider.set(3)
noise_slider.grid(row=3, column=0, pady=5, sticky="ew")

ttk.Label(slider_frame, text="Dilation Kernel (1-10):").grid(row=4, column=0, pady=5, sticky="w")
dilation_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
dilation_slider.set(3)
dilation_slider.grid(row=5, column=0, pady=5, sticky="ew")

ttk.Label(slider_frame, text="Erosion Kernel (1-10):").grid(row=6, column=0, pady=5, sticky="w")
erosion_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
erosion_slider.set(3)
erosion_slider.grid(row=7, column=0, pady=5, sticky="ew")

# Buttons
button_frame = ttk.Frame(slider_frame)
button_frame.grid(row=8, column=0, pady=10)

ttk.Button(button_frame, text="Toggle Camera", command=toggle_camera, width=15).grid(row=0, column=0, padx=5, sticky="ew")
ttk.Button(button_frame, text="Identify", command=apply_ocr, width=15).grid(row=0, column=1, padx=5, sticky="ew")
ttk.Button(button_frame, text="Reset", command=reset_image, width=15).grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

# Start the camera
show_camera()

# Main loop
root.mainloop()