"""
Blurkey.py
----------
Keyword / address detection + blur/replace utilities.
Requires: opencv-python, pytesseract, pdf2image, pillow.
"""

import cv2, pytesseract, numpy as np
from pdf2image import convert_from_path
from typing import List, Optional

# ------------------------------------------------------------------ #
# 1. Load pages (PDF -> list of cv2 images)                           #
# ------------------------------------------------------------------ #
def load_pages(file_path: str):
    ext = file_path.lower()
    if ext.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
        return [cv2.imread(file_path)]
    if ext.endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=300)
        return [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in pages]
    raise ValueError("Unsupported file type")

# ------------------------------------------------------------------ #
# 2. Internal helper – mask ROI                                      #
# ------------------------------------------------------------------ #
def _mask_roi(img, x1, y1, x2, y2, *, mode="blur"):
    if mode == "blur":
        roi = cv2.GaussianBlur(img[y1:y2, x1:x2], (45,45), 0)
        img[y1:y2, x1:x2] = roi
    else:  # replace
        cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,255), -1)
        cv2.putText(img, "MASKED", (x1, y1+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

# ------------------------------------------------------------------ #
# 3. Keyword blur                                                    #
# ------------------------------------------------------------------ #
def detect_and_blur_entities(img, keywords: List[str], *, mode="blur"):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n = len(data["text"])
    keys = [k.lower().split() for k in keywords]

    i = 0
    while i < n:
        if not data["text"][i].strip():
            i += 1; continue
        matched = None
        for kw in keys:
            L = len(kw)
            if i+L <= n and kw == [data["text"][i+j].strip().lower() for j in range(L)]:
                matched = L; break
        if not matched:
            i += 1; continue

        box_x1 = min(data['left'][i+j] for j in range(matched))
        box_y1 = min(data['top'][i+j]  for j in range(matched))
        box_x2 = max(data['left'][i+j]+data['width'][i+j] for j in range(matched))
        box_y2 = max(data['top'][i+j] +data['height'][i+j] for j in range(matched))
        _mask_roi(img, box_x1, box_y1, box_x2, box_y2, mode=mode)
        i += matched
    return img

# ------------------------------------------------------------------ #
# 4. Address blur (keyword + N lines below)                           #
# ------------------------------------------------------------------ #
def detect_and_blur_address_entities(img, keywords: List[str], *,
                                     mode="blur", lines_below=4):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n       = len(data["text"])
    key_lc  = [k.lower() for k in keywords]

    # build line map
    line_to_indices = {}
    for idx in range(n):
        line_to_indices.setdefault(data['line_num'][idx], []).append(idx)
    sorted_lines = sorted(line_to_indices)

    for idx in range(n):
        if data["text"][idx].strip().lower() in key_lc:
            base_line = data['line_num'][idx]
            base_idx  = sorted_lines.index(base_line)
            target_lines = sorted_lines[base_idx: base_idx+lines_below+1]

            xs = [data['left'][j] for ln in target_lines for j in line_to_indices[ln]]
            ys = [data['top'][j]  for ln in target_lines for j in line_to_indices[ln]]
            ws = [data['width'][j] for ln in target_lines for j in line_to_indices[ln]]
            hs = [data['height'][j] for ln in target_lines for j in line_to_indices[ln]]

            x1, y1 = max(min(xs)-10,0), max(min(ys)-5,0)
            x2, y2 = min(max([x+w for x,w in zip(xs,ws)])+10, img.shape[1]), \
                     min(max([y+h for y,h in zip(ys,hs)])+5,  img.shape[0])
            _mask_roi(img, x1, y1, x2, y2, mode=mode)
            break
    return img

# ------------------------------------------------------------------ #
# 5. Entry point                                                     #
# ------------------------------------------------------------------ #
def process_file(file_path: str, keywords: List[str], *,
                 mask_mode="blur",
                 page_numbers: Optional[List[int]] = None,
                 address_mode=False):
    pages = load_pages(file_path)
    iterable = (enumerate(pages,1) if not page_numbers else
                [(i+1,p) for i,p in enumerate(pages) if i+1 in page_numbers])

    outputs=[]
    for page_no, img in iterable:
        if address_mode:
            out = detect_and_blur_address_entities(img, keywords, mode=mask_mode)
        else:
            out = detect_and_blur_entities(img, keywords, mode=mask_mode)
        out_path = f"output_page_{page_no}.jpg"
        cv2.imwrite(out_path, out); outputs.append(out_path)
    return outputs

__all__ = ["process_file", "load_pages"]
