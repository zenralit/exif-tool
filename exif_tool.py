import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif
import os

def dms_to_deg(dms, ref):
    deg = dms[0][0] / dms[0][1]
    min_ = dms[1][0] / dms[1][1]
    sec = dms[2][0] / dms[2][1]
    coord = deg + (min_ / 60.0) + (sec / 3600.0)
    if ref in ['S', 'W']:
        coord *= -1
    return coord

def get_metadata(path):
    exif_data = piexif.load(path)
    info = {}

 
    dt = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
    if dt:
        info["Дата и время"] = dt.decode()

 
    make = exif_data["0th"].get(piexif.ImageIFD.Make, b"").decode(errors="ignore")
    model = exif_data["0th"].get(piexif.ImageIFD.Model, b"").decode(errors="ignore")
    if make or model:
        info["Устройство"] = f"{make} {model}"


    gps_data = exif_data.get("GPS", {})
    if gps_data:
        try:
            lat = dms_to_deg(gps_data[2], gps_data[1].decode())
            lon = dms_to_deg(gps_data[4], gps_data[3].decode())
            info["GPS"] = f"{lat:.6f}, {lon:.6f}"
        except:
            info["GPS"] = "Ошибка парсинга"

   
    sw = exif_data["0th"].get(piexif.ImageIFD.Software, b"").decode(errors="ignore")
    if sw:
        info["Редактор"] = sw

    return info

def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.HEIC *.JPG *.MOV")])
    if not file_path:
        return

    info = get_metadata(file_path)
    text_output.delete(1.0, tk.END)
    for k, v in info.items():
        text_output.insert(tk.END, f"{k}: {v}\n")

    app.file_path = file_path

def wipe_exif():
    if not hasattr(app, 'file_path'):
        messagebox.showerror("Ошибка", "Сначала выберите изображение")
        return

    img = Image.open(app.file_path)
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)

    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Images", "*.jpg *.jpeg *.JPG *.MOV")])
    if save_path:
        img_no_exif.save(save_path)
        messagebox.showinfo("Готово", "Метаданные удалены и файл сохранён")

app = tk.Tk()
app.title("EXIF Viewer / Cleaner")

tk.Button(app, text="Открыть фото", command=choose_file).pack(pady=5)
tk.Button(app, text="Удалить метаданные", command=wipe_exif).pack(pady=5)

text_output = tk.Text(app, height=12, width=50)
text_output.pack(pady=5)

app.mainloop()

