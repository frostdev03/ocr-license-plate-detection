from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
import cv2
import numpy as np
import easyocr
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Dark mode window
root = ttk.Window(themename="darkly")
root.geometry("1000x600")
root.title("Image Processing and OCR with Camera")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

font_path = "arial.ttf"
font_size = 30
font = ImageFont.truetype(font_path, font_size)

# Kamera
cap = cv2.VideoCapture(0)
camera_mode = True  # Mode default adalah kamera langsung

# EasyOCR Reader instance
reader = easyocr.Reader(['en', 'id'])

# Label untuk total confidence
confidence_label = ttk.Label(root, text="Total Confidence: N/A", font=("Helvetica", 12), anchor="e", foreground="white")
confidence_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

# Citra
original_image = None
processed_image = None
zoom_factor = 1.0

# Fungsi untuk menampilkan gambar
def display_image(image):
    image.thumbnail((640, 480))  # Menyesuaikan ukuran tampilan dengan ukuran kamera
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

# Fungsi untuk menangkap dan menampilkan frame dari kamera
def show_camera():
    global processed_image
    if not camera_mode:  # Jika mode kamera dimatikan, hentikan update frame
        return

    ret, frame = cap.read()
    if ret:
        # Convert frame BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_image = Image.fromarray(frame)
        display_image(processed_image)
    
    root.after(10, show_camera)  # Update setiap 10 ms

# Fungsi untuk mengganti mode antara kamera langsung dan citra statis
def toggle_camera():
    global camera_mode, processed_image
    camera_mode = not camera_mode
    if camera_mode:
        show_camera()
    else:
        # Ambil frame terakhir untuk pengolahan
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed_image = Image.fromarray(frame)
            display_image(processed_image)

# Fungsi pemrosesan citra menggunakan slider
def update_processing():
    global original_image, processed_image
    if original_image:
        # Convert ke grayscale
        cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2GRAY)

        # Adaptive Threshold
        binary_image = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 11, 2)

        # Noise removal
        ksize = int(noise_slider.get())
        if ksize % 2 == 0:
            ksize += 1
        noise_removed = cv2.medianBlur(binary_image, ksize)

        # Dilation dan Erosion
        kernel_size = int(dilation_slider.get())
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        dilated = cv2.dilate(noise_removed, kernel, iterations=1)

        kernel_size_erosion = int(erosion_slider.get())
        kernel_erosion = np.ones((kernel_size_erosion, kernel_size_erosion), np.uint8)
        eroded = cv2.erode(dilated, kernel_erosion, iterations=1)

        processed_image = Image.fromarray(eroded)
        display_image(processed_image)

# OCR menggunakan EasyOCR
def apply_ocr():
    global processed_image
    if processed_image:
        processed_array = np.array(processed_image.convert('RGB'))
        results = reader.readtext(processed_array)
        draw = ImageDraw.Draw(processed_image)

        total_confidence = 0
        for (bbox, text, confidence) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # Tambahkan confidence ke total
            total_confidence += confidence

            # Gambar kotak dan teks
            draw.rectangle([top_left, bottom_right], outline="red", width=3)
            draw.text(top_left, f"{text} ({confidence:.2f})", fill="red", font=font)

        # Tampilkan total confidence
        confidence_label.config(text=f"Total Confidence: {total_confidence:.2f}")
        display_image(processed_image)

# Reset gambar ke aslinya
def reset_image():
    global processed_image
    if processed_image:
        display_image(processed_image)

# Elemen GUI
title = ttk.Label(
    root,
    text="               PRAKTIK PENGOLAHAN CITRA DIGITAL\nDETEKSI KARAKTER PADA PLAT NOMOR KENDARAAN",
    style="primary.TLabel",
    font=("Helvetica", 14, "bold"),
    anchor="center",
    foreground="white"
)
title.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

# Frame untuk gambar
image_frame = ttk.LabelFrame(root, text="Image Display", style="primary.TLabelframe")
image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

# Frame untuk slider dan tombol (di sisi kanan)
slider_frame = ttk.Frame(root)
slider_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
slider_frame.columnconfigure(0, weight=1)

# Slider untuk parameter
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

ttk.Button(slider_frame, text="Toggle Camera", command=toggle_camera, width=15).grid(pady=10)
ttk.Button(slider_frame, text="Identify", command=apply_ocr, width=15).grid(pady=5)
ttk.Button(slider_frame, text="Reset", command=reset_image, width=15).grid(pady=5)

# Jalankan kamera
show_camera()

# Main loop
root.mainloop()
