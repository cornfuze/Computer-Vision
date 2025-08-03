import pandas as pd
import numpy as np # Berguna untuk konversi tipe data jika diperlukan

# --- Konfigurasi ---
file_hasil_pengujian = 'hasil_pengujian_otomatis.csv'
# Jumlah soal per LJK, harus konsisten dengan bagaimana Anda membuat ground truth dan sistem memproses
JUMLAH_SOAL_PER_LJK = 30 
# ------------------------------------------------------------------------------------

try:
    df_hasil = pd.read_csv(file_hasil_pengujian)
except FileNotFoundError:
    print(f"Error: File hasil pengujian '{file_hasil_pengujian}' tidak ditemukan.")
    print("Pastikan Anda sudah menjalankan 'test_script.py' dan file CSV berhasil dibuat.")
    exit()
except pd.errors.EmptyDataError:
    print(f"Error: File hasil pengujian '{file_hasil_pengujian}' kosong.")
    print("Periksa kembali output dari 'test_script.py' dan 'omr_processor.py' untuk kemungkinan error.")
    exit()


if df_hasil.empty:
    print(f"File hasil pengujian '{file_hasil_pengujian}' tidak berisi data.")
    exit()

# List untuk menyimpan akurasi deteksi jawaban per LJK
akurasi_deteksi_per_ljk_list = []
# List untuk menyimpan akurasi skor per LJK (jika skor ground truth manual ada)
# Untuk kasus ini, kita fokus pada akurasi deteksi jawaban yang ditandai.
# Skor sistem sudah ada, kita bisa merata-ratakannya.
skor_sistem_list = []

total_semua_jawaban_cocok = 0
total_semua_soal_diuji = 0

print(f"Menganalisis hasil dari '{file_hasil_pengujian}'...")

for index, row in df_hasil.iterrows():
    nama_file = row['nama_file_gambar']
    
    # --- Konversi string jawaban menjadi list of integers ---
    try:
        # Jawaban yang sebenarnya ditandai di kertas (dari ground_truth.csv)
        jawaban_fisik_list = [int(x) for x in str(row['jawaban_fisik_ditandai_str']).split(',')]
        
        # Jawaban yang dideteksi oleh sistem OMR
        jawaban_sistem_list = [int(x) for x in str(row['jawaban_dideteksi_sistem_str']).split(',')]

    except ValueError as e:
        print(f"  Peringatan untuk file {nama_file}: Format string jawaban tidak valid. Baris dilewati. Detail: {e}")
        print(f"    Jawaban Fisik String: '{row['jawaban_fisik_ditandai_str']}'")
        print(f"    Jawaban Sistem String: '{row['jawaban_dideteksi_sistem_str']}'")
        continue # Lanjut ke baris berikutnya jika ada error konversi

    skor_sistem = row['skor_dari_sistem']
    skor_sistem_list.append(skor_sistem)

    # Pastikan kedua list jawaban memiliki panjang yang sama (JUMLAH_SOAL_PER_LJK)
    if len(jawaban_fisik_list) != JUMLAH_SOAL_PER_LJK or len(jawaban_sistem_list) != JUMLAH_SOAL_PER_LJK:
        print(f"  Peringatan untuk file {nama_file}: Panjang list jawaban tidak sesuai dengan JUMLAH_SOAL_PER_LJK ({JUMLAH_SOAL_PER_LJK}).")
        print(f"    Panjang Jawaban Fisik: {len(jawaban_fisik_list)}")
        print(f"    Panjang Jawaban Sistem: {len(jawaban_sistem_list)}")
        # Anda bisa memutuskan untuk melewati baris ini atau menanganinya secara khusus
        continue 

    # --- Hitung akurasi deteksi jawaban untuk LJK ini ---
    jumlah_jawaban_cocok_ljk_ini = 0
    for i in range(JUMLAH_SOAL_PER_LJK):
        # Kita ingin tahu apakah sistem mendeteksi tanda yang sama dengan yang ada di kertas
        # Termasuk jika murid tidak mengisi (diwakili oleh -1 di ground truth dan deteksi sistem)
        if jawaban_fisik_list[i] == jawaban_sistem_list[i]:
            jumlah_jawaban_cocok_ljk_ini += 1
    
    total_semua_jawaban_cocok += jumlah_jawaban_cocok_ljk_ini
    total_semua_soal_diuji += JUMLAH_SOAL_PER_LJK
    
    akurasi_ljk_ini = (jumlah_jawaban_cocok_ljk_ini / JUMLAH_SOAL_PER_LJK) * 100
    akurasi_deteksi_per_ljk_list.append(akurasi_ljk_ini)
    
    # print(f"  File: {nama_file}, Akurasi Deteksi Jawaban: {akurasi_ljk_ini:.2f}%, Skor Sistem: {skor_sistem:.2f}%")


# --- Hitung Rata-rata Keseluruhan ---
if total_semua_soal_diuji > 0:
    rata_rata_akurasi_deteksi_keseluruhan = (total_semua_jawaban_cocok / total_semua_soal_diuji) * 100
    print(f"\n--- Hasil Analisis Keseluruhan ---")
    print(f"Total LJK yang Dianalisis (valid): {len(akurasi_deteksi_per_ljk_list)}")
    print(f"Total Soal Diuji (dari LJK valid): {total_semua_soal_diuji}")
    print(f"Total Jawaban yang Terdeteksi Cocok dengan Fisik: {total_semua_jawaban_cocok}")
    print(f"Rata-rata Akurasi Deteksi Jawaban (per soal dari semua LJK valid): {rata_rata_akurasi_deteksi_keseluruhan:.2f}%")
else:
    print("\nTidak ada data valid untuk dianalisis.")

if skor_sistem_list:
    rata_rata_skor_sistem = np.mean(skor_sistem_list)
    print(f"Rata-rata Skor yang Dihasilkan Sistem (dari LJK valid): {rata_rata_skor_sistem:.2f}%")
else:
    print("Tidak ada data skor sistem yang valid untuk dihitung rata-ratanya.")

# --- (Opsional) Simpan ringkasan hasil analisis jika perlu ---
# output_summary = {
#     'total_ljk_valid': [len(akurasi_deteksi_per_ljk_list)],
#     'rata_rata_akurasi_deteksi_jawaban': [rata_rata_akurasi_deteksi_keseluruhan if total_semua_soal_diuji > 0 else 0],
#     'rata_rata_skor_sistem': [rata_rata_skor_sistem if skor_sistem_list else 0]
# }
# df_summary = pd.DataFrame(output_summary)
# df_summary.to_csv('ringkasan_analisis_pengujian.csv', index=False)
# print("\nRingkasan analisis disimpan ke 'ringkasan_analisis_pengujian.csv'")