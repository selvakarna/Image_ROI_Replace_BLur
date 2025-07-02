# Image_ROI_Replace_BLur
PDF-to-Image + Blur/Logo GUI Tool

1. Upload a File (PDF or Image)
You start the app.

Click “Upload PDF/Image” button.

Choose a PDF or image file from your computer.

2. If PDF → Convert to Images
If it’s a PDF, each page is converted to an image.

Images are saved to the same folder as main_gui.py.
❓ 3. Choose What to Do
A popup appears asking:

"Choose process mode:"

✅ Blur Mode: To detect and blur keywords or address

✅ Logo Replace Mode: To erase/replace a region and insert a logo
🧠 4. Depending on Mode:
👁️ A. Blur Mode
Enter keywords (like company name, address, etc.).

App will:

Use OCR to detect those words.

Blur or replace those regions on each page image.
🖼️ B. Logo Replace Mode
You manually:

Select a region on each image to erase.

Insert a logo in that area.

Process each page one by one.

After each page:


Saves every updated image with suffix like _logo.png.

📁 5. Output
Processed images (blurred or with logos) are saved in the current folder.

✅ Tools Used:
Tkinter: GUI interface.

OpenCV: Image processing (blur, ROI, logo).

PDF2Image: Converts PDF pages to images.

Pytesseract: OCR (to detect text in images).

NumPy: Image array handling.


