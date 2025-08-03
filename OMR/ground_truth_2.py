import os
import csv

# --- Konfigurasi ---
folder_augmented_rotasi = 'dataset_uji_rotasi' # Folder hasil augmentasi rotasi
file_output_csv_rotasi = 'ground_truth_rotasi.csv' # Nama file CSV baru

# Definisikan SATU string jawaban yang sama untuk SEMUA LJK DASAR Anda
# (Kunci Jawaban Ujian yang Anda arsir di LJK dasar)
# Kunci jawaban: C,B,D,B,B,B,B,E,D,C,B,B,C,D,B,B,B,C,B,C,D,C,A,C,B,C,E,A,C,B
# Dikonversi ke indeks (A=0, B=1, C=2, D=3, E=4):
string_kunci_jawaban_diarsir = "2,1,3,1,1,1,1,4,3,2,1,1,2,3,1,1,1,2,1,2,3,2,0,2,1,2,4,0,2,1"
# Pastikan konversi ini sudah 100% akurat.
# ------------------------------------------------------------------------------------

data_untuk_csv = []
header = ['nama_file_gambar', 'jawaban_sebenarnya_ditandai']

if not os.path.exists(folder_augmented_rotasi):
    print(f"Error: Folder '{folder_augmented_rotasi}' tidak ditemukan. Pastikan Anda sudah menjalankan skrip 'augmentasi_rotasi.py'.")
else:
    for nama_file_augmented in os.listdir(folder_augmented_rotasi):
        if nama_file_augmented.endswith(('.jpg', '.jpeg', '.png')):
            data_untuk_csv.append([nama_file_augmented, string_kunci_jawaban_diarsir])

    if data_untuk_csv:
        with open(file_output_csv_rotasi, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_untuk_csv)
        print(f"File '{file_output_csv_rotasi}' berhasil dibuat dengan {len(data_untuk_csv)} baris data.")
        print(f"Semua gambar di dataset rotasi menggunakan ground truth jawaban: {string_kunci_jawaban_diarsir}")
    else:
        print(f"Tidak ada file gambar ditemukan di folder '{folder_augmented_rotasi}'.")