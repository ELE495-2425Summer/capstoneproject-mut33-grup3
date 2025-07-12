

import os
import re
import json
import ctypes
import time
import subprocess
import socket
import ipaddress

import speech_recognition as sr
import google.generativeai as genai
import serial
import socketio
from gtts import gTTS

import tempfile
import numpy as np
from scipy.spatial.distance import cosine
from scipy.io.wavfile import write
from resemblyzer import VoiceEncoder, preprocess_wav
from speechbrain.pretrained import SpeakerRecognition
from speechbrain.utils.fetching import LocalStrategy
import torchaudio


# Google Gemini API anahtarını yapılandır
genai.configure(api_key="")  # Buraya kendi API anahtarınızı yazın

# Gemini modeli
model = genai.GenerativeModel('gemini-2.0-flash')

#  Parametre
THRESHOLD = 0.57
print(THRESHOLD)
#  Model yükle
encoder = VoiceEncoder()
speechbrain_model = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb",
    local_strategy=LocalStrategy.COPY
)

# ALSA uyarılarını bastır
def disable_alsa_warnings_completely():
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    try:
        asound = ctypes.cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(None)
    except Exception:
        pass

disable_alsa_warnings_completely()

"""
def sunucu_ip_bul(subnet,port=5000):
    for ip in ipaddress.IPv4Network(subnet, strict=False):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            if result == 0:
                print(f"Sunucu bulundu: {ip}")
                return str(ip)
        except Exception:
            continue
    print("Sunucu bulunamadı.")
    return None
def get_local_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        subnet = ".".join(ip.split(".")[:3]) + ".0/24"
        return subnet
    except Exception:
        return "1.239.216.0/24"
 """  
      
def sunucu_ip_dinle(port=54545, hedef_mesaj=b"ARAC_KONTROL_SUNUCU", timeout=50):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", port))
    sock.settimeout(timeout)
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == hedef_mesaj:
                print(f"Sunucu bulundu: {addr[0]}")
                return addr[0]
    except socket.timeout:
        print("Sunucu yayını alınamadı (timeout).")
        return None
       
        
# USB mikrofon index bul
def usb_mikrofon_index_bul():
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "USB" in name or "usb" in name:
            print(f"USB mikrofon bulundu: {name} (index: {index})")
            return index
    print("USB mikrofon bulunamadı, varsayılan cihaz kullanılacak.")
    return None

import json

def komutu_sifreli_array_olarak_dondur(turkce_komut):
    prompt = f"""
Aşağıdaki Türkçe robot komutunu, aşağıdaki kurallara göre sadece bir integer dizisine (array) çevir:
Aşağıdaki Türkçe robot komutunu, aşağıdaki kurallara göre sadece bir integer dizisine (array) çevir:
Yapamayacağı, yeteneklerini aşan durumlarda bunu da belirtmelisin.
Örneğin, "uçarak gidemem" veya "renk tespiti yapamam" gibi bir metin çıktısı verebilirsin. 
Eğer bir komut yeteneklerimin dışında ise ancak komutta başka geçerli komutlar da varsa,sırayla hepsini uygun formatta örneklerdeki gibi çıktı ver.

Kurallar:
- Komutlar: "ileri_git" → 0, "sola_don" → 1, "saga_don" → 2, "dur" → 3, "geri_dön" → 4
- Koşullar: "engel_yok" → 0, "engel_varsa" ve "engel_algilayana_kadar" → 1, "engelin_solundan_kurtul"  → 2, "engelin_sagindan_kurtul"  → 3
- Süre saniye cinsinden bir sayı olacak (örnek: "3 saniye" → 3)
- Şifreleme formatı: [komut_kodu, kosul_kodu, sure, 9]
- Eğer koşul belirtilmemişse "engel_yok" (yani 0) kabul et
- Eğer süre belirtilmemişse "0" kabul et
- "engelden kurtul" içeren komutlar zaten "engel algılayana kadar" koşulunu içerir, bu nedenle öncesinde ayrıca bu komutu ekleme
- "180 derece dön" komutu otomatik olarak "geri_dön" (4) ile eşlenir
- Merhaba araba, Merhaba, Selam araba ve benzeri komutuna tepki verme 
- Her şeyden önce komutu gelirse o komutu en başa koy, mesela her şeyden önce şunu yap gibi, ama önce komutu gelirse bunu o komutun bir öncesinde sıraya koy aşağıda örnekler var
- Kullanıcının istediği sıralamaya da dikkat et
- DİKKAT: Açıklama yapma, kod dışına metin ekleme. Sadece örneklerdeki formatta cevap ver. 


Örnekler:
Örnekler:
    "engelin üzerinden yürü": [["Yürüyemem."]],
    "çay demle": [["Çay demleyemem."]],
    "atla": [["Atlayamam."]],
    "uçarak 3 saniye ilerle": [["Uçamam."]],
    "yüzerek sağa dön": [["Yüzemem."]],
    "görünmez ol": [["Ben arabayım, görünürüm."]],
    "sekerek ilerle": [["Sekemem."]],
    "Merhaba zıpla": [["Zıplayamam."]],
    "engelin üzerinden zıpla": [["Zıplayamam."]],
    "renkleri algıla": [["Renkleri algılayamam."]],
    "fotoğraf çek": [["Fotoğraf çekemem."]],
    "konuş": [["Konuşamam."]],
    "dans et": [["Dans edemem."]],
    "Merhaba ışınlan": [["Işınlanamam."]],
    "yemek yap": [["Yemek yapamam."]],
    "kapıyı aç": [["Kapıyı açamam."]],
    "şarkı söyle": [["Şarkı söyleyemem."]],
    "göz kırp": [["Göz kırpamam."]],
    "havla": [["Havlayamam."]],
    "uçaktan atla": [["Atlayamam."]],
    "ev temizle": [["Ev temizleyemem."]],
    "kendini yok et": [["Bunu yapamam."]],
    "selfie çek": [["Selfie çekemem."]],
    "suyu ısıt": [["Suyu ısıtamam."]],
    "ışıkları aç": [["Işıkları açamam."]],
    "araba sür": [["Ben zaten bir arabayım."]],
    "uçan tekme at": [["Uçamam ve tekme atamam."]],
    "evcil hayvan ol": [["Evcil hayvan olamam."]],
    "insan ol": [["İnsan değilim, arabayım."]],
"2 saniye ileri git" → [[0, 0, 2, 9]]
"sağa dön" → [[2, 0, 0, 9]]
"1 saniye ilerle eğer engel görürsen sola dön" → [[0, 1, 1, 9], [1, 0, 0, 9]]
"engel görene kadar düz git sonra sağa dön sonra 9 saniye geri dön" → [[0, 1, 0, 9], [2, 0, 0, 9], [4, 0, 0, 9]]
"geri dön sonra 2 sn ilerle" → [[4, 0, 0, 9], [0, 0, 2, 9]]
"sağa dön sonra engel görene kadar düz git engel görünce sola dön 1 saniye düz git" → [[2, 0, 0, 9], [0, 1, 0, 9], [1, 0, 0, 9], [0, 0, 1, 9]]
"Merhaba sağa dön ama öncesinde 10 saniye düz git" → [[0, 0, 10, 9], [2, 0, 0, 9]]
"3 saniye düz git eğer engel çıkarsa sağa yönel sonra 1 saniye dümdüz ilerle" → [[0, 1, 3, 9], [2, 0, 0, 9], [0, 0, 1, 9]]
"Merhaba engel görene kadar düz git sonra 2 saniye geri ilerle sonra sola yönel" → [[0, 1, 0, 9], [4, 0, 2, 9], [1, 0, 0, 9]]
"engel görene kadar düz git sonra sağa yönel sonra 1 saniye düz git" → [[0, 1, 0, 9], [2, 0, 0, 9], [0, 0, 1, 9]]
"sağa dön 13 saniye ilerle ama önüne engel çıkarsa sağa dön ve dur" → [[2, 0, 0, 9], [0, 1, 13, 9], [2, 0, 0, 9], [3, 0, 1, 9]]
"sağa dön fakat öncesinde 19 saniye ileri git eğer önüne engel çıkarsa dur" → [[0, 1, 19, 9], [3, 0, 1, 9], [2, 0, 0, 9]]
"Selam engelin sagından sıyrıl  sonra 2 sn ilerle sonra geri dön" → [[0, 3, 0, 9], [0, 0, 2, 9], [4, 0, 0, 9]]
"engel algılayınca sağa dön" → [[0, 1, 0, 9], [2, 0, 0, 9]]
"engel algılayınca geri dön" →  [[0, 1, 0, 9], [4, 0, 0, 9]]
"engelin solundan kurtul sonra 2 sn ilerle sonra geri dön sonra 10 sn ilerle" → [[0, 2, 0, 9], [0, 0, 2, 9], [4, 0, 0, 9], [0, 0, 10, 9]]
"Merhaba önce dur sonra sağa dön sonra dola dön sonra 5 sn düz git " → [[3, 0, 0, 9], [2, 0, 0, 9], [1, 0, 0, 9], [0, 0, 5, 9]]
"geri dönüp sağa dön ilerle ama engel varsa sol taraftan kaçın" → [[4, 0, 0, 9], [2, 0, 0, 9], [0, 2, 0, 9]]
"1 sn öte git sonrasında etrafında 180 derece dön sonra dümdüz ilerle ama bir şey görürsen dur " → [[0, 0, 1, 9], [4, 0, 0, 9], [0, 1, 0, 9], [3, 0, 1, 9]]
" 5 saniye ilerle sağa dön ama öncesinde 3 saniye dur " → [[0, 0, 5, 9], [3, 0, 1, 9], [2, 0, 0, 9]]
" 5 saniye ilerle sağa dön ama herşeyden önce 3 saniye dur " → [[3, 0, 1, 9], [0, 0, 5, 9], [2, 0, 0, 9]]
"3 saniye ilerle sonra dans et sonra dur" → [[0, 0, 3, 9], ["Dans edemem"], [3, 0, 0, 9]]

"Sağın tersine dön" → [[1, 0, 0, 9]]

"Solun tersine dön" → [[2, 0, 0, 9]]

"sağa dön 5 saniye ilerle çay demle sonra geri dön" → [[2, 0, 0, 9], [0, 0, 5, 9], ["Çay demleyemem."], [4, 0, 0, 9]]

"engel algılayana kadar düz git fotoğraf çek sonra sola dön" → [[0, 1, 0, 9], ["Fotoğraf çekemem."], [1, 0, 0, 9]]

"10 saniye geri git zıpla sonra dur" → [[4, 0, 10, 9], ["Zıplayamam."], [3, 0, 0, 9]]


"ileri git sonra şarkı söyle sonra sağa dön" → [[0, 0, 0, 9], ["Şarkı söyleyemem."], [2, 0, 0, 9]]


"konuş ve sonra ileri git" → [["Konuşamam."], [0, 0, 0, 9]]

"1 saniye ileri git sonra ev temizle sonra dur" → [[0, 0, 1, 9], ["Ev temizleyemem."], [3, 0, 0, 9]]

"Uç sonra yüz 1 saniye ileri git" → [["uçamam."], ["yüzemem."], [0, 0, 1, 9]]



Komut: "{turkce_komut}"
Cevap:
"""
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        print("Gemini API çağrısı başarısız oldu:", e)
        return [["Gemini API hatası"]]

    try:
        try:
            response_text = response.text.strip()
        except AttributeError:
            response_text = response.candidates[0].content.parts[0].text.strip()
            return [["Anlayamadım"]]

        # Kod bloğu içinden sadece içerik çek (``` kod etiketi varsa)
        if "```" in response_text:
            response_text = response_text.split("```")[1].strip()

        # JSON dizisi gibi görünüyor mu?
        if response_text.startswith("[") and response_text.endswith("]"):
            try:
                parsed = json.loads(response_text)
            except Exception as e:
                print("JSON parse hatası:", e)
                return [["Cevap çözülemedi"]]

            # ✅ Format kontrolü
            def is_gecerli_model_cevabi(veri):
                if isinstance(veri, list):
                    for eleman in veri:
                        if isinstance(eleman, list):
                            if len(eleman) == 4 and all(isinstance(x, int) for x in eleman):
                                continue
                            elif len(eleman) == 1 and isinstance(eleman[0], str):
                                continue
                            else:
                                return False
                        else:
                            return False
                    return True
                return False

            if is_gecerli_model_cevabi(parsed):
                return parsed
            else:
                print("Geçersiz model cevabı formatı:", parsed)
                return [["Geçersiz format"]]
        else:
            # Düz string dönerse yine liste içine alınarak dönsün
            return [[response_text.strip()]]

    except Exception as e:
        print("Genel parse hatası:", e)
        print("Model cevabı:\n", response_text)
        return [["Genel hata"]]


# Komutu sesli olarak al

# Test edilecek komutlar




def google_tts_konus(metin, dosya_adi="tts_cikti.mp3"):
    try:
        # Eğer metin listeyse sadece ilk elemanı kullan
        if isinstance(metin, list):
            metin = metin[0]
        tts = gTTS(text=metin, lang="tr")
        tts.save(dosya_adi)
        subprocess.run(["mpg123", dosya_adi])
        os.remove(dosya_adi)
    except Exception as e:
        print("TTS hatası:", e)

def harf_var_mi(liste):
    for eleman in liste:
        if isinstance(eleman, str) and any(char.isalpha() for char in eleman):
            return True
    return False

#  Normalize
def normalize_vector(v):
    return v / np.linalg.norm(v)

# Embedding çıkar
def get_combined_embedding(file_path):
    wav = preprocess_wav(file_path)
    emb_res = normalize_vector(encoder.embed_utterance(wav))

    signal, fs = torchaudio.load(file_path)
    if fs != 16000:
        signal = torchaudio.transforms.Resample(orig_freq=fs, new_freq=16000)(signal)
    emb_sb = speechbrain_model.encode_batch(signal).squeeze().detach().numpy()
    emb_sb = normalize_vector(emb_sb)

    return normalize_vector(np.concatenate([emb_res, emb_sb]))

mean_embeddings = np.load("mean_embeddings_rasperry.npy", allow_pickle=True).item()

def komut_dinle():
    #İBO#
    global motor_durum
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    if not motor_durum:
        print("Motor durduruldu1, dinleme iptal edildi.")
        return None, None

    while motor_durum:
        print("Lütfen konuşun...")
        with mic as source:
            r.adjust_for_ambient_noise(source,duration=1.5)
            r.pause_threshold = 1.2
            try:
                audio = r.listen(source, timeout = 10)
            except sr.WaitTimeoutError:
                google_tts_konus("Konuşma algılanmadı.")
                if not motor_durum:
                    print("Motor durduruldu2, dinleme iptal edildi.")
                    return None, None

                continue
            except Exception as e:
                print("Dinleme hatası:", e)
                return None, None
        # Eğer bu noktaya geldiyse, ama motor kapatılmışsa işlemi bitir
        if not motor_durum:
            print("Motor durduruldu3, dinleme iptal edildi.")
            return None, None
    #İBO
    
        # Embedding oluştur
        try:
            raw_audio = audio.get_raw_data()
            np_audio = np.frombuffer(raw_audio, dtype=np.int16)
            wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            write(wav_path, 44100, np_audio)
        except Exception as e:
            print("Ses dosyasını işleme hatası:", e)
            return None, None
    
        try:
            test_emb = get_combined_embedding(wav_path)
        except Exception as e:
            print(f"Embedding oluşturulamadı: {e}")
            continue

        similarities = {
            name: 1 - cosine(mean_emb, test_emb)
            for name, mean_emb in mean_embeddings.items()
        }

        best_match = max(similarities, key=similarities.get)
        confidence = similarities[best_match]
        print(f"Tanınma oranı: {confidence:.3f} ({best_match})")

        if confidence > THRESHOLD:
            print(f"Konuşan kişi tanındı: {best_match}")
            try:
                with sr.AudioFile(wav_path) as source:
                    audio = r.record(source)
                    command = r.recognize_google(audio, language="tr-TR")
                    print(" Komut:", command)
                    return best_match, command
            except sr.UnknownValueError:
                print("Komut anlaşılamadı.")
                    
                return best_match, None
                
            except sr.RequestError as e:
                print(f"Google API hatası: {e}")
                return best_match, None
        else:
            subprocess.run(["mpg123", "taniyamadim.mp3"])
            print("Kişi tanınmadı. Tekrar deneyin.\n")
            return None, None 

def sesli_geribildirim(komut):
    if komut[0]==0:
        subprocess.run(["mpg123", "ilerliyorum.mp3"])
    elif komut[0]==1:
        subprocess.run(["mpg123", "sola_don.mp3"])
    elif komut[0]==2:
        subprocess.run(["mpg123", "saga_don.mp3"])
    elif komut[0]==3:
        subprocess.run(["mpg123", "Durdum.mp3"])
    elif komut[0]==4:
        subprocess.run(["mpg123", "geridonu.mp3"])
    else:
        print("Tanımsız komut:", komut)

def kisi_seslendirme(komut):
    if komut=="ibrahim":
        subprocess.run(["mpg123", "ibrahim.mp3"])
    elif komut=="emre":
        subprocess.run(["mpg123", "Emre.mp3"])
    elif komut=="osman":
        subprocess.run(["mpg123", "Osman.mp3"])
    elif komut=="melih":
        subprocess.run(["mpg123", "Melih.mp3"])
    elif komut=="baris":
        subprocess.run(["mpg123", "baris.mp3"])
    else:
        print("Tanımsız komut:", komut)


import time
import serial

####IBO#####

# WebSocket istemcisi ile bağlan
sio = socketio.Client()

# Motor durumu
motor_durum = False  # Başlangıçta motor kapalı

# WebSocket event: Motoru aç veya kapat
@sio.on('komut_gonder')
def komut_alindi(data):
    global motor_durum
    
    if data['hareket'] == 'motor':
        subprocess.run(["mpg123", "car_engine.mp3"])
        
        motor_durum = True
        print("Motor on state.")

    else:
        motor_durum= False
        print("Motor off state.")
        
        subprocess.run(["mpg123", "car_stop.mp3"])
        
    
try:
	"""
    #sunucu_ip = sunucu_ip_bul()
    subnet = get_local_subnet()
    print(subnet)
    sunucu_ip = sunucu_ip_bul(subnet, port=5000)
    if sunucu_ip:
        sio.connect(f"http://{sunucu_ip}:5000")
    else:
        print("Sunucuya bağlanılamadı.")
     """
	sunucu_ip = sunucu_ip_dinle()

	if sunucu_ip:
		#sio = socketio.Client()
		try:
			sio.connect(f"http://{sunucu_ip}:5000")
			google_tts_konus("Sunucuya bağlanıldı.")
		except Exception as e:
			print("Sunucu Bağlantı hatası:")
	else:
		print("Sunucu IP’si bulunamadı.")
except Exception as e:
    print("WebSocket bağlantı hatası:", e)


komut_adi = {
    0: "İleri Git",
    1: "Sola Dön",
    2: "Sağa Dön",
    3: "Dur",
    4: "Geri Git"
}

def is_gecerli_model_cevabi(veri):
    if not veri:
        return False  # None veya []

    if isinstance(veri, list):
        # 1. Tek bir açıklama metni
        if len(veri) == 1 and isinstance(veri[0], str):
            text = veri[0].strip()
            if not text:
                return False
            # String içinde JSON array varsa?
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list) and all(
                    isinstance(i, list) and len(i) == 4 and all(isinstance(x, int) for x in i)
                    for i in parsed
                ):
                    return True
            except:
                pass
            return True  # Gerçek açıklama

        # 2. Liste liste integer komutlar
        elif all(isinstance(alt, list) and len(alt) == 4 and all(isinstance(x, int) for x in alt) for alt in veri):
            return True

    return False


    
####IBO#####
if __name__ == "__main__":
    subprocess.run(["mpg123", "acildim.mp3"])
    while(1):

        if motor_durum:

            subprocess.run(["mpg123", "sizidinliyorum.mp3"])

            kisi, komut_metni = komut_dinle()

            if kisi is None and komut_metni is None:
                continue  # başa dön, tekrar motorun açılmasını bekle

            if komut_metni:

                json_komutlar = komutu_sifreli_array_olarak_dondur(komut_metni)
                print(json_komutlar)

                '''
                #not isinstance(json_komutlar, list) or   
                if not is_gecerli_model_cevabi(json_komutlar):
                    print("Gelen komutlar2")
                    if kisi == "ibrahim":
                        subprocess.run(["mpg123", "ibrahim_anlamadim.mp3"])
                    elif kisi == "emre":
                        subprocess.run(["mpg123", "emre_anlamadim.mp3"])
                    elif kisi == "osman":
                        subprocess.run(["mpg123", "osman_anlamadim.mp3"])
                    elif kisi == "melih":
                        subprocess.run(["mpg123", "melih_anlamadim.mp3"])
                    elif kisi == "baris":
                        subprocess.run(["mpg123", "baris_anlamadim.mp3"])
                    continue  # Sonraki komuta geç
                '''

                print("Gelen komutlar:", json_komutlar)

                kisi_seslendirme(kisi)
                print(json_komutlar)
                
                PORT = "/dev/ttyUSB0"  # veya "/dev/ttyACM0"
                try:
                    SerialObj = serial.Serial(
                        port=PORT,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=0  # Non-blocking modda çalışacak
                    )

                    time.sleep(3)  # Seri bağlantının oturması için bekleme

                    for i, sifre in enumerate(json_komutlar):
                        print(f"\n{i+1}. komut gönderiliyor: {sifre}")
                        if harf_var_mi(sifre):
                            google_tts_konus(sifre)

                            ##IBO##
                            durum = {
                                "komut_metni": komut_metni,
                                "hareket": f"{sifre}",
                                "sifre": "-",
                                "kisi": kisi,
                                "zaman": time.time()
                            }
                            try:
                                sio.emit("durum_gonder", durum)
                                print("Gönderildi:", durum)
                            except Exception as e:
                                print("WebSocket'e gönderilemedi:", e)
                            ##IBO##

                            continue

                        sesli_geribildirim(sifre)  # Sesli geri bildirim gönderimden sonra
                        bytes_written = SerialObj.write(bytearray(sifre))

                        ##IBO##
                        durum = {
                            "komut_metni": komut_metni,
                            "hareket": komut_adi.get(sifre[0], f"Bilinmeyen Komut ({sifre[0]})"),
                            "sifre": sifre,
                            "kisi": kisi,
                            "zaman": time.time()
                        }
                        try:
                            sio.emit("durum_gonder", durum)
                            print("Gönderildi:", durum)
                        except Exception as e:
                            print("WebSocket'e gönderilemedi:", e)
                        ##IBO##

                        print(f"{bytes_written} byte gönderildi")

                        # Arduino'dan '1' cevabını bekle (max 10 saniye boyunca)
                        max_bekleme = 18
                        baslangic = time.time()
                        yanit = None

                        while True:
                            if SerialObj.in_waiting > 0:
                                yanit = SerialObj.read(1)
                                break
                            if time.time() - baslangic > max_bekleme:
                                break
                            time.sleep(0.1)

                        if yanit == b'\x01':
                            print("Arduino: İşlem tamamlandı, sıradaki komut gönderilecek.")

                            final_durum = {
                                "komut_metni": komut_metni,
                                "hareket": "Komut tamamlandı",
                                "sifre": sifre,
                                "kisi": kisi,
                                "zaman": time.time()
                            }
                            try:
                                sio.emit("durum_gonder", final_durum)
                                print("Son durum gönderildi:", final_durum)
                            except Exception as e:
                                print("Final durum WebSocket'e gönderilemedi:", e)

                        else:
                            print(f"Beklenen '1' cevabı alınamadı, gelen: {yanit}")
                            final_durum = {
                                "komut_metni": komut_metni,
                                "hareket": "Komut başarısız",
                                "sifre": sifre,
                                "kisi": kisi,
                                "zaman": time.time()
                            }
                            try:
                                sio.emit("durum_gonder", final_durum)
                                print("Son durum gönderildi:", final_durum)
                            except Exception as e:
                                print("Final durum WebSocket'e gönderilemedi:", e)
                            break

                except serial.SerialException as e:
                    print(f"Seri port hatası: {e}")

                finally:
                    if 'SerialObj' in locals() and SerialObj.is_open:
                        SerialObj.close()
                        print("Seri port kapatıldı.")




                
