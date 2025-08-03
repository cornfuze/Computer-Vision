import cv2
import numpy as np
import os
import random

# --- Konfigurasi ---
folder_ljk_dasar = 'ljkdasar'  # Folder tempat LJK dasar Anda (ljk_dasar_kunci_1.jpg & ljk_dasar_kunci_2.jpg)
folder_output_rotasi = 'dataset_uji_rotasi' # Folder BARU untuk menyimpan hasil augmentasi rotasi
jumlah_augmentasi_rotasi_per_gambar = 15 # Target augmentasi rotasi untuk setiap gambar dasar

# Pastikan folder output ada, jika tidak buat folder tersebut
if not os.path.exists(folder_output_rotasi):
    os.makedirs(folder_output_rotasi)

# --- Fungsi Augmentasi Rotasi (Sama seperti sebelumnya) ---
def augment_rotate(image, angle_range=(-5, 5)): # Anda bisa mengubah angle_range jika perlu
    """Rotasi gambar dengan sudut acak dalam rentang tertentu."""
    angle = random.uniform(angle_range[0], angle_range[1])
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Menggunakan border putih agar area di luar gambar yang terotasi menjadi putih
    rotated = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
    return rotated, f"rot{int(angle)}"

# --- Proses Utama Augmentasi Rotasi ---

list_gambar_dasar = [f for f in os.listdir(folder_ljk_dasar) if f.endswith(('.jpg', '.jpeg', '.png'))]

if not list_gambar_dasar:
    print(f"Tidak ada gambar ditemukan di folder '{folder_ljk_dasar}'. Pastikan Anda sudah menempatkan LJK dasar di sana.")
else:
    print(f"Ditemukan {len(list_gambar_dasar)} gambar dasar untuk di-augmentasi dengan rotasi.")

for nama_file_dasar in list_gambar_dasar:
    path_gambar_dasar = os.path.join(folder_ljk_dasar, nama_file_dasar)
    image_dasar = cv2.imread(path_gambar_dasar)

    if image_dasar is None:
        print(f"Gagal membaca gambar: {path_gambar_dasar}")
        continue

    print(f"\nMemproses augmentasi rotasi untuk: {nama_file_dasar}")
    nama_tanpa_ekstensi = os.path.splitext(nama_file_dasar)[0]
    
    for i in range(jumlah_augmentasi_rotasi_per_gambar):
        temp_image = image_dasar.copy()
        
        # Terapkan hanya augmentasi rotasi
        rotated_image, op_name_suffix = augment_rotate(temp_image) # Anda bisa menyesuaikan angle_range di sini jika mau
        
        nama_file_augmented = f"{nama_tanpa_ekstensi}_{op_name_suffix}_{i}.jpg"
        path_output = os.path.join(folder_output_rotasi, nama_file_augmented)
        
        cv2.imwrite(path_output, rotated_image)
        # print(f"  -> Dihasilkan: {nama_file_augmented}") # Bisa di-uncomment jika ingin lihat proses

print(f"\nProses augmentasi rotasi selesai.")
print(f"{len(list_gambar_dasar) * jumlah_augmentasi_rotasi_per_gambar} gambar hasil augmentasi rotasi disimpan di folder '{folder_output_rotasi}'.")