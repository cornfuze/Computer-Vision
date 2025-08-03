import cv2
import numpy as np
import utils # Asumsi ada file utils.py untuk fungsi bantuan

def proses_ljk_dan_dapatkan_skor(path_gambar, kunci_jawaban):
    """
    Fungsi utama untuk memproses satu gambar LJK dari awal hingga akhir.
    """
    # Parameter Awal
    lebar_gambar = 700
    tinggi_gambar = 700
    jumlah_soal = 30
    jumlah_opsi = 5

    # 1. TAHAP PRA-PEMROSESAN
    img = cv2.imread(path_gambar)
    img = cv2.resize(img, (lebar_gambar, tinggi_gambar))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, 
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)

    # 2. TAHAP DETEKSI & TRANSFORMASI
    contours, _ = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    kontur_terbesar = utils.rectContour(contours)
    if kontur_terbesar.size != 0:
        titik_sudut = utils.getCornerPoints(kontur_terbesar)
        if titik_sudut.size != 0:
            titik_sudut_terurut = utils.reorder(titik_sudut)

            pt1 = np.float32(titik_sudut_terurut)
            pt2 = np.float32([[0, 0], [lebar_gambar, 0], 
                              [0, tinggi_gambar], [lebar_gambar, tinggi_gambar]])
            
            matrix = cv2.getPerspectiveTransform(pt1, pt2)
            img_warped = cv2.warpPerspective(img, matrix, (lebar_gambar, tinggi_gambar))
            img_warped_gray = cv2.cvtColor(img_warped, cv2.COLOR_BGR2GRAY)

            # 3. TAHAP SEGMENTASI & EKSTRAKSI
            kotak_jawaban = utils.splitBoxes(img_warped_gray)
            pixel_values = np.zeros((jumlah_soal, jumlah_opsi))

            for i, kotak in enumerate(kotak_jawaban):
                baris = i // jumlah_opsi
                kolom = i % jumlah_opsi
                pixel_values[baris][kolom] = cv2.countNonZero(kotak)

            jawaban_terdeteksi = [np.argmax(row) for row in pixel_values]

            # 4. TAHAP PENILAIAN (GRADING)
            skor = 0
            for i in range(jumlah_soal):
                if jawaban_terdeteksi[i] == kunci_jawaban[i]:
                    skor += 1
            
            skor_persentase = (skor / jumlah_soal) * 100

            return skor_persentase, img_warped # Mengembalikan skor dan gambar hasil untuk visualisasi
            
    return 0, None # Mengembalikan nilai default jika LJK tidak terdeteksi