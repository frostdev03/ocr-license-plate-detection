from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps, ImageDraw
import cv2
import numpy as np
import easyocr
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Dark mode window
root = ttk.Window(themename="darkly")
root.geometry("1000x600")
root.title("Image Processing and OCR with Sliders")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# EasyOCR Reader instance
reader = easyocr.Reader(['en'])  # Bisa ditambah bahasa lain seperti ['en', 'id']

# Citra
original_image = None
processed_image = None

# Fungsi untuk menampilkan gambar
def display_image(image):
    image.thumbnail((image_frame.winfo_width(), image_frame.winfo_height()))
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

# Fungsi untuk membuka gambar
def get_image():
    global original_image, processed_image
    path = filedialog.askopenfilename(filetypes=[("Image File", '.jpg .jpeg .png')])
    if path:
        original_image = Image.open(path)
        processed_image = original_image.copy()
        display_image(processed_image)

# Fungsi pemrosesan citra menggunakan slider
def update_processing():
    global original_image, processed_image
    if original_image:
        cv_image = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2GRAY)

        # Threshold
        _, binary_image = cv2.threshold(cv_image, int(threshold_slider.get()), 255, cv2.THRESH_BINARY)
        
        # Noise removal (Median Blur)
        ksize = int(noise_slider.get())
        if ksize % 2 == 0:  # Pastikan ksize ganjil
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

# OCR menggunakan EasyOCR
def apply_ocr():
    global processed_image
    if processed_image:
        # Konversi gambar ke numpy array
        processed_array = np.array(processed_image.convert('RGB'))
        
        # Deteksi teks menggunakan EasyOCR
        results = reader.readtext(processed_array)
        
        # Menampilkan bounding box dan teks pada gambar
        draw = ImageDraw.Draw(processed_image)
        for (bbox, text, _) in results:
            # Bounding box koordinat
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            
            # Gambar bounding box
            draw.rectangle([top_left, bottom_right], outline="red", width=2)
            
            # Teks di atas kotak
            draw.text(top_left, text, fill="red")
        
        display_image(processed_image)

# Reset gambar ke aslinya
def reset_image():
    global processed_image
    if original_image:
        processed_image = original_image.copy()
        display_image(processed_image)

# Elemen GUI
title = ttk.Label(
    root,
    text="PRAKTIK PENGOLAHAN CITRA DIGITAL\nDETEKSI KARAKTER PADA PLAT NOMOR KENDARAAN",
    style="primary.TLabel",
    font=("Helvetica", 14, "bold"),
    anchor="center",
    foreground="white"
)
title.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

# Frame untuk gambar
image_frame = ttk.LabelFrame(root, text="Image Display", style="primary.TLabelframe")
image_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

# Frame untuk slider
slider_frame = ttk.Frame(root)
slider_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
slider_frame.columnconfigure(0, weight=1)

# Slider untuk parameter
ttk.Label(slider_frame, text="Threshold (0-255):").grid(pady=5, sticky="w")
threshold_slider = ttk.Scale(slider_frame, from_=0, to=255, orient=HORIZONTAL, command=lambda e: update_processing())
threshold_slider.set(127)
threshold_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Noise Removal (Blur Kernel):").grid(pady=5, sticky="w")
noise_slider = ttk.Scale(slider_frame, from_=1, to=15, orient=HORIZONTAL, command=lambda e: update_processing())
noise_slider.set(3)  # Default value
noise_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Dilation Kernel (1-10):").grid(pady=5, sticky="w")
dilation_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
dilation_slider.set(3)
dilation_slider.grid(pady=5, sticky="ew")

ttk.Label(slider_frame, text="Erosion Kernel (1-10):").grid(pady=5, sticky="w")
erosion_slider = ttk.Scale(slider_frame, from_=1, to=10, orient=HORIZONTAL, command=lambda e: update_processing())
erosion_slider.set(3)
erosion_slider.grid(pady=5, sticky="ew")

ttk.Button(slider_frame, text="Get Image", command=get_image, width=15).grid(pady=10)
ttk.Button(slider_frame, text="Segment (OCR)", command=apply_ocr, width=15).grid(pady=5)
ttk.Button(slider_frame, text="Reset", command=reset_image, width=15).grid(pady=5)

# Main loop
root.mainloop()
