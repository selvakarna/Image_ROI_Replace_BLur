"""
main_gui.py  – v2
• Upload PDF or image.
• If Logo-mode chosen:
    – Every PDF page saved in current working directory
      as  <pdfname>_pageNNN.png
    – User picks a page, edits logo, saves as *_logo.png
      Repeats until user quits.
• If Blur-mode chosen:
    – Normal keyword / address blur workflow.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import os
from Blurkey import process_file, load_pages
from logo_editor import launch_logo_editor

# ─────────── Globals & LED helpers ────────────
selected_file_path = None
processing = False
blink_on  = True

def set_led(color, blink=False):
    global blink_on
    led_canvas.itemconfig(led_circle, fill=color)
    if blink:
        blink_on = True
        blink_led(color)

def blink_led(color):
    global blink_on
    if processing:
        led_canvas.itemconfig(led_circle, fill=color if blink_on else "gray")
        blink_on = not blink_on
        root.after(500, lambda: blink_led(color))

def reset_ui():
    global selected_file_path
    selected_file_path = None
    lbl_file.config(text="No file selected")
    txt_keywords.delete("1.0", tk.END)
    set_led("gray")

# ─────────── Upload & choose mode ────────────
def upload_file():
    """Handle file selection and branch to logo-mode or blur-mode."""
    global selected_file_path
    path = filedialog.askopenfilename(
        title="Select PDF or Image",
        filetypes=[("PDF or Image files", "*.pdf *.jpg *.jpeg *.png *.tiff")])
    if not path:
        return

    selected_file_path = path
    lbl_file.config(text=os.path.basename(path))

    # Ask which mode
    logo_mode = messagebox.askyesno(
        "Choose Processing Mode",
        "Logo Replace mode?\nYes → logo editor   |   No → blur/replace keywords")

    if logo_mode:
        iterative_logo_flow(path)
        reset_ui()
    # else: stay on GUI for keyword blur

# ─────────── Iterative logo flow ────────────
def iterative_logo_flow(src_path):
    """
    • Save every PDF page as PNG in CWD (or take single image).
    • Let user keep picking images until they quit.
    """
    # Prepare list of images in current dir
    cwd = os.getcwd()
    candidate_images = []

    if src_path.lower().endswith(".pdf"):
        base = os.path.splitext(os.path.basename(src_path))[0]
        pages = load_pages(src_path)
        for idx, page in enumerate(pages, 1):
            img_name = f"{base}_page{idx:03}.png"
            img_path = os.path.join(cwd, img_name)
            if not os.path.exists(img_path):   # avoid re-writing if it exists
                import cv2
                cv2.imwrite(img_path, page)
            candidate_images.append(img_path)
    else:
        candidate_images.append(src_path)

    # Iterative editing loop
    while True:
        img = filedialog.askopenfilename(
            title="Choose image for logo editing",
            initialdir=cwd,
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not img:
            break

        out_path = launch_logo_editor(img)   # returns the saved file path (or None)
        if out_path:
            messagebox.showinfo("Saved",
                                f"Logo-added image saved as:\n{os.path.basename(out_path)}")

        cont = messagebox.askyesno("Continue?",
                                   "Edit another image from this PDF?")
        if not cont:
            break

# ─────────── Page list helper ────────────
def ask_page_numbers():
    s = simpledialog.askstring("Pages",
                               "Page numbers (comma-separated, blank = all):")
    if not s or s.strip() == "":
        return None
    try:
        pages = [int(x.strip()) for x in s.split(",") if x.strip()]
        if any(p < 1 for p in pages): raise ValueError
        return sorted(set(pages))
    except ValueError:
        messagebox.showerror("Invalid", "Enter e.g. 1,2,5")
        return ask_page_numbers()

# ─────────── Blur workflow ────────────
def run_process(address_mode=False):
    global processing
    if not selected_file_path:
        messagebox.showwarning("No File", "Upload a PDF or image first.")
        return

    keywords = [k.strip() for k in txt_keywords.get("1.0", tk.END).splitlines() if k.strip()]
    if not keywords:
        messagebox.showwarning("No Keywords", "Enter at least one keyword.")
        return

    try:
        processing = True
        set_led("green", blink=True)
        pages     = ask_page_numbers()
        mask_mode = mask_mode_var.get()

        process_file(selected_file_path, keywords,
                     mask_mode=mask_mode, page_numbers=pages,
                     address_mode=address_mode)

        set_led("blue")
        if not messagebox.askyesno("Done", "Processing finished. Another file?"):
            root.destroy()
        else:
            reset_ui()
    except Exception as e:
        set_led("red"); messagebox.showerror("Error", str(e))
    finally:
        processing = False

# ─────────── GUI layout ────────────
root = tk.Tk(); root.title("Document Processor"); root.geometry("520x520")

tk.Button(root, text="Upload PDF / Image", width=30,
          command=upload_file).pack(pady=10)

lbl_file = tk.Label(root, text="No file selected", fg="gray"); lbl_file.pack()

tk.Label(root, text="Enter Keywords (one per line):").pack(pady=(10,0))
txt_keywords = tk.Text(root, height=6, width=54); txt_keywords.pack()

frame = tk.Frame(root); frame.pack(pady=10)
tk.Label(frame, text="Mask Mode:").grid(row=0, column=0, padx=(0,5))
mask_mode_var = tk.StringVar(value="blur")
mask_mode_menu = ttk.Combobox(frame, textvariable=mask_mode_var,
                              values=["blur", "replace"],
                              state="readonly", width=11)
mask_mode_menu.grid(row=0, column=1)

led_canvas = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=0)
led_circle = led_canvas.create_oval(2,2,18,18, fill="gray"); led_canvas.grid(row=0,column=2,padx=(10,0))

tk.Button(root, text="Address Blur", width=20,
          bg="#2196F3", fg="white",
          command=lambda: run_process(address_mode=True)).pack(pady=(15,5))
tk.Button(root, text="Generic Blur", width=20,
          bg="#4CAF50", fg="white",
          command=lambda: run_process(address_mode=False)).pack(pady=5)

root.mainloop()
