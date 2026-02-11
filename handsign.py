import cv2
import time
import os
import sys
import pygame
from gtts import gTTS

# --- 1. SETUP MEDIAPIPE ---
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except ImportError:
    print("Error: Library belum terinstall. Jalankan 'pip install mediapipe opencv-python gTTS pygame'")
    sys.exit()

# --- 2. KAMUS DATA 31 KOMBINASI (SESUAI REQUEST) ---
# Format: ID: "Keterangan Jari"
# Kode Jari: 1=Kelingking, 2=Manis, 3=Tengah, 4=Telunjuk, 5=Jempol
DESKRIPSI_GESTUR = {
    1: "[1] Kelingking",
    2: "[2] Manis",
    3: "[3] Tengah",
    4: "[4] Telunjuk",
    5: "[5] Jempol",
    6: "[1,2] Kelingking + Manis",
    7: "[1,3] Kelingking + Tengah",
    8: "[1,4] Kelingking + Telunjuk",
    9: "[1,5] Kelingking + Jempol",
    10: "[2,3] Manis + Tengah",
    11: "[2,4] Manis + Telunjuk",
    12: "[2,5] Manis + Jempol",
    13: "[3,4] Tengah + Telunjuk",
    14: "[3,5] Tengah + Jempol",
    15: "[4,5] Telunjuk + Jempol",
    16: "[1,2,3] Kelingking + Manis + Tengah",
    17: "[1,2,4] Kelingking + Manis + Telunjuk",
    18: "[1,2,5] Kelingking + Manis + Jempol",
    19: "[1,3,4] Kelingking + Tengah + Telunjuk",
    20: "[1,3,5] Kelingking + Tengah + Jempol",
    21: "[1,4,5] Kelingking + Telunjuk + Jempol",
    22: "[2,3,4] Manis + Tengah + Telunjuk",
    23: "[2,3,5] Manis + Tengah + Jempol",
    24: "[2,4,5] Manis + Telunjuk + Jempol",
    25: "[3,4,5] Tengah + Telunjuk + Jempol",
    26: "[1,2,3,4] Kelingking + Manis + Tengah + Telunjuk",
    27: "[1,2,3,5] Kelingking + Manis + Tengah + Jempol",
    28: "[1,2,4,5] Kelingking + Manis + Telunjuk + Jempol",
    29: "[1,3,4,5] Kelingking + Tengah + Telunjuk + Jempol",
    30: "[2,3,4,5] Manis + Tengah + Telunjuk + Jempol",
    31: "[1,2,3,4,5] FULL (Semua Jari)"
}

# Mapping Tuple Jari Aktif ke Nomor ID (Logic Mesin)
# Tuple harus urut (sorted)
LOGIC_MAP = {
    (1,): 1, (2,): 2, (3,): 3, (4,): 4, (5,): 5,
    (1, 2): 6, (1, 3): 7, (1, 4): 8, (1, 5): 9,
    (2, 3): 10, (2, 4): 11, (2, 5): 12,
    (3, 4): 13, (3, 5): 14,
    (4, 5): 15,
    (1, 2, 3): 16, (1, 2, 4): 17, (1, 2, 5): 18,
    (1, 3, 4): 19, (1, 3, 5): 20,
    (1, 4, 5): 21,
    (2, 3, 4): 22, (2, 3, 5): 23,
    (2, 4, 5): 24,
    (3, 4, 5): 25,
    (1, 2, 3, 4): 26, (1, 2, 3, 5): 27, (1, 2, 4, 5): 28,
    (1, 3, 4, 5): 29,
    (2, 3, 4, 5): 30,
    (1, 2, 3, 4, 5): 31
}

class HandSignSystem:
    def __init__(self, user_text_mapping):
        self.user_text_mapping = user_text_mapping # ID -> Teks Suara
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Setup Audio
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        self.generate_audio_cache()
        
        self.last_trigger_time = 0
        self.cooldown = 2.5 # Detik jeda antar suara
        self.current_subtitle = "Menunggu Gestur..."

    def generate_audio_cache(self):
        """Membuat file MP3 di awal agar tidak delay saat runtime"""
        if not os.path.exists("cache_31"):
            os.makedirs("cache_31")
            
        print("\n[SYSTEM] Memproses Audio Cache...")
        for gesture_id, text in self.user_text_mapping.items():
            filename = f"cache_31/sound_{gesture_id}.mp3"
            if not os.path.exists(filename):
                print(f"  -> Generate suara ID {gesture_id}: '{text}'")
                try:
                    tts = gTTS(text=text, lang='id')
                    tts.save(filename)
                except Exception as e:
                    print(f"  [Error TTS] {e}")
        print("[SYSTEM] Audio Siap.\n")

    def play_sound(self, gesture_id):
        self.current_subtitle = self.user_text_mapping[gesture_id]
        filename = f"cache_31/sound_{gesture_id}.mp3"
        if os.path.exists(filename):
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

    def detect_fingers(self, lms):
        """
        Deteksi jari mana yang aktif.
        Return: Tuple urut (misal: (1, 4, 5))
        """
        active_fingers = []
        
        # 1. JEMPOL (ID 5) - Cek Horizontal
        # Asumsi tangan kanan menghadap kamera (mirroring nanti diatur)
        if lms.landmark[4].x < lms.landmark[3].x:
            active_fingers.append(5)
            
        # 2. JARI LAIN (4=Telunjuk, 3=Tengah, 2=Manis, 1=Kelingking) - Cek Vertikal
        # Tip ID: [8, 12, 16, 20]
        # PIP ID: [6, 10, 14, 18]
        # Mapping Index Loop ke ID Jari Kita: 0->4, 1->3, 2->2, 3->1
        finger_ids = [4, 3, 2, 1] 
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for i in range(4):
            # Jika Ujung Jari lebih tinggi (nilai Y lebih kecil) dari ruas tengah
            if lms.landmark[tips[i]].y < lms.landmark[pips[i]].y:
                active_fingers.append(finger_ids[i])
                
        return tuple(sorted(active_fingers))

def setup_menu():
    """Menu Interaktif Pengisian Teks"""
    user_map = {}
    print("="*50)
    print("   KONFIGURASI SUARA 31 KOMBINASI")
    print("="*50)
    print("Ketik nomor ID gestur untuk mengisi teks suara.")
    print("Ketik 'list' untuk melihat daftar 1-31.")
    print("Ketik 'run' jika sudah selesai.")
    print("-" * 50)

    while True:
        pilih = input(">> Masukkan Nomor ID / Perintah: ").lower().strip()
        
        if pilih == 'run':
            if not user_map:
                print("⚠️ Belum ada gestur yang diisi! Isi minimal satu.")
                continue
            break
            
        elif pilih == 'list':
            print("\nDAFTAR GESTUR:")
            for k, v in DESKRIPSI_GESTUR.items():
                status = "[SUDAH DIISI]" if k in user_map else ""
                print(f" {k}. {v} {status}")
            print("")
            
        elif pilih.isdigit():
            idx = int(pilih)
            if idx in DESKRIPSI_GESTUR:
                print(f"Gestur Dipilih: {DESKRIPSI_GESTUR[idx]}")
                teks = input(f"Masukkan teks ucapan untuk ID {idx}: ")
                if teks:
                    user_map[idx] = teks
                    print(f"✅ Disimpan: ID {idx} -> '{teks}'\n")
            else:
                print("❌ Nomor tidak valid (1-31).")
        else:
            print("❌ Perintah tidak dikenal.")
            
    return user_map

def main():
    # 1. Jalankan Setup Dulu
    gestur_data = setup_menu()
    
    # 2. Inisialisasi Sistem
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    bot = HandSignSystem(gestur_data)
    
    print("\n[INFO] Tekan 'Q' untuk keluar.")
    print("[INFO] Tunjukkan tangan kanan Anda ke kamera.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Mirroring (Penting agar logika Jempol benar)
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = bot.hands.process(rgb)
        
        detected_id = None
        detected_desc = ""

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
                
                # Dapatkan kombinasi jari aktif (Tuple)
                fingers = bot.detect_fingers(hand_lms)
                
                # Cari ID-nya di Logic Map (1-31)
                if fingers in LOGIC_MAP:
                    detected_id = LOGIC_MAP[fingers]
                    detected_desc = DESKRIPSI_GESTUR[detected_id]
                    
                    # Cek apakah ID ini punya teks suara dari user?
                    if detected_id in bot.user_text_mapping:
                        now = time.time()
                        if now - bot.last_trigger_time > bot.cooldown:
                            print(f"🔊 Trigger ID {detected_id}: {bot.user_text_mapping[detected_id]}")
                            bot.play_sound(detected_id)
                            bot.last_trigger_time = now

        # --- TAMPILAN UI ---
        # Background Header
        cv2.rectangle(frame, (0, 0), (1280, 80), (0, 0, 0), -1)
        
        # Teks Subtitle Suara
        cv2.putText(frame, f"SUARA: {bot.current_subtitle}", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Info Debug (Kombinasi Jari yg Terdeteksi)
        if detected_desc:
            cv2.putText(frame, f"DETEKSI: {detected_desc}", (20, 700), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Jarvis 31 Gestur", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()  