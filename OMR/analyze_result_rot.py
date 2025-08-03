import pandas as pd
import numpy as np # Untuk np.mean

# --- Konfigurasi ---
# Ganti nama file ini jika Anda menganalisis hasil untuk kondisi spesifik
# Misalnya: 'hasil_pengujian_rotasi.csv'
file_hasil_pengujian = 'hasil_pengujian_rotasi.csv' 

# Jumlah soal per LJK, harus konsisten
JUMLAH_SOAL_PER_LJK = 30 

# Judul untuk output (sesuaikan jika menganalisis kondisi tertentu)
JUDUL_ANALISIS = "--- Hasil Analisis Keseluruhan ---"
# Contoh jika untuk kondisi rotasi:
# JUDUL_ANALISIS = "--- Hasil Analisis KONDISI 2: Efek Rotasi ---"
# ------------------------------------------------------------------------------------

try:
    df_hasil = pd.read_csv(file_hasil_pengujian)
except FileNotFoundError:
    print(f"Error: File hasil pengujian '{file_hasil_pengujian}' tidak ditemukan.")
    print("Pastikan Anda sudah menjalankan skrip pengujian (misal: 'test_script.py') dan file CSV hasil berhasil dibuat.")
    exit()
except pd.errors.EmptyDataError:
    print(f"Error: File hasil pengujian '{file_hasil_pengujian}' kosong.")
    print("Periksa kembali output dari skrip pengujian dan 'omr_processor.py' untuk kemungkinan error.")
    exit()


if df_hasil.empty:
    print(f"File hasil pengujian '{file_hasil_pengujian}' tidak berisi data.")
    exit()

# List untuk menyimpan akurasi deteksi jawaban per LJK
akurasi_deteksi_per_ljk_list = []
# List untuk menyimpan skor dari sistem per LJK
skor_sistem_list = []

total_semua_jawaban_cocok = 0
total_semua_soal_diuji = 0
jumlah_ljk_valid_diproses = 0

print(f"Menganalisis hasil dari '{file_hasil_pengujian}'...")
print(JUDUL_ANALISIS)


for index, row in df_hasil.iterrows():
    nama_file = row['nama_file_gambar']
    
    try:
        # Jawaban yang sebenarnya ditandai di kertas (dari ground_truth.csv)
        jawaban_fisik_list = [int(x) for x in str(row['jawaban_fisik_ditandai_str']).split(',')]
        
        # Jawaban yang dideteksi oleh sistem OMR
        jawaban_sistem_list = [int(x) for x in str(row['jawaban_dideteksi_sistem_str']).split(',')]

    except ValueError as e:
        print(f"  Peringatan untuk file {nama_file}: Format string jawaban tidak valid. Baris dilewati. Detail: {e}")
        print(f"    Jawaban Fisik String: '{row['jawaban_fisik_ditandai_str']}'")
        print(f"    Jawaban Sistem String: '{row['jawaban_dideteksi_sistem_str']}'")
        continue 

    skor_sistem = row['skor_dari_sistem']
    skor_sistem_list.append(skor_sistem)

    if len(jawaban_fisik_list) != JUMLAH_SOAL_PER_LJK or len(jawaban_sistem_list) != JUMLAH_SOAL_PER_LJK:
        print(f"  Peringatan untuk file {nama_file}: Panjang list jawaban tidak sesuai ({len(jawaban_fisik_list)} atau {len(jawaban_sistem_list)}) dengan JUMLAH_SOAL_PER_LJK ({JUMLAH_SOAL_PER_LJK}). Baris dilewati.")
        continue 
    
    jumlah_ljk_valid_diproses += 1
    jumlah_jawaban_cocok_ljk_ini = 0
    for i in range(JUMLAH_SOAL_PER_LJK):
        if jawaban_fisik_list[i] == jawaban_sistem_list[i]:
            jumlah_jawaban_cocok_ljk_ini += 1
    
    total_semua_jawaban_cocok += jumlah_jawaban_cocok_ljk_ini
    total_semua_soal_diuji += JUMLAH_SOAL_PER_LJK
    
    if JUMLAH_SOAL_PER_LJK > 0: # Hindari pembagian dengan nol jika JUMLAH_SOAL_PER_LJK = 0
        akurasi_ljk_ini = (jumlah_jawaban_cocok_ljk_ini / JUMLAH_SOAL_PER_LJK) * 100
        akurasi_deteksi_per_ljk_list.append(akurasi_ljk_ini)
    else:
        akurasi_deteksi_per_ljk_list.append(0)


# --- Hitung Rata-rata Keseluruhan ---
if total_semua_soal_diuji > 0:
    rata_rata_akurasi_deteksi_keseluruhan = (total_semua_jawaban_cocok / total_semua_soal_diuji) * 100
    print(f"\nTotal LJK yang Dianalisis (valid): {jumlah_ljk_valid_diproses}")
    print(f"Total Soal Diuji (dari LJK valid): {total_semua_soal_diuji}")
    print(f"Total Jawaban yang Terdeteksi Cocok dengan Fisik: {total_semua_jawaban_cocok}")
    print(f"Rata-rata Akurasi Deteksi Jawaban (per soal dari semua LJK valid): {rata_rata_akurasi_deteksi_keseluruhan:.2f}%")
else:
    print("\nTidak ada data LJK valid yang diproses untuk dianalisis.")

if skor_sistem_list: # Pastikan list tidak kosong
    rata_rata_skor_sistem = np.mean(skor_sistem_list)
    print(f"Rata-rata Skor yang Dihasilkan Sistem (dari LJK valid): {rata_rata_skor_sistem:.2f}%")
else:
    # Ini akan terjadi jika semua baris dilewati karena error format atau panjang
    print("Tidak ada data skor sistem yang valid untuk dihitung rata-ratanya.")

# --- (Opsional) Menyimpan ringkasan jika Anda mau ---
# if jumlah_ljk_valid_diproses > 0:
#     output_summary_data = {
#         'Kondisi Analisis': [JUDUL_ANALISIS.replace("--- ", "").replace(" ---", "")],
#         'Total LJK Valid': [jumlah_ljk_valid_diproses],
#         'Rata-rata Akurasi Deteksi Jawaban (%)': [round(rata_rata_akurasi_deteksi_keseluruhan, 2) if total_semua_soal_diuji > 0 else 0],
#         'Rata-rata Skor Sistem (%)': [round(rata_rata_skor_sistem, 2) if skor_sistem_list else 0]
#     }
#     df_summary = pd.DataFrame(output_summary_data)
    
#     nama_file_ringkasan = 'ringkasan_analisis_pengujian.csv'
#     # Tambahkan ke file yang ada atau buat baru
#     try:
#         existing_summary = pd.read_csv(nama_file_ringkasan)
#         df_summary = pd.concat([existing_summary, df_summary], ignore_index=True)
#     except FileNotFoundError:
#         pass # File belum ada, akan dibuat baru
        
#     df_summary.to_csv(nama_file_ringkasan, index=False)
#     print(f"\nRingkasan analisis disimpan/diperbarui di '{nama_file_ringkasan}'")