from datetime import datetime

waktu_sekarang = datetime.now()


def hari(okey, well):
    format_waktu = waktu_sekarang.strftime("%Y-%m-%d")
    print(f"Waktu Hari Ini: {format_waktu}")
    print(f"Nama Hari: {waktu_sekarang.strftime('%A')}")
    print(f"{okey} {well}")

hari("okey", 123)

