# omr_processor.py
import cv2
import numpy as np
# Pastikan Anda mengganti 'testutil' dengan nama file utilitas Anda yang sebenarnya jika berbeda
# dan file tersebut berada di lokasi yang dapat diimpor (misalnya, di folder yang sama)
import testutil as utils

def proses_satu_gambar(path_gambar_input, kunci_jawaban_ujian_benar):
    """
    Memproses satu gambar LJK dan mengembalikan skor serta jawaban yang terdeteksi.
    
    Args:
        path_gambar_input (str): Path ke file gambar LJK.
        kunci_jawaban_ujian_benar (list): List integer dari kunci jawaban ujian (0=A, 1=B, dst.).
                                          Ini digunakan untuk menghitung skor.
    
    Returns:
        tuple: (float skor_sistem, list jawaban_terdeteksi_sistem)
               skor_sistem adalah persentase.
               jawaban_terdeteksi_sistem adalah list integer dari pilihan yang terdeteksi sistem.
               Mengembalikan (0.0, [-3]*len(kunci_jawaban_ujian_benar)) jika ada error kritis.
               Jawaban -1 berarti tidak ada jawaban terdeteksi untuk soal itu.
               Jawaban -2 berarti error saat mencocokkan jumlah jawaban terdeteksi.
               Jawaban -3 berarti error pemrosesan gambar awal.
    """
    img_original = cv2.imread(path_gambar_input)
    if img_original is None:
        print(f"Error: Gagal membaca gambar {path_gambar_input}")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)
        
    # Resize gambar input ke ukuran standar pemrosesan
    img = cv2.resize(img_original, (700, 700)) # Ukuran standar dari kode awal Anda

    # 1. Preprocessing Awal
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 2. Deteksi Kontur LJK
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rectCon = utils.rectContour(contours) # Fungsi utilitas Anda

    if not rectCon:
        print(f"Error: Tidak ditemukan kontur persegi panjang yang valid untuk {path_gambar_input}")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)

    # Asumsi kontur LJK adalah yang terbesar atau salah satu yang terbesar
    # Kode Anda sebelumnya menggunakan rectCon[1], kita coba adaptasi dari sana.
    # Jika rectCon hanya mengembalikan satu kontur LJK yang valid:
    if len(rectCon) >= 1:
        ljk_contour = rectCon[0] # Ambil kontur LJK utama (mungkin perlu penyesuaian)
        # Jika rectCon[0] adalah LJK dan rectCon[1] adalah bagian lain, maka sesuaikan.
        # Jika Anda yakin rectCon[1] adalah LJK:
        # if len(rectCon) > 1:
        #     ljk_contour = rectCon[1]
        # else:
        #     ljk_contour = rectCon[0] # Fallback jika hanya satu
    else:
        print(f"Error: Tidak cukup kontur valid yang ditemukan oleh rectContour untuk {path_gambar_input}")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)


    biggest_contour_points = utils.getCornerPoints(ljk_contour) # Fungsi utilitas Anda

    if biggest_contour_points.size == 0:
        print(f"Error: Tidak bisa mendapatkan titik sudut dari kontur LJK untuk {path_gambar_input}")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)

    # 3. Transformasi Perspektif
    reordered_points = utils.reorder(biggest_contour_points) # Fungsi utilitas Anda
    pt1 = np.float32(reordered_points)
    
    # Ukuran standar untuk gambar LJK yang sudah diluruskan (warped)
    warped_width = 700  # Sesuaikan jika LJK Anda proporsinya berbeda & splitBoxes mengharapkan lain
    warped_height = 700 # Sesuaikan jika LJK Anda proporsinya berbeda & splitBoxes mengharapkan lain
    pt2 = np.float32([[0, 0], [warped_width, 0], [0, warped_height], [warped_width, warped_height]])
    
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    img_warped_color = cv2.warpPerspective(img, matrix, (warped_width, warped_height))

    # 4. Preprocessing pada Gambar Warped & Persiapan untuk SplitBoxes
    img_warped_gray = cv2.cvtColor(img_warped_color, cv2.COLOR_BGR2GRAY)
    img_thresh_warped = cv2.adaptiveThreshold(img_warped_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 11, 2)

    # Isolasi area pilihan jawaban dari img_thresh_warped
    # Proporsi ini dari kode Anda di testutil.py (1/4.5)
    # Mungkin perlu disesuaikan berdasarkan layout LJK Anda pada gambar 700x700 yang sudah di-warp
    h_w, w_w = img_thresh_warped.shape[:2]
    # batas_pemotongan = int(w_w / 4.5) # Ini adalah kolom AWAL dari pilihan jawaban
    # Kode splitBoxes Anda di testutil.py: `pilihan_jawaban = img_resized[:, batas_pemotongan:]`
    # Ini berarti kita perlu mengambil dari `batas_pemotongan` hingga akhir.
    
    # Sesuaikan 'start_col_pilihan' jika cropping di splitBoxes berbeda.
    # Berdasarkan kode `splitBoxes` Anda yang lama: `batas_pemotongan = int(width / 4.5)`
    # lalu `pilihan_jawaban = img_resized[:, batas_pemotongan:]`
    start_col_pilihan = int(w_w / 4.5) # Kolom di mana area pilihan jawaban dimulai
    area_pilihan_jawaban = img_thresh_warped[:, start_col_pilihan:]

    h_p, w_p = area_pilihan_jawaban.shape[:2]

    # Pastikan tinggi dan lebar area pilihan jawaban adalah kelipatan yang diinginkan (30 baris, 5 kolom)
    # sebelum dikirim ke splitBoxes versi sederhana.
    target_h_for_split = (h_p // 30) * 30
    target_w_for_split = (w_p // 5) * 5

    if target_h_for_split == 0 or target_w_for_split == 0:
        print(f"Error: Ukuran area pilihan jawaban ({h_p}x{w_p}) terlalu kecil setelah di-crop untuk di-split menjadi 30x5 pada {path_gambar_input}.")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)

    img_ready_for_split = cv2.resize(area_pilihan_jawaban, (target_w_for_split, target_h_for_split))
    
    # 5. Split menjadi Kotak-kotak Jawaban
    # Asumsi utils.splitBoxes sekarang adalah versi sederhana yang hanya melakukan vsplit dan hsplit
    boxes = utils.splitBoxes(img_ready_for_split) 

    if not boxes or len(boxes) != (30 * 5): # 30 soal, 5 opsi
        print(f"Error: Jumlah kotak jawaban ({len(boxes) if boxes else 0}) tidak sesuai harapan (150) untuk {path_gambar_input}")
        return 0.0, [-3] * len(kunci_jawaban_ujian_benar)

    # 6. Ekstraksi Jawaban dari Setiap Kotak
    myPixelValue = np.zeros((30, 5)) # 30 soal, 5 opsi
    countC = 0
    countR = 0

    for image_box in boxes:
        if image_box is None or image_box.size == 0:
            print(f"Peringatan: Kotak jawaban kosong atau tidak valid pada R{countR} C{countC} untuk {path_gambar_input}")
            # Beri nilai yang sangat kecil agar tidak terpilih jika ada yang lain
            myPixelValue[countR][countC] = -1 
        else:
            totalPixels = cv2.countNonZero(image_box)
            myPixelValue[countR][countC] = totalPixels
        
        countC += 1
        if countC == 5: 
            countR += 1
            countC = 0
    
    jawaban_terdeteksi_sistem = []
    for x in range(30): # Asumsi 30 soal
        arr = myPixelValue[x]
        if np.all(arr <= 0): # Jika semua nilai pixel count <= 0 (termasuk -1 dari box kosong)
            jawaban_terdeteksi_sistem.append(-1) # -1 menandakan tidak ada jawaban terdeteksi / tidak diisi
            # print(f"Peringatan: Tidak ada jawaban terdeteksi (atau box error) untuk soal {x+1} di {path_gambar_input}")
        else:
            # Hanya pertimbangkan nilai positif untuk np.amax
            positive_arr = arr[arr > 0]
            if positive_arr.size == 0 : # Jika setelah filter tidak ada nilai positif (semua <=0)
                jawaban_terdeteksi_sistem.append(-1)
            else:
                # Temukan max di array asli, tapi pastikan max > 0
                max_val = np.amax(arr)
                if max_val <=0: # Jika max nya sendiri <=0
                    jawaban_terdeteksi_sistem.append(-1)
                else:
                    myIndexVal = np.where(arr == max_val)
                    jawaban_terdeteksi_sistem.append(myIndexVal[0][0])


    # 7. Penilaian (Grading)
    grading = []
    if len(jawaban_terdeteksi_sistem) == len(kunci_jawaban_ujian_benar):
        for x in range(len(kunci_jawaban_ujian_benar)):
            if jawaban_terdeteksi_sistem[x] == -1: # Jika sistem tidak mendeteksi jawaban
                grading.append(0) # Dianggap salah
            elif kunci_jawaban_ujian_benar[x] == jawaban_terdeteksi_sistem[x]:
                grading.append(1)
            else:
                grading.append(0)
        
        if len(kunci_jawaban_ujian_benar) > 0:
            skor_sistem = (sum(grading) / len(kunci_jawaban_ujian_benar)) * 100
        else:
            skor_sistem = 0.0 # Hindari pembagian dengan nol
    else:
        print(f"Error: Jumlah jawaban terdeteksi ({len(jawaban_terdeteksi_sistem)}) tidak sama dengan jumlah kunci jawaban ({len(kunci_jawaban_ujian_benar)}) untuk {path_gambar_input}")
        skor_sistem = 0.0
        jawaban_terdeteksi_sistem = [-2] * len(kunci_jawaban_ujian_benar) # -2 menandai error panjang array

    return skor_sistem, jawaban_terdeteksi_sistem

# --- Contoh Penggunaan (untuk testing fungsi ini saja, bisa di-comment) ---
# if __name__ == '__main__':
#     # Sediakan path gambar contoh dan kunci jawaban contoh
#     contoh_path_gambar = 'dataset_uji_augmented/ljk_dasar_kunci_1_rot2_0.jpg' # Ganti dengan path valid
#     # Kunci jawaban dari diskusi sebelumnya (30 soal)
#     contoh_kunci_jawaban = [2,1,3,1,1,1,1,4,3,2,1,1,2,3,1,1,1,2,1,2,3,2,0,2,1,2,4,0,2,1] 
    
#     if os.path.exists(contoh_path_gambar):
#         skor, jawaban_deteksi = proses_satu_gambar(contoh_path_gambar, contoh_kunci_jawaban)
#         print(f"Skor Sistem: {skor}%")
#         print(f"Jawaban Terdeteksi: {jawaban_deteksi}")
#     else:
#         print(f"File contoh tidak ditemukan: {contoh_path_gambar}")