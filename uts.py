from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np
import pytesseract
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Konfigurasi jalur tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Membuat jendela utama dengan tema dark
root = ttk.Window(themename="darkly")
root.geometry("800x600")
root.title("Image Processing and OCR")

# Variabel untuk menyimpan gambar
original_image = None
processed_image = None

title = Label(root, text='Ujian Tengah Semester\nPraktik Pengolahan Citra Digital')
title.pack()

# Fungsi untuk membuka dan menampilkan gambar
def get_image():
    global original_image, processed_image
    path = filedialog.askopenfilename(filetypes=[("Image File", '.jpg .jpeg .png')])
    if path:
        original_image = Image.open(path)
        processed_image = original_image.copy()  # Salin gambar asli
        display_image(processed_image)

# Fungsi untuk menampilkan gambar di jendela
def display_image(image):
    # Tentukan ukuran maksimum label untuk menampilkan gambar
    max_width, max_height = 600, 400  # Batas ukuran gambar
    image.thumbnail((max_width, max_height))  # Resize gambar dengan menjaga rasio aspek

    # Konversi gambar ke format Tkinter
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

# Fungsi untuk menerapkan grayscale
def apply_grayscale():
    global processed_image
    if processed_image is None:
        print("No image loaded!")
        return
    processed_image = ImageOps.grayscale(processed_image)
    display_image(processed_image)

# Fungsi untuk menerapkan dilasi
def apply_dilation():
    global processed_image
    if processed_image is None:
        print("No image loaded!")
        return
    cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2BGR)
    kernel = np.ones((5, 5), np.uint8)
    dilated_image = cv2.dilate(cv_image, kernel, iterations=1)
    processed_image = Image.fromarray(cv2.cvtColor(dilated_image, cv2.COLOR_BGR2RGB))
    display_image(processed_image)

# Fungsi untuk menerapkan erosi
def apply_erosion():
    global processed_image
    if processed_image is None:
        print("No image loaded!")
        return
    cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2BGR)
    kernel = np.ones((5, 5), np.uint8)
    eroded_image = cv2.erode(cv_image, kernel, iterations=1)
    processed_image = Image.fromarray(cv2.cvtColor(eroded_image, cv2.COLOR_BGR2RGB))
    display_image(processed_image)

# Fungsi untuk menerapkan deteksi tepi (Canny)
def apply_edge_detection():
    global processed_image
    if processed_image is None:
        print("No image loaded!")
        return
    cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(cv_image, 100, 200)
    processed_image = Image.fromarray(edges)
    display_image(processed_image)

# Fungsi untuk melakukan OCR
def apply_ocr():
    global processed_image
    if processed_image is None:
        print("No image loaded!")
        return
    try:
        text = pytesseract.image_to_string(processed_image.convert("RGB"))
        ocr_result_text.delete(1.0, END)  # Hapus hasil sebelumnya
        ocr_result_text.insert(END, text)  # Masukkan hasil OCR baru
    except Exception as e:
        print("Error during OCR:", e)

# Fungsi untuk mereset gambar ke kondisi awal
def reset_image():
    global processed_image
    if original_image:
        processed_image = original_image.copy()  # Reset ke gambar asli
        display_image(processed_image)

# Elemen antarmuka
image_label = ttk.Label(root, style="primary.TLabel")
image_label.place(relx=0.5, rely=0.3, anchor=CENTER)  # Tempatkan label di tengah atas

# Hasil OCR
result_label = ttk.Label(root, text="OCR Result:", style="primary.TLabel")
result_label.place(x=200, y=420)
ocr_result_text = ttk.Text(root, height=10, width=50)
ocr_result_text.place(x=200, y=450)

# Tombol-tombol
ttk.Button(root, text="Get Image", command=get_image).place(x=50, y=50)
ttk.Button(root, text="Grayscale", command=apply_grayscale).place(x=50, y=100)
ttk.Button(root, text="Dilation", command=apply_dilation).place(x=50, y=150)
ttk.Button(root, text="Erosion", command=apply_erosion).place(x=50, y=200)
ttk.Button(root, text="Edge Detection", command=apply_edge_detection).place(x=50, y=250)
ttk.Button(root, text="Segment (OCR)", command=apply_ocr).place(x=50, y=300)
ttk.Button(root, text="Reset", command=reset_image).place(x=50, y=350)

root.mainloop()