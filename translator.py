import tkinter as tk
import tempfile 
import os
from datetime import datetime #zaman ekleme
from PIL import Image, ImageTk
from tkinter import ttk
from playsound import playsound
from PIL import Image, ImageTk
from gtts import gTTS  # bu satırda da text to speech (konuşma) kütüphane ekleme
from deep_translator import GoogleTranslator # google translate import ekleme

tts_languages = { # destekli diller fonksiyonu
    "Turkish": "tr",
    "English": "en",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it",
    "Arabic": "ar",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
}


# Translator örneği ile desteklenen dilleri al
translator = GoogleTranslator(source='auto', target='en')
raw_languages = translator.get_supported_languages(as_dict=True)


# Baş harfleri büyük yap, Otomatik Algıla ekle
readable_to_code = {"Otomatik Algıla": "auto"}
readable_to_code.update({lang.title(): code for lang, code in raw_languages.items()})

def get_language_names_with_icons():
    names = []
    for name in readable_to_code:
        if name in tts_languages:
            names.append(f"(Sesli) {name} ")
        else:
            names.append(name)
    return sorted(names)
        
language_names = get_language_names_with_icons()


# clean_lang_name adında bir fonksiyon tanımlıyoruz 
# nedeni de Combobox normal iconları tanımaz ve burada eğer icon varsa önceden temizler
def clean_lang_name(name):
    return name.replace("🔊", "").replace("(Sesli)", "").strip()

root = tk.Tk()
#buradaki 3 satır geçmiş çeviriler ile ilgili
history_frame = tk.Frame(root, width=180, height=360, bg="#303134", bd=2)
history_frame.place(x=1400, y=0)  # Başlangıçta ekran dışında
history_frame.pack_propagate(False)
root.geometry("1370x360")
root.configure(bg="#202124")
root.title("Expandable Translation Application")

source_lang_var = tk.StringVar(value="English")
target_lang_var = tk.StringVar(value="Turkish")

# Üst menü
top_frame = tk.Frame(root, bg="#202124")
top_frame.pack(pady=10)

def swap_languages():
    source = source_lang_var.get()
    target = target_lang_var.get()
    source_lang_var.set(target)
    target_lang_var.set(source)
    perform_translation()

swap_btn = tk.Button(top_frame, text="↔", command=swap_languages, bg="#202124", fg="white", relief="flat", font=("Arial", 14, "bold"))
swap_btn.grid(row=0, column=1, padx=5)

source_menu = ttk.Combobox(top_frame, textvariable=source_lang_var, values=language_names, state="readonly", width=20)
source_menu.grid(row=0, column=0, padx=10)

target_menu = ttk.Combobox(top_frame, textvariable=target_lang_var, values=language_names, state="readonly", width=20)
target_menu.grid(row=0, column=2, padx=10)

# Ana alan
main_frame = tk.Frame(root, bg="#202124")
main_frame.pack(pady=10)


input_box = tk.Text(main_frame, width=40, height=10,padx=10, pady=10,bd=0, font=("Arial", 14), bg="#303134", fg="white", insertbackground="white", wrap="word")
input_box.grid(row=0, column=0, padx=10)
input_box.bind("<KeyRelease>", lambda e: [trigger_translation(), update_char_counter(), limit_input_length()]) # gerekli bileşenler input_box içne eklenir

right_frame = tk.Frame(main_frame, bg="#303134", width=400, height=240)
right_frame.grid(row=0, column=1, padx=10)
right_frame.grid_propagate(False)

output_frame = tk.Frame(main_frame, bg="#303134")
output_frame.grid(row=0, column=1, padx=10)
#burada da çıkış kutusu var (saü kutu)
output_box = tk.Text(output_frame, width=40, height=10, font=("Arial", 14),
                     bg="#303134", fg="white", state="disabled", wrap="word",
                     bd=0, padx=10, pady=10)
output_box.pack()

# Kopyala butonu için görsel işlevi atama daha sonra bu button değerine verilecek
copy_img = Image.open("copy_icon.png").resize((23, 23))
copy_icon = ImageTk.PhotoImage(copy_img)


# tema iconu yükler | işlev temayı değştirmek
theme_img = Image.open("theme_icon.png").resize((22,22))
theme_icon = ImageTk.PhotoImage(theme_img)

# otomatik konuşma icon ekleme işlevi
listen_img = Image.open("volume_up.png").resize((24,24))
listen_icon = ImageTk.PhotoImage(listen_img)

# delete butonu ekleme
clear_img = Image.open("delete_icon.png").resize((26,26))
clear_icon = ImageTk.PhotoImage(clear_img)


#kaydetme iconu için gerekli değişkenler aşağıda verildi
saved_translations = [] # kaydedilen çeviriler burada tutulur
is_saved_panel_open = False # panel açık mı değil mi kontrol
saved_panel = None # panelin referansı


# kaydetme ve kaydedildi iconu için görsel yerleşimi
save_img = Image.open("add_to_save.png").resize((25, 25))  #PIL nesnesi burada yer alıyor bu satırda sadece bu nesne yer almak zorundadır (hata düzelttim
save_icon = ImageTk.PhotoImage(save_img)  # tkinter için uygun hale getirdim gerekli bileşen olarak da PIL aldım

#kaydedildi
saved_img = Image.open("added_to_save.png").resize((25, 25))
saved_icon = ImageTk.PhotoImage(saved_img)


# kaydedilenleri görme butonu için görsel yükleme
view_img = Image.open("added_to_save.png").resize((24, 24))
view_icon = ImageTk.PhotoImage(view_img)

# geçmiş butonu için görsel ekleme
history_icon = Image.open("history_icon.png").resize((24, 24))
history_icon = ImageTk.PhotoImage(history_icon)


current_theme = "dark" # referans renk dark|koyu olarak belirtildi
# tema ekleme/yenileme ve değiştirme işlemleri burada
def toggle_theme():
    global current_theme
    if current_theme == "dark":
        # Açık tema
        root.configure(bg="white")
        top_frame.configure(bg="white")
        main_frame.configure(bg="white")
        input_box.configure(bg="#303134", fg="white", insertbackground="black")
        output_box.configure(bg="#303134", fg="white")
        output_frame.configure(bg="white")
        status_label.configure(bg="white", fg="gray")
        copy_button.configure(bg="#303134", activebackground="#eee")
        clear_button.configure(bg="#303134", activebackground="#eee")
        listen_button.configure(bg="#303134", activebackground="#eee")
        theme_button.configure(bg="#303134", activebackground="#303134")
        view_button.configure(bg="#303134", activebackground="#303134")
        char_counter.configure(fg="gray", bg="white")
        current_theme = "light"
    else:
        # Karanlık tema
        root.configure(bg="#202124")
        top_frame.configure(bg="#202124")
        main_frame.configure(bg="#202124")
        input_box.configure(bg="#303134", fg="white", insertbackground="white")
        output_box.configure(bg="#303134", fg="white")
        output_frame.configure(bg="#303134")
        status_label.configure(bg="#202124", fg="gray")
        copy_button.configure(bg="#303134", activebackground="#3c4043")
        clear_button.configure(bg="#303134", activebackground="#3c4043")
        listen_button.configure(bg="#303134", activebackground="#3c4043")
        theme_button.configure(bg="#303134", activebackground="#303134")
        char_counter.configure(fg="gray", bg="#202124")

        current_theme = "dark"

def copy_to_clipboard():
    try:
        result = output_box.get("1.0", tk.END).strip()
        if not result:
            raise ValueError("Boş Metin")
        root.clipboard_clear()
        root.clipboard_append(result)
        status_label.config(text="Çeviri kopyalandı", fg="white")
        root.after(2000, lambda: status_label.config(text=""))
    except Exception as e:
        status_label.config(text="Çeviri kopyalanamadı", fg="white")
        print("Hata:", e)

# konuşma fonksiyonunu güncelleme kısmı burada
def speak_translation():
    try:
        text = output_box.get("1.0", tk.END).strip()
        if not text:
            raise ValueError("Boş metin")

        src = readable_to_code[clean_lang_name(source_lang_var.get())]
        tgt = readable_to_code[clean_lang_name(target_lang_var.get())]

        tts_lang = tts_languages.get(clean_lang_name(target_lang_var.get()), "en")
        tts = gTTS(text=text, lang=tts_lang)

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_audio.close()
        tts.save(temp_audio.name)

        playsound(temp_audio.name)
        os.remove(temp_audio.name)

    except Exception as e:
        print("Sesli okuma hatası:", e)
        status_label.config(text="Sesli okuma başarısız", fg="white")



icon_bar = tk.Frame(root, bg="#303134", width=100, height=35)
icon_bar.pack_propagate(False)
icon_bar.place(x=1000, y=0)

icon_bar2 = tk.Frame(root, bg="#303134", width=100, height=35)
icon_bar2.pack_propagate(False)
icon_bar2.place(x=240, y=330)

theme_button = tk.Button(icon_bar, image=theme_icon, command=toggle_theme, bg="#303134", bd=0, activebackground="#303134")
theme_button.image = theme_icon # burada referans tutuluyor
theme_button.pack(side="left", padx=5)

#kopyalama icon butonu ekleme
copy_button = tk.Button(output_frame, image=copy_icon, command=copy_to_clipboard,
                        bg="#303134", bd=0, activebackground="#3c4043")
copy_button.place(x=420, y=200)  # yaklaşık hizalama | position

# listen button ekleme
listen_button = tk.Button(output_frame, image=listen_icon, command=speak_translation,
                          bg="#303134", bd=0, activebackground="#3c4043")
listen_button.image = listen_icon
listen_button.place(x=340, y=202) # hizalama işlemleri | position

# ilk olarak kaydet iconu buttonu
save_button = tk.Button(output_frame, image=save_icon, command=lambda: save_translation(),
                        bg="#303134", bd=0, activebackground="#3c4044")
save_button.image = save_icon
save_button.place(x=300, y=201)


# kaydedilenleri görme  butonu 
view_button = tk.Button(icon_bar2, image=view_icon, command=lambda:  toggle_saved_panel(),
                        bg="#303134", bd=0, activebackground="#303134")
view_button.image = view_icon
view_button.pack(side="left", padx=5)

# geçmişi görme button
history_button = tk.Button(icon_bar2, image=history_icon, command=lambda: toggle_history_panel(),
                           bg="#303134", bd=0, activebackground="#303134")
history_button.image = history_icon
history_button.pack(side="right", padx=5)

# GEÇMİŞ ÇEVİRİLERİ GÖRME fonksiyonu
def toggle_history_panel():
    global history_visible
    if history_visible:
        history_frame.place(x=1510, y=0) #burada gizle
        history_visible = False
    else:
        history_frame.place(x=1190, y=0)
        refresh_history()
        history_visible = True



def refresh_history():
    for widget in history_frame.winfo_children():
        widget.destroy()

    # Başlık ve X tuşu
    title_frame = tk.Frame(history_frame, bg="#303134")
    title_frame.pack(fill="x", pady=(10, 0), padx=10)

    title = tk.Label(title_frame, text="Geçmiş Çeviriler", bg="#303134", fg="white", font=("Arial", 12, "bold"))
    title.pack(side="left")

    close_btn = tk.Button(title_frame, text="X", command=toggle_history_panel,
                          bg="#303134", fg="white", bd=0, font=("Arial", 12))
    close_btn.pack(side="right")

    for idx, item in enumerate(history_data):
        frame = tk.Frame(history_frame, bg="#303134", padx=5, pady=5)
        frame.pack(fill="x", padx=5, pady=3)

        text_label = tk.Label(frame,
            text=item["text"][:25] + ("..." if len(item["text"]) > 25 else ""),
            fg="white", bg="#303134", anchor="w", justify="left", wraplength=170)
        text_label.grid(row=0, column=0, sticky="w", columnspan=3)

        timestamp_label = tk.Label(frame, text=item["timestamp"], fg="gray", bg="#303134", font=("Arial", 8))
        timestamp_label.grid(row=1, column=0, sticky="w", columnspan=3)

                 

is_saved = False # burada ilk başta normal içi boş yıldız
history_visible = False  # panel açık mı
history_data = []   
history_frame = None  # panel frame için global referans

# çeviriyi kaydet fonksiyonu
def save_translation():
    global is_saved

    text = output_box.get("1.0", tk.END).strip()
    if not text:
        return

    if not is_saved:
        # Geçmişe de ekle
        if text and not any(entry["text"] == text for entry in history_data):
            history_data.append({
                "text": text,
                "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M")
            })

        # Çeviriyi kaydet
        if text not in saved_translations:
            saved_translations.append(text)
            refresh_saved_panel()

        # İkonu değiştir
        save_button.config(image=saved_icon)
        save_button.image = saved_icon
        is_saved = True
        status_label.config(text="Çeviri kaydedildi", fg="white")

    else:
        # (İsteğe bağlı) tekrar basılırsa çeviriyi kaldır
        # saved_translations.remove(text)
        # refresh_saved_panel()
        save_button.config(image=save_icon)
        save_button.image = save_icon
        is_saved = False
        status_label.config(text="Kaydedilmedi", fg="gray")

    root.after(2000, lambda: status_label.config(text=""))




def toggle_saved_panel():
    global is_saved_panel_open, saved_panel

    if is_saved_panel_open:
        if saved_panel:
            saved_panel.destroy()
        is_saved_panel_open = False
    else:
        saved_panel = tk.Frame(root, bg="#303134", width=150, height=360)
        saved_panel.place(x=1210, y=0)  # sağdan açılma
        saved_panel.pack_propagate(False)

        # Başlık ve kapatma tuşu
        top_bar = tk.Frame(saved_panel, bg="#303134", height=25)
        top_bar.pack(fill="x")

        title = tk.Label(top_bar, text="Kaydedilenler", bg="#303134", fg="white", font=("Arial", 10, "bold"))
        title.pack(side="left", padx=10)

        close_btn = tk.Button(top_bar, text="X", command=toggle_saved_panel, bg="#1e1e1e", fg="white", bd=0)
        close_btn.pack(side="right", padx=5)

        # Liste alanı
        list_box = tk.Text(saved_panel, bg="#303134", fg="white", wrap="word",
                           font=("Arial", 10), padx=10, pady=10, bd=0)
        list_box.pack(fill="both", expand=True)

        # Çevirileri göster
        for item in saved_translations:
            list_box.insert(tk.END, f"• {item}\n\n")

        list_box.config(state="disabled")

        is_saved_panel_open = True


def refresh_saved_panel():
    if is_saved_panel_open:
        toggle_saved_panel() # burada önce kapat
        toggle_saved_panel() # sonra güncel çevirilerle yeniden başlatır

# temizleme fonksiyonu tanımlama işlemi
def clear_input():
    input_box.delete("1.0", tk.END)
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")
    status_label.config(text="", fg="white")
    root.after(2000, lambda: status_label.config(text=""))

# temizleme butonunu yerleştir
clear_button = tk.Button(output_frame, image=clear_icon,command=clear_input, bg="#303134", activebackground="#3c4043", bd=0)
clear_button.image = clear_icon
clear_button.place(x=380, y=200) #burada da position veriyorum


# Durum mesajı (diğer ögelerle bağlanıt kuruldugunda burada mesaj belirir)
status_label = tk.Label(root, text="", font=("Arial", 10), bg="#202124", fg="gray")
status_label.place(x=1060 , y=315)

# burada oto çeviri yapıyor ve her 0.5 saniyede bir yenileniyor (bu istenildiği gibi ayarlanabilir)
after_id = None
def trigger_translation():
    global after_id
    if after_id:
        root.after_cancel(after_id)
    after_id = root.after(500, perform_translation)



def perform_translation():
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        return
    try:
        src = readable_to_code[clean_lang_name(source_lang_var.get())]
        tgt = readable_to_code[clean_lang_name(target_lang_var.get())]

        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated)
        output_box.config(state="disabled")
    except Exception as e:
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, "Çeviri başarısız.")
        output_box.config(state="disabled")
        print("Hata:", e)



# karakter sayacı kodları buradan başlıyor
max_chars = 5000

# KARAKTER SAYACI İŞLEMLERİ > buradan sonra (root içinde, istenildiği gibi ayarlanabilir)
char_counter = tk.Label(root, text=f"0 / {max_chars}", font=("Arial", 10), fg="gray", bg="#202124")
char_counter.place(x=620, y=315) # pencerenin (rigth_frame köşede) position

# karakter sayacı fonksiyon tanımlama
def update_char_counter(event=None):
    current_text = input_box.get("1.0", tk.END)
    length = len(current_text.strip())
    char_counter.config(text=f"{length} / {max_chars}")

    # eger sınır aşılırsa yazı rengi kırmızı yap
    if length > max_chars:
        char_counter.config(fg="white")
    else:
        char_counter.config(fg="gray")

# karakter sınıra ulaşınca yazmayı oto durdur
def limit_input_length(event=None):
    current_text = input_box.get("1.0", tk.END)
    if len(current_text.strip()) > max_chars:
        input_box.delete("1.0" , tk.END)
        input_box.insert("1.0", current_text.strip()[:max_chars])

root.mainloop() # en sonda mainloop tanımlama