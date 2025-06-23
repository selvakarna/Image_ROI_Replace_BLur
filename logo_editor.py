# """
# logo_editor.py  – returns output path of saved image
# """

# import cv2, numpy as np, os, tkinter as tk
# from tkinter import filedialog

# def _browse(title):
#     root=tk.Tk(); root.withdraw()
#     return filedialog.askopenfilename(title=title,
#                                       filetypes=[("Images","*.png;*.jpg;*.jpeg")])

# # --- callbacks (unchanged except shortened logging) ---
# def _erase_cb(evt,x,y,flags,param):
#     global erase_start, main_img, dirty
#     if evt==cv2.EVENT_LBUTTONDOWN: erase_start=(x,y)
#     elif evt==cv2.EVENT_MOUSEMOVE and erase_start:
#         tmp=main_img.copy(); cv2.rectangle(tmp,erase_start,(x,y),(0,255,0),2)
#         cv2.imshow("Image Editor",tmp)
#     elif evt==cv2.EVENT_LBUTTONUP and erase_start:
#         x1,y1=erase_start; x2,y2=x,y
#         x1,x2=sorted((x1,x2)); y1,y2=sorted((y1,y2))
#         if x2-x1>0 and y2-y1>0:
#             main_img[y1:y2,x1:x2]=255; dirty=True; cv2.imshow("Image Editor",main_img)
#         erase_start=None

# def _logo_cb(evt,x,y,flags,param):
#     global logo_start, main_img, logo_img, dirty
#     if evt==cv2.EVENT_LBUTTONDOWN: logo_start=(x,y)
#     elif evt==cv2.EVENT_MOUSEMOVE and logo_start:
#         tmp=main_img.copy(); cv2.rectangle(tmp,logo_start,(x,y),(255,0,0),2)
#         cv2.imshow("Image Editor",tmp)
#     elif evt==cv2.EVENT_LBUTTONUP and logo_start:
#         x1,y1=logo_start; x2,y2=x,y
#         x1,x2=sorted((x1,x2)); y1,y2=sorted((y1,y2))
#         if x2-x1>0 and y2-y1>0:
#             h,w=y2-y1,x2-x1
#             rs=cv2.resize(logo_img,(w,h))
#             mask=cv2.GaussianBlur(np.ones((h,w))*255,(0,0),w*0.05)
#             alpha=(mask/255)[:,:,None]
#             main_img[y1:y2,x1:x2]=(rs*alpha+main_img[y1:y2,x1:x2]*(1-alpha)).astype(np.uint8)
#             dirty=True; cv2.imshow("Image Editor",main_img)
#         logo_start=None

# # -------- public launcher --------
# def launch_logo_editor(image_path: str):
#     """
#     Opens an editor on `image_path`.
#     Returns the path of the saved logo-added image, or None if user cancelled.
#     """
#     global main_img, orig_img, erase_start, logo_start, logo_img, dirty

#     if not image_path: return None
#     orig_img = cv2.imread(image_path)
#     if orig_img is None: return None
#     main_img = orig_img.copy()

#     # interactive session
#     while True:
#         dirty=False
#         cv2.namedWindow("Image Editor"); cv2.setMouseCallback("Image Editor", _erase_cb)
#         cv2.imshow("Image Editor", main_img)
#         while cv2.waitKey(1)!=27: pass   # Esc exits erase stage

#         print("\n1 Erase more | 2 Insert logo | 3 Reset | 4 Save & Exit | 5 Exit")
#         ch=input("Choice: ").strip()
#         if ch=='1':
#             continue
#         elif ch=='2':
#             lp=_browse("Select logo")
#             if not lp: continue
#             logo_img=cv2.imread(lp); 
#             if logo_img is None: continue
#             cv2.setMouseCallback("Image Editor", _logo_cb)
#             while cv2.waitKey(1)!=27: pass
#             cv2.setMouseCallback("Image Editor", lambda *a:None)
#         elif ch=='3':
#             main_img = orig_img.copy()
#         elif ch=='4':
#             stem,ext = os.path.splitext(image_path)
#             out_path  = stem + "_logo" + ext
#             cv2.imwrite(out_path, main_img)
#             print("Saved", out_path)
#             cv2.destroyAllWindows()
#             return out_path
#         elif ch=='5':
#             break
#     cv2.destroyAllWindows()
#     return None

# # globals
# main_img=None; orig_img=None
# erase_start=None; logo_start=None
# logo_img=None; dirty=False
################
##################################
import cv2, numpy as np, os, tkinter as tk
from tkinter import filedialog

# Global holders
main_img = None        # Original image
disp_img = None        # Resized for display
scale    = 1.0
dirty    = False
erase_start = None
logo_start = None
logo_img = None

def _browse(title):
    root = tk.Tk(); root.withdraw()
    return filedialog.askopenfilename(
        title=title,
        filetypes=[("Images", "*.png;*.jpg;*.jpeg")])

def _resize_for_display(img, max_width=900):
    h, w = img.shape[:2]
    if w > max_width:
        scale = max_width / w
        return cv2.resize(img, None, fx=scale, fy=scale), scale
    return img.copy(), 1.0

# ============================
# CALLBACKS with scaling fix
# ============================
def _erase_cb(evt, x, y, flags, param):
    global erase_start, main_img, disp_img, dirty, scale
    x_orig, y_orig = int(x / scale), int(y / scale)

    if evt == cv2.EVENT_LBUTTONDOWN:
        erase_start = (x_orig, y_orig)
    elif evt == cv2.EVENT_MOUSEMOVE and erase_start:
        tmp = disp_img.copy()
        x1, y1 = int(erase_start[0] * scale), int(erase_start[1] * scale)
        cv2.rectangle(tmp, (x1, y1), (x, y), (0, 255, 0), 2)
        cv2.imshow("Image Editor", tmp)
    elif evt == cv2.EVENT_LBUTTONUP and erase_start:
        x1, y1 = erase_start
        x2, y2 = x_orig, y_orig
        x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2))
        if (x2 - x1 > 0) and (y2 - y1 > 0):
            main_img[y1:y2, x1:x2] = 255
            dirty = True
        erase_start = None
        disp_img[:]=cv2.resize(main_img, None, fx=scale, fy=scale)
        cv2.imshow("Image Editor", disp_img)

def _logo_cb(evt, x, y, flags, param):
    global logo_start, main_img, disp_img, dirty, scale, logo_img
    x_orig, y_orig = int(x / scale), int(y / scale)

    if evt == cv2.EVENT_LBUTTONDOWN:
        logo_start = (x_orig, y_orig)
    elif evt == cv2.EVENT_MOUSEMOVE and logo_start:
        tmp = disp_img.copy()
        x1, y1 = int(logo_start[0] * scale), int(logo_start[1] * scale)
        cv2.rectangle(tmp, (x1, y1), (x, y), (255, 0, 0), 2)
        cv2.imshow("Image Editor", tmp)
    elif evt == cv2.EVENT_LBUTTONUP and logo_start:
        x1, y1 = logo_start
        x2, y2 = x_orig, y_orig
        x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2))
        if (x2 - x1 > 0) and (y2 - y1 > 0):
            roi_h, roi_w = y2 - y1, x2 - x1
            logo_resized = cv2.resize(logo_img, (roi_w, roi_h), interpolation=cv2.INTER_AREA)
            mask = cv2.GaussianBlur(np.ones((roi_h, roi_w), dtype=np.uint8) * 255,
                                    (0, 0), sigmaX=roi_w * 0.05)

            logo_f = logo_resized.astype(np.float32)
            roi_f = main_img[y1:y2, x1:x2].astype(np.float32)
            alpha = (mask / 255.0)[..., None]

            blended = (logo_f * alpha + roi_f * (1 - alpha)).astype(np.uint8)
            main_img[y1:y2, x1:x2] = blended
            dirty = True

        logo_start = None
        disp_img[:]=cv2.resize(main_img, None, fx=scale, fy=scale)
        cv2.imshow("Image Editor", disp_img)

# =============================
# MAIN LAUNCH FUNCTION
# =============================
def launch_logo_editor(image_path: str):
    global main_img, disp_img, scale, dirty, erase_start, logo_start, logo_img

    if not image_path: return None
    main_img = cv2.imread(image_path)
    if main_img is None: return None

    disp_img, scale = _resize_for_display(main_img)

    while True:
        dirty = False
        cv2.namedWindow("Image Editor")
        cv2.setMouseCallback("Image Editor", _erase_cb)
        cv2.imshow("Image Editor", disp_img)
        while cv2.waitKey(1) != 27:
            pass

        print("\n1 Erase more | 2 Insert logo | 3 Reset | 4 Save & Exit | 5 Exit")
        ch = input("Choice: ").strip()
        if ch == '1':
            continue
        elif ch == '2':
            logo_path = _browse("Select Logo")
            if not logo_path: continue
            logo_img = cv2.imread(logo_path)
            if logo_img is None: continue
            cv2.setMouseCallback("Image Editor", _logo_cb)
            while cv2.waitKey(1) != 27:
                pass
        elif ch == '3':
            main_img = cv2.imread(image_path)
            disp_img, scale = _resize_for_display(main_img)
        elif ch == '4':
            stem, ext = os.path.splitext(image_path)
            out_path = stem + "_logo" + ext
            cv2.imwrite(out_path, main_img)
            cv2.destroyAllWindows()
            print("✅ Saved:", out_path)
            return out_path
        elif ch == '5':
            break

    cv2.destroyAllWindows()
    return None
