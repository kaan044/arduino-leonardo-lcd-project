import requests
import serial
import time
import json
import sys

# --- AYARLAR ---
OHM_IP = 'http://localhost:8085/data.json'
COM_PORT = 'COM3'  # <--- PORTUNU KONTROL ET
BAUD_RATE = 9600

print(f"--- BAŞLATILIYOR ({COM_PORT}) ---")

# Serial Bağlantı Testi
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("✅ Arduino Bağlantısı BAŞARILI!")
except Exception as e:
    print(f"❌ ARDUINO HATASI: {e}")
    print("Çözüm: Başka bir Python penceresi açıksa kapat, port numarasını kontrol et.")
    input("Kapatmak için Enter...")
    sys.exit()

def get_sensor_value(data, hardware_name, group_name, sensor_name):
    """
    Verilen donanım ve sensörü JSON içinde arar.
    Bulamazsa 'BULUNAMADI' döndürür.
    """
    if 'Children' in data:
        for hardware in data['Children'][0]['Children']:
            if hardware_name in hardware['Text']:
                for group in hardware['Children']:
                    if group['Text'] == group_name:
                        for sensor in group['Children']:
                            if sensor['Text'] == sensor_name:
                                raw_value = sensor['Value']
                                # Temizlik yap
                                clean_value = raw_value.replace(' °C', '').replace(' %', '').replace(',', '.')
                                # RAM için bazen "GB" gelebilir, onu da temizleyelim
                                clean_value = clean_value.replace(' GB', '').replace(' RPM', '')
                                return clean_value.split('.')[0]
    return None

print("Veri okunuyor... (Durdurmak için pencereyi kapat)")

while True:
    try:
        response = requests.get(OHM_IP)
        data = response.json()
        
        # 1. CPU
        cpu = get_sensor_value(data, "AMD Ryzen 5 5500", "Temperatures", "CPU Package")
        if cpu is None: print("⚠️ UYARI: CPU verisi bulunamadı!"); cpu = "0"
        
        # 2. GPU
        gpu = get_sensor_value(data, "AMD Radeon RX 6600", "Temperatures", "GPU Core")
        if gpu is None: print("⚠️ UYARI: GPU verisi bulunamadı!"); gpu = "0"
        
        # 3. RAM (İsmi 'Memory' olarak geçiyor)
        ram = get_sensor_value(data, "Generic Memory", "Load", "Memory")
        if ram is None: print("⚠️ UYARI: RAM verisi bulunamadı!"); ram = "0"

        # Ekrana yazdır (Hata ayıklamak için)
        print(f"OKUNAN -> CPU: {cpu}°C | GPU: {gpu}°C | RAM: %{ram}")

        # Arduino Formatı
        line1 = f"CPU:{cpu}C GPU:{gpu}C"
        line2 = f"RAM: %{ram}"
        to_send = f"{line1};{line2}\n"
        
        ser.write(to_send.encode('utf-8'))
        
        time.sleep(1)

    except requests.exceptions.ConnectionError:
        print("❌ HATA: OpenHardwareMonitor'a bağlanılamıyor! Program açık mı?")
        time.sleep(2)
    except Exception as e:
        print(f"❌ BEKLENMEYEN HATA: {e}")
        time.sleep(1)