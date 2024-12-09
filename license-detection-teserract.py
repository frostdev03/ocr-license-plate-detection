from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np
import pytesseract
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# path ocr
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# dark mode
root = ttk.Window(themename="darkly")
root.geometry("800x600")
root.title("Image Processing and OCR")
root.columnconfigure(1, weight=1)  # Kolom untuk gambar dan hasil teks menjadi fleksibel
root.rowconfigure(1, weight=1)

# citra
original_image = None
processed_image = None

# Fungsi untuk menampilkan gambar
def display_image(image):
    # Resize agar sesuai dengan frame
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
        processed_image = original_image.copy()  # Salin gambar asli
        display_image(processed_image)

# Fungsi untuk berbagai pemrosesan
def apply_grayscale():
    global processed_image
    if processed_image:
        processed_image = ImageOps.grayscale(processed_image)
        display_image(processed_image)

def apply_dilation():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2BGR)
        kernel = np.ones((5, 5), np.uint8)
        dilated_image = cv2.dilate(cv_image, kernel, iterations=1)
        processed_image = Image.fromarray(cv2.cvtColor(dilated_image, cv2.COLOR_BGR2RGB))
        display_image(processed_image)

def apply_erosion():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2BGR)
        kernel = np.ones((5, 5), np.uint8)
        eroded_image = cv2.erode(cv_image, kernel, iterations=1)
        processed_image = Image.fromarray(cv2.cvtColor(eroded_image, cv2.COLOR_BGR2RGB))
        display_image(processed_image)

def apply_edge_detection():
    global processed_image
    if processed_image:
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(cv_image, 100, 200)
        processed_image = Image.fromarray(edges)
        display_image(processed_image)

def apply_ocr():
    global processed_image
    if processed_image:
        text = pytesseract.image_to_string(processed_image.convert("RGB"))
        ocr_result_text.delete(1.0, END)
        ocr_result_text.insert(END, text)

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
ttk.Button(button_frame, text="Dilation", command=apply_dilation, width=15).grid(pady=5)
ttk.Button(button_frame, text="Erosion", command=apply_erosion, width=15).grid(pady=5)
ttk.Button(button_frame, text="Edge Detection", command=apply_edge_detection, width=15).grid(pady=5)
ttk.Button(button_frame, text="Segment (OCR)", command=apply_ocr, width=15).grid(pady=5)
ttk.Button(button_frame, text="Reset", command=reset_image, width=15).grid(pady=5)

# Frame untuk hasil OCR
ocr_frame = ttk.LabelFrame(root, text="OCR Result", style="primary.TLabelframe")
ocr_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
ocr_result_text = ttk.Text(ocr_frame, height=5)
ocr_result_text.pack(expand=True, fill=BOTH)

root.mainloop()