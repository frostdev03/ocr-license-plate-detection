from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
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
root.title("Deteksi Karakter pada Plat Nomor Kendaraan")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# Maximize the window
root.wm_state('zoomed')

# Fonts
font_path = "C:/Windows/Fonts/arial.ttf"  # Ganti sesuai dengan sistem Anda
font_size = 20
font = ImageFont.truetype(font_path, font_size)

fsize_bbox = 35
fbbox = ImageFont.truetype(font_path, fsize_bbox)

# Camera
cap = cv2.VideoCapture(0)
camera_mode = True  # Default mode is live camera

# EasyOCR Reader instance
reader = easyocr.Reader(['en','id'])

# Images
original_image = None
processed_image = None

error_message = None

# Function to display image
def display_image(image):
    # Resize image to fit image_frame
    frame_width = image_frame.winfo_width()
    frame_height = image_frame.winfo_height()
    resized_image = image.resize((frame_width, frame_height), Image.Resampling.LANCZOS)
    
    if error_message:
        draw = ImageDraw.Draw(resized_image)
        font_error = ImageFont.truetype(font_path, 15)
        draw.text((10, frame_height - 30), error_message, fill="red", font=font_error)
    
    tk_image = ImageTk.PhotoImage(resized_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image


# Function to capture and display camera frame
def show_camera():
    global processed_image, error_message
    if not camera_mode:
        return

    try:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_width = image_frame.winfo_width()
            frame_height = image_frame.winfo_height()
            frame = cv2.resize(frame, (frame_width, frame_height))
            processed_image = Image.fromarray(frame)
            error_message = None  # Reset error jika tidak ada kesalahan
            display_image(processed_image)
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Debugging ke konsol

    if camera_mode:
        root.after(10, show_camera)

# Function to capture image from camera

def capture_image():
    global original_image, processed_image, camera_mode, error_message
    try:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_width = image_frame.winfo_width()
            frame_height = image_frame.winfo_height()
            frame = cv2.resize(frame, (frame_width, frame_height))
            original_image = Image.fromarray(frame)
            processed_image = original_image.copy()
            camera_mode = False
            error_message = None  # Reset error jika tidak ada kesalahan
            display_image(processed_image)
    except Exception as e:
        error_message = f"Error: {str(e)}"

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

# Improved OCR logic
def apply_ocr():
    global processed_image
    try:
        if processed_image:
            # Convert to array and process OCR
            processed_array = np.array(processed_image)
            results = reader.readtext(processed_array)
            draw_image = Image.fromarray(processed_array).convert('RGB')
            draw = ImageDraw.Draw(draw_image)

            # Debugging: Print results to console
            print("OCR Results:")
            confidences = []  # To store all confidence values
            expiration_date = None

            for bbox, text, confidence in results:
                print(f"Text: {text}, Confidence: {confidence}")
                confidences.append(confidence)  # Append confidence to the list
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = tuple(map(int, top_left))
                bottom_right = tuple(map(int, bottom_right))
                
                draw.rectangle([top_left, bottom_right], outline="green", width=3)
                draw.text(top_left, text, fill="green", font=fbbox)

                # Clean text and look for date-like patterns
                text_cleaned = text.replace(" ", "").replace(".", "").replace(",", "").replace("'", "")
                match = re.match(r'(\d{2})(\d{2})$', text_cleaned)  # Match last 4 digits as MMYY
                if match:
                    expiration_date = match.groups()

            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Display confidence on the image
            confidence_text = f"Accuracy: {avg_confidence * 100:.2f}%"
            draw.text(
                (processed_image.width - 200, 10),  # Top-right corner
                confidence_text,
                fill="green",
                font=ImageFont.truetype("arial.ttf", size=25)  # Larger font size
            )

            if expiration_date:
                # Parse year and month from matched text
                exp_month, exp_year_suffix = map(int, expiration_date)
                exp_year = 2000 + exp_year_suffix  # Convert 2-digit year to 4-digit year
                exp_date = datetime.date(exp_year, exp_month, 1)

                # Get the current date
                today = datetime.date.today()

                # Calculate the expiration status
                if exp_date < today:
                    expiration_status = f"Expired {(today - exp_date).days} days ago"
                else:
                    expiration_status = f"Valid for {(exp_date - today).days} more days"

                # Print expiration status to console
                print(f"Expiration Status: {expiration_status}")

                # Display the expiration date and status on the image
                draw.text((20, processed_image.height - 100), f"Exp Date: {exp_month:02}/{exp_year}", fill="green", font=fbbox)
                draw.text((20, processed_image.height - 70), expiration_status, fill="green", font=fbbox)
            else:
                # If no valid date was detected
                print("No valid expiration date detected.")
                draw.text((20, processed_image.height - 90), "No valid expiration date detected.", fill="green", font=fbbox)

            # Update the GUI with processed image
                processed_image = draw_image
                error_message = None  # Reset error jika tidak ada kesalahan
                display_image(processed_image)
    except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)  # Debugging ke konsol

# Reset all sliders to 0
def reset_sliders():
    threshold_slider.set(0)
    noise_slider.set(1)
    dilation_slider.set(1)
    erosion_slider.set(1)

# Reset image to original
def reset_image():
    global processed_image, camera_mode
    reset_sliders()  # Reset all sliders to 0
    if original_image:
        # Reset to the captured image
        processed_image = original_image.copy()
        display_image(processed_image)
        print("Reset to captured image")
    else:
        # Return to live camera mode
        camera_mode = True
        print("Reset to live camera")
        show_camera()

def live_camera_mode():
    """Reset everything and return to live camera mode."""
    global camera_mode, processed_image
    reset_sliders()  # Reset sliders
    camera_mode = True  # Reactivate live camera mode
    processed_image = None  # Clear the processed image
    show_camera()  # Start showing live camera feed

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

image_frame = ttk.LabelFrame(root, text="Image Display", style="primary.TLabelframe", width=600, height=400)
image_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

root.update_idletasks()  # Pastikan ukuran diatur sebelum gambar pertama ditampilkan
# image_frame.config(width=400, height=400)  # Sesuaikan dengan ukuran frame yang Anda tentukan

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

slider_frame = ttk.Frame(root)
slider_frame.grid(row=1, column=2, padx=35, pady=5, sticky="nsew")
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

ttk.Button(slider_frame, text="Capture", command=capture_image, width=20).grid(pady=10)
ttk.Button(slider_frame, text="Identify", command=apply_ocr, width=20).grid(pady=10)
ttk.Button(slider_frame, text="Reset Processing", command=reset_image, width=20).grid(pady=10)
ttk.Button(slider_frame, text="Reset Camera", command=live_camera_mode, width=20).grid(pady=10)

# Start sliders at 0 when the program is run
threshold_slider.set(0)
noise_slider.set(1)
dilation_slider.set(1)
erosion_slider.set(1)

# Start camera feed
show_camera()
root.mainloop()