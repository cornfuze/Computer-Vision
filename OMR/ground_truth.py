import os
import csv

folder_augmented = 'dataset_uji_augmented' # Folder hasil augmentasi
file_output_csv = 'ground_truth.csv'

# --- Definisikan SATU string jawaban yang sama untuk SEMUA LJK DASAR Anda ---
# Ini adalah KUNCI JAWABAN UJIAN yang Anda arsir/tandai secara fisik pada SEMUA LJK dasar Anda.
# Kunci jawaban Anda: C,B,D,B,B,B,B,E,D,C,B,B,C,D,B,B,B,C,B,C,D,C,A,C,B,C,E,A,C,B
# Dikonversi ke indeks (A=0, B=1, C=2, D=3, E=4):
string_kunci_jawaban_diarsir = "2,1,3,1,1,1,1,4,3,2,1,1,2,3,1,1,1,2,1,2,3,2,0,2,1,2,4,0,2,1"
# Harap pastikan konversi ini sudah 100% akurat sesuai dengan apa yang Anda arsir di kertas.
# ------------------------------------------------------------------------------------

data_untuk_csv = []
header = ['nama_file_gambar', 'jawaban_sebenarnya_ditandai']

if not os.path.exists(folder_augmented):
    print(f"Error: Folder '{folder_augmented}' tidak ditemukan. Pastikan Anda sudah menjalankan skrip augmentasi.")
else:
    for nama_file_augmented in os.listdir(folder_augmented):
        if nama_file_augmented.endswith(('.jpg', '.jpeg', '.png')):
            data_untuk_csv.append([nama_file_augmented, string_kunci_jawaban_diarsir])

    if data_untuk_csv:
        with open(file_output_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_untuk_csv)
        print(f"File '{file_output_csv}' berhasil dibuat dengan {len(data_untuk_csv)} baris data.")
        print(f"Semua gambar menggunakan ground truth jawaban yang ditandai (sesuai kunci ujian): {string_kunci_jawaban_diarsir}")
    else:
        print(f"Tidak ada file gambar ditemukan di folder '{folder_augmented}'.")