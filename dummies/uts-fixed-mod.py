from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np
import pytesseract
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Path Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Dark mode window
root = ttk.Window(themename="darkly")
root.geometry("800x600")
root.title("Image Processing and OCR")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

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

# Pra-pengolahan citra
def apply_grayscale():
    global processed_image
    if processed_image:
        processed_image = ImageOps.grayscale(processed_image)
        display_image(processed_image)

def apply_threshold():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2GRAY)
        _, binary_image = cv2.threshold(cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_image = Image.fromarray(binary_image)
        display_image(processed_image)

def apply_noise_removal():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2GRAY)
        denoised_image = cv2.medianBlur(cv_image, 3)
        processed_image = Image.fromarray(denoised_image)
        display_image(processed_image)

def apply_resize(scale=2):
    global processed_image
    if processed_image:
        cv_image = np.array(processed_image)
        height, width = cv_image.shape[:2]
        resized_image = cv2.resize(cv_image, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)
        processed_image = Image.fromarray(resized_image)
        display_image(processed_image)

# Segmentasi wilayah plat nomor
def find_plate_area():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(cv_image, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > h and w > 50:  # Threshold lebar dan tinggi
                plate = cv_image[y:y + h, x:x + w]
                processed_image = Image.fromarray(plate)
                display_image(processed_image)
                break

# OCR
def apply_ocr():
    global processed_image
    if processed_image:
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(processed_image.convert("RGB"), config=custom_config)
        ocr_result_text.delete(1.0, END)
        ocr_result_text.insert(END, text)

# Reset gambar ke aslinya
def reset_image():
    global processed_image
    if original_image:
        processed_image = original_image.copy()
        display_image(processed_image)

# Elemen GUI
title = ttk.Label(root, text="            PRAKTIK PENGOLAHAN CITRA DIGITAL\nDETEKSI KARAKTER PADA PLAT NOMOR KENDARAAN", style="primary.TLabel", font=("Helvatica",10,"bold"))
title.grid(row=0, column=0, columnspan=3, pady=10)

# Frame untuk gambar
image_frame = ttk.LabelFrame(root, text="Image Display", style="primary.TLabelframe")
image_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
image_frame.rowconfigure(0, weight=1)
image_frame.columnconfigure(0, weight=1)

image_label = ttk.Label(image_frame)
image_label.grid(sticky="nsew")

# Frame untuk tombol
button_frame = ttk.Frame(root)
button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
button_frame.columnconfigure(0, weight=1)

ttk.Button(button_frame, text="Get Image", command=get_image, width=15).grid(pady=5)
ttk.Button(button_frame, text="Grayscale", command=apply_grayscale, width=15).grid(pady=5)
ttk.Button(button_frame, text="Thresholding", command=apply_threshold, width=15).grid(pady=5)
ttk.Button(button_frame, text="Noise Removal", command=apply_noise_removal, width=15).grid(pady=5)
ttk.Button(button_frame, text="Resize", command=lambda: apply_resize(scale=2), width=15).grid(pady=5)
ttk.Button(button_frame, text="Find Plate", command=find_plate_area, width=15).grid(pady=5)
ttk.Button(button_frame, text="Segment (OCR)", command=apply_ocr, width=15).grid(pady=5)
ttk.Button(button_frame, text="Reset", command=reset_image, width=15).grid(pady=5)

# Frame untuk hasil OCR
ocr_frame = ttk.LabelFrame(root, text="OCR Result", style="primary.TLabelframe")
ocr_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
ocr_result_text = ttk.Text(ocr_frame, height=5)
ocr_result_text.pack(expand=True, fill=BOTH)

# Main loop
root.mainloop()
