import cv2
import numpy as np

# Load gambar
path = 'Assets/kunci.jpeg'  # Sesuaikan dengan lokasi gambar
img = cv2.imread(path)
if img is None:
    print("Gambar tidak ditemukan!")
    exit()
print("Gambar berhasil dimuat!")

# Resize gambar agar ukurannya konsisten
img = cv2.resize(img, (700, 700))

# Variabel untuk menyimpan koordinat ROI
x_start, y_start, x_end, y_end = 0, 0, 0, 0
cropping = False

def select_roi(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start = x, y
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        x_end, y_end = x, y
        cropping = False
        roi = img[y_start:y_end, x_start:x_end]
        cv2.imshow("ROI Terpilih", roi)
        process_roi(roi)

def process_roi(roi):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)
    
    # Deteksi kontur
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Jumlah Kontur Ditemukan: {len(contours)}")

    # Filter kontur berdasarkan ukuran
    contours = [c for c in contours if cv2.contourArea(c) > 100]  # Buang kontur kecil

    # Urutkan kontur dari atas ke bawah, kiri ke kanan
    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

    # Pisahkan ke dalam baris
    rows = []
    row = []
    prev_y = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if prev_y is not None and abs(y - prev_y) > 10:  # Jika y cukup jauh, buat baris baru
            rows.append(row)
            row = []
        row.append(c)
        prev_y = y
    rows.append(row)  # Tambahkan baris terakhir

    # Cek apakah jumlah baris sesuai dengan jumlah soal
    print(f"Jumlah Baris Terbaca: {len(rows)}")

    # Identifikasi jawaban yang dipilih
    jawaban_terpilih = []
    for i, row in enumerate(rows):
        row = sorted(row, key=lambda c: cv2.boundingRect(c)[0])  # Urutkan dari kiri ke kanan
        pilihan = ["A", "B", "C", "D", "E"]
        max_fill = 0
        jawaban = "X"  # Default jika tidak ada yang dipilih

        for j, c in enumerate(row):
            x, y, w, h = cv2.boundingRect(c)
            roi_box = thresh[y:y+h, x:x+w]
            filled_pixels = cv2.countNonZero(roi_box)

            if filled_pixels > max_fill:
                max_fill = filled_pixels
                jawaban = pilihan[j]

        jawaban_terpilih.append(jawaban)
        print(f"Soal {i+1}: Jawaban {jawaban}")

    # Gambar hasil deteksi
    roi_contours = roi.copy()
    cv2.drawContours(roi_contours, contours, -1, (0, 255, 0), 2)
    cv2.imshow("Kontur pada ROI", roi_contours)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

cv2.imshow("Pilih Area ROI", img)
cv2.setMouseCallback("Pilih Area ROI", select_roi)
cv2.waitKey(0)
cv2.destroyAllWindows()
