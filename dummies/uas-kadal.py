from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import cv2
import numpy as np
import easyocr
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime
import re

# Dark mode window
root = ttk.Window(themename="darkly")
root.geometry("1000x600")
root.title("Image Processing and OCR with Camera")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# Maximize the window
root.wm_state('zoomed')

font_path = "arial.ttf"
font_size = 20
font = ImageFont.truetype(font_path, font_size)

# Camera
cap = cv2.VideoCapture(0)
camera_mode = True  # Default mode is live camera

# EasyOCR Reader instance
reader = easyocr.Reader(['en'])

# Images
original_image = None
processed_image = None

# Function to display image
# def display_image(image):
#     image.thumbnail((image_frame.winfo_width(), image_frame.winfo_height()))
#     tk_image = ImageTk.PhotoImage(image)
#     image_label.config(image=tk_image)
#     image_label.image = tk_image

def display_image(image):
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

# Function to capture and display camera frame
# def show_camera():
#     global processed_image
#     if not camera_mode:
#         return

#     ret, frame = cap.read()
#     if ret:
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         processed_image = Image.fromarray(frame)
#         display_image(processed_image)
    
#     root.after(10, show_camera)

def show_camera():
    global processed_image
    if not camera_mode:
        return

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get the current size of the image_frame
        frame_width = image_frame.winfo_width()
        frame_height = image_frame.winfo_height()
        
        # Resize the frame to fit the image_frame
        frame = cv2.resize(frame, (frame_width, frame_height))
        
        processed_image = Image.fromarray(frame)
        display_image(processed_image)
    
    root.after(10, show_camera)

# Function to capture image from camera
# def capture_image():
#     global original_image, processed_image, camera_mode
#     ret, frame = cap.read()
#     if ret:
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         original_image = Image.fromarray(frame)
#         processed_image = original_image.copy()
#         camera_mode = False
#         display_image(processed_image)

def capture_image():
    global original_image, processed_image, camera_mode
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get the current size of the image_frame
        frame_width = image_frame.winfo_width()
        frame_height = image_frame.winfo_height()
        
        # Resize the captured frame to fit the image_frame
        frame = cv2.resize(frame, (frame_width, frame_height))
        
        original_image = Image.fromarray(frame)
        processed_image = original_image.copy()
        camera_mode = False
        display_image(processed_image)

# Function for image processing using sliders
def update_processing():
    global original_image, processed_image
    if original_image:
        cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2GRAY)
        _, binary_image = cv2.threshold(cv_image, int(threshold_slider.get()), 255, cv2.THRESH_BINARY)

        ksize = int(noise_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        noise_removed = cv2.medianBlur(binary_image, ksize)

        kernel_size = int(dilation_slider.get())
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated = cv2.dilate(noise_removed, kernel, iterations=1)

        kernel_size_erosion = int(erosion_slider.get())
        kernel_erosion = np.ones((kernel_size_erosion, kernel_size_erosion), np.uint8)
        eroded = cv2.erode(dilated, kernel_erosion, iterations=1)

        processed_image = Image.fromarray(eroded)
        display_image(processed_image)

# OCR using EasyOCR
# def apply_ocr():
#     global processed_image
#     if processed_image:
#         processed_array = np.array(processed_image.convert('RGB'))
#         results = reader.readtext(processed_array)
#         draw = ImageDraw.Draw(processed_image)

#         for (bbox, text, confidence) in results:
#             (top_left, top_right, bottom_right, bottom_left) = bbox
#             top_left = tuple(map(int, top_left))
#             bottom_right = tuple(map(int, bottom_right))

#             draw.rectangle([top_left, bottom_right], outline="red", width=3)
#             draw.text(top_left, text, fill="red", font=font)
        
#         # Display last confidence in the bottom right corner
#         if results:
#             last_confidence = results[-1][2]
#             draw.text(
#                 (processed_image.width - 200, processed_image.height - 50),
#                 f"Confidence: {last_confidence:.2f}",
#                 fill="white",
#                 font=font
#             )
#         display_image(processed_image)

def apply_ocr():
    global processed_image
    if processed_image:
        processed_array = np.array(processed_image.convert('RGB'))
        results = reader.readtext(processed_array)
        draw = ImageDraw.Draw(processed_image)

        expiration_date = None
        for (bbox, text, confidence) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            draw.rectangle([top_left, bottom_right], outline="red", width=3)
            draw.text(top_left, text, fill="red", font=font)

            # Check if the text matches the expiration date format (XX.XX)
            if re.match(r'\d{2}\\d{2}', text):
                expiration_date = text

        if expiration_date:
            # Convert the expiration date string to a datetime object
            exp_year, exp_month = map(int, expiration_date.split('.'))
            exp_date = datetime.date(2000 + exp_year, exp_month, 1)

            # Get the current date
            today = datetime.date.today()

            # Calculate the expiration status
            if exp_date < today:
                expiration_status = f"Expired {(today - exp_date).days} days ago"
            else:
                expiration_status = f"Valid for {(exp_date - today).days} more days"

            # Display the expiration status
            draw.text((processed_image.width - 200, processed_image.height - 100), expiration_status, fill="white", font=font)

        display_image(processed_image)

# Reset image to original
def reset_image():
    global processed_image
    if original_image:
        processed_image = original_image.copy()
        display_image(processed_image)

# GUI Elements
title = ttk.Label(
    root,
    text="               PRAKTIK PENGOLAHAN CITRA DIGITAL\nDETEKSI KARAKTER PADA PLAT NOMOR KENDARAAN",
    style="primary.TLabel",
    font=("Helvetica", 14, "bold"),
    anchor="center",
    foreground="white"
)
title.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

image_frame = ttk.LabelFrame(root, text="Image Display", style="primary.TLabelframe")
image_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

slider_frame = ttk.Frame(root)
slider_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
slider_frame.columnconfigure(0, weight=1)

ttk.Label(slider_frame, text="Threshold (0-255):").grid(pady=5, sticky="w")
threshold_slider = ttk.Scale(slider_frame, from_=0, to=255, orient=HORIZONTAL, command=lambda e: update_processing())
threshold_slider.set(127)
threshold_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Noise Removal (Blur Kernel):").grid(pady=5, sticky="w")
noise_slider = ttk.Scale(slider_frame, from_=1, to=15, orient=HORIZONTAL, command=lambda e: update_processing())
noise_slider.set(3)
noise_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Dilation Kernel (1-10):").grid(pady=5, sticky="w")
dilation_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
dilation_slider.set(3)
dilation_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Erosion Kernel (1-10):").grid(pady=5, sticky="w")
erosion_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
erosion_slider.set(3)
erosion_slider.grid(pady=5, sticky="ew")

ttk.Button(slider_frame, text="Capture", command=capture_image, width=15).grid(pady=10)
ttk.Button(slider_frame, text="Identify", command=apply_ocr, width=15).grid(pady=5)
ttk.Button(slider_frame, text="Reset", command=reset_image, width=15).grid(pady=5)

show_camera()
root.mainloop()