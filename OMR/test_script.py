import pandas as pd
import os
from omr__processor import proses_satu_gambar

# --- Konfigurasi ---
# Di dalam test_script_rotasi.py
file_ground_truth_csv = 'ground_truth_rotasi.csv' # Gunakan CSV ground truth yang baru
folder_gambar_uji = 'dataset_uji_rotasi'         # Gunakan folder gambar rotasi
file_hasil_pengujian_csv = 'hasil_pengujian_rotasi.csv' # Simpan hasil ke file baru

# Definisikan KUNCI JAWABAN UJIAN yang sebenarnya (digunakan sistem OMR untuk menilai)
# Kunci jawaban Anda: C,B,D,B,B,B,B,E,D,C,B,B,C,D,B,B,B,C,B,C,D,C,A,C,B,C,E,A,C,B
# Dikonversi ke indeks (A=0, B=1, C=2, D=3, E=4):
kunci_jawaban_ujian_benar = [2,1,3,1,1,1,1,4,3,2,1,1,2,3,1,1,1,2,1,2,3,2,0,2,1,2,4,0,2,1]
# ------------------------------------------------------------------------------------

# Baca file ground truth
try:
    df_ground_truth = pd.read_csv(file_ground_truth_csv)
except FileNotFoundError:
    print(f"Error: File '{file_ground_truth_csv}' tidak ditemukan. Jalankan skrip 'buat_ground_truth.py' terlebih dahulu.")
    exit()

hasil_pengujian_list = []

print(f"Memulai pengujian otomatis untuk {len(df_ground_truth)} gambar...")

# Loop untuk setiap gambar dalam file ground truth
for index, row in df_ground_truth.iterrows():
    nama_file_gambar = row['nama_file_gambar']
    path_gambar_lengkap = os.path.join(folder_gambar_uji, nama_file_gambar)
    
    # jawaban_sebenarnya_ditandai adalah apa yang secara fisik ditandai di LJK (dari ground_truth.csv)
    # Ini akan digunakan nanti di skrip analisis untuk membandingkan dengan deteksi sistem
    jawaban_fisik_ditandai_str = row['jawaban_sebenarnya_ditandai'] 
    
    print(f"  Memproses: {nama_file_gambar}...")
    
    # Panggil fungsi inti OMR Anda
    # Fungsi ini akan menggunakan kunci_jawaban_ujian_benar untuk menghitung skor internalnya
    skor_dari_sistem, jawaban_dideteksi_sistem_list = proses_satu_gambar(path_gambar_lengkap, kunci_jawaban_ujian_benar)
    
    # Konversi list jawaban yang dideteksi sistem menjadi string untuk disimpan di CSV
    jawaban_dideteksi_sistem_str = ','.join(map(str, jawaban_dideteksi_sistem_list))
    
    hasil_pengujian_list.append({
        'nama_file_gambar': nama_file_gambar,
        'jawaban_fisik_ditandai_str': jawaban_fisik_ditandai_str, # Dari ground_truth.csv
        'jawaban_dideteksi_sistem_str': jawaban_dideteksi_sistem_str, # Dari OMR
        'skor_dari_sistem': skor_dari_sistem # Skor yang dihitung OMR
    })

# Simpan semua hasil ke file CSV baru
df_hasil_pengujian = pd.DataFrame(hasil_pengujian_list)
df_hasil_pengujian.to_csv(file_hasil_pengujian_csv, index=False)

print(f"\nPengujian otomatis selesai!")
print(f"Hasil disimpan di: '{file_hasil_pengujian_csv}'")