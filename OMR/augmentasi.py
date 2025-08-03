import cv2
import numpy as np
import os
import random

# --- Konfigurasi ---
folder_ljk_dasar = 'ljkdasar' # Folder tempat Anda menyimpan ljk_dasar_kunci_1.jpg & ljk_dasar_kunci_2.jpg
folder_output_augmented = 'dataset_uji_augmented' # Folder untuk menyimpan hasil augmentasi
jumlah_augmentasi_per_gambar_dasar = 15 # Target augmentasi untuk setiap gambar dasar

# Pastikan folder output ada, jika tidak buat folder tersebut
if not os.path.exists(folder_output_augmented):
    os.makedirs(folder_output_augmented)

# --- Fungsi-fungsi Augmentasi (Sama seperti sebelumnya) ---

def augment_rotate(image, angle_range=(-5, 5)):
    """Rotasi gambar dengan sudut acak dalam rentang tertentu."""
    angle = random.uniform(angle_range[0], angle_range[1])
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
    return rotated, f"rot{int(angle)}"

def augment_brightness_contrast(image, alpha_range=(0.8, 1.2), beta_range=(-20, 20)):
    """Mengubah kecerahan (beta) dan kontras (alpha) gambar."""
    alpha = random.uniform(alpha_range[0], alpha_range[1]) # Kontras
    beta = random.randint(beta_range[0], beta_range[1])   # Kecerahan
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted, f"bc_a{alpha:.1f}_b{beta}"

def augment_gaussian_noise(image, mean=0, var_range=(10, 50)):
    """Menambahkan noise Gaussian pada gambar."""
    sigma = random.uniform(var_range[0], var_range[1]) ** 0.5
    # Pastikan gambar memiliki 3 channel jika inputnya grayscale dari awal
    if len(image.shape) == 2: # Jika grayscale
        row, col = image.shape
        ch = 1
        image = image.reshape(row, col, ch) # Ubah bentuk agar bisa ditambah noise
    elif len(image.shape) == 3:
        row, col, ch = image.shape
    else: # Tidak terduga
        print("Format gambar tidak didukung untuk noise")
        return image, "noise_error"
        
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    
    noisy_img_float = image.astype(np.float32) + gauss # Tambah noise ke float image
    noisy = np.clip(noisy_img_float, 0, 255).astype(np.uint8)

    if ch == 1: # Kembalikan ke grayscale jika aslinya grayscale
        noisy = noisy.reshape(row,col)
    return noisy, f"noise{int(sigma**2)}"

def augment_slight_perspective(image, max_offset=15):
    """Memberikan sedikit distorsi perspektif."""
    # Pastikan gambar berwarna untuk warpPerspective dengan borderValue 3 channel
    if len(image.shape) == 2:
        image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        image_color = image

    rows, cols, _ = image_color.shape
    
    pts1 = np.float32([[0,0],[cols-1,0],[0,rows-1],[cols-1,rows-1]])
    offsets = np.random.randint(-max_offset, max_offset, size=(4,2)).astype(np.float32)
    pts2 = pts1 + offsets
    
    for i in range(4):
        pts2[i,0] = np.clip(pts2[i,0], 0, cols-1)
        pts2[i,1] = np.clip(pts2[i,1], 0, rows-1)

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(image_color, matrix, (cols, rows), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
    
    # Jika gambar asli grayscale, kembalikan hasil warp ke grayscale
    if len(image.shape) == 2:
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
    return warped, "persp_slight"

# --- Proses Utama Augmentasi ---

list_gambar_dasar = [f for f in os.listdir(folder_ljk_dasar) if f.endswith(('.jpg', '.jpeg', '.png'))]

if not list_gambar_dasar:
    print(f"Tidak ada gambar ditemukan di folder '{folder_ljk_dasar}'. Pastikan Anda sudah menempatkan LJK dasar di sana.")
else:
    print(f"Ditemukan {len(list_gambar_dasar)} gambar dasar untuk di-augmentasi.")

for nama_file_dasar in list_gambar_dasar:
    path_gambar_dasar = os.path.join(folder_ljk_dasar, nama_file_dasar)
    image_dasar = cv2.imread(path_gambar_dasar) # Baca sebagai gambar berwarna secara default

    if image_dasar is None:
        print(f"Gagal membaca gambar: {path_gambar_dasar}")
        continue

    print(f"\nMemproses augmentasi untuk: {nama_file_dasar}")
    nama_tanpa_ekstensi = os.path.splitext(nama_file_dasar)[0]

    augment_functions = [
        augment_rotate,
        augment_brightness_contrast,
        augment_gaussian_noise,
        augment_slight_perspective
    ]
    
    generated_count = 0
    # Untuk menghindari duplikasi nama file jika augmentasi sama persis (meski kecil kemungkinannya)
    # kita bisa menambahkan counter unik
    unique_counter_for_file = 0 

    while generated_count < jumlah_augmentasi_per_gambar_dasar:
        temp_image = image_dasar.copy()
        
        num_ops_to_apply = random.randint(1, 2) 
        selected_ops = random.sample(augment_functions, num_ops_to_apply)
        
        applied_ops_names = []
        for op_func in selected_ops:
            temp_image, op_name_suffix = op_func(temp_image)
            applied_ops_names.append(op_name_suffix)
        
        # Tambahkan unique_counter_for_file untuk memastikan nama file selalu unik
        nama_file_augmented = f"{nama_tanpa_ekstensi}_{'_'.join(applied_ops_names)}_{unique_counter_for_file}.jpg"
        path_output = os.path.join(folder_output_augmented, nama_file_augmented)
        
        cv2.imwrite(path_output, temp_image)
        # print(f"  -> Dihasilkan: {nama_file_augmented}") # Bisa di-uncomment jika ingin lihat proses
        generated_count += 1
        unique_counter_for_file +=1

print(f"\nProses augmentasi selesai. {len(list_gambar_dasar) * jumlah_augmentasi_per_gambar_dasar} gambar augmented disimpan di folder '{folder_output_augmented}'.")