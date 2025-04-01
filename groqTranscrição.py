import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from groq import Groq
import pygame
import threading
import time
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

# Configurar o pydub para usar o ffmpeg instalado pelo imageio-ffmpeg
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

var_api_key = "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"
client = Groq(api_key=var_api_key)

audio_paused = False
pause_start_time = 0
total_pause_time = 0
update_thread = None
audio_duration = 0

def transcrever_audio(event=None):
    global audio_duration
    if event:
        filename = event.data
    else:
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo de áudio",
            filetypes=(("Arquivos de áudio", "*.mp3 *.wav"), ("Todos os arquivos", "*.*"))
        )
    if not filename:
        return

    try:
        audio = AudioSegment.from_file(filename)
        audio_duration = len(audio) / 1000  # duração em segundos
        timeline.config(to=audio_duration)

        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3-turbo",
                prompt="Specify context or spelling",
                response_format="json",
                language="pt",
                temperature=0.0
            )
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, transcription.text)
            play_audio(filename, transcription.text)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def on_drop(event):
    transcrever_audio(event)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Transcrição de Áudio")
root.geometry("800x600")

root.drop_target_register(tk.DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

def play_audio(filename, transcription_text):
    global update_thread
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    update_thread = threading.Thread(target=update_timeline_and_highlight, args=(transcription_text,))
    update_thread.start()

def toggle_audio():
    global audio_paused, pause_start_time, total_pause_time, update_thread
    if audio_paused:
        pygame.mixer.music.unpause()
        toggle_button.config(text="Pausar")
        total_pause_time += time.time() - pause_start_time
        update_thread = threading.Thread(target=update_timeline_and_highlight, args=(text_area.get("1.0", tk.END),))
        update_thread.start()
    else:
        pygame.mixer.music.pause()
        toggle_button.config(text="Continuar")
        pause_start_time = time.time()
    audio_paused = not audio_paused

def stop_audio():
    pygame.mixer.music.stop()

def clear_data():
    text_area.delete(1.0, tk.END)
    timeline.set(0)

def update_timeline_and_highlight(transcription_text):
    words = transcription_text.split()
    word_index = 0
    text_area.tag_remove("highlight", "1.0", tk.END)
    while pygame.mixer.music.get_busy() and not audio_paused:
        current_pos = (pygame.mixer.music.get_pos() / 1000) - total_pause_time  # posição atual em segundos ajustada pelo tempo de pausa
        timeline.set(current_pos)
        if word_index < len(words):
            start_idx = text_area.search(words[word_index], "1.0", tk.END)
            if start_idx:
                end_idx = f"{start_idx}+{len(words[word_index])}c"
                text_area.tag_add("highlight", start_idx, end_idx)
                text_area.tag_config("highlight", background="yellow")
                text_area.see(start_idx)
                text_area.update_idletasks()
                word_index += 1
        time.sleep(0.1)  # Ajuste o atraso conforme necessário

# Configuração da interface gráfica
root = tk.Tk()
root.title("Transcrição de Áudio")
root.geometry("800x600")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

timeline = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=600)
timeline.pack(pady=5)

text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=20)
text_area.pack(pady=5, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(frame)
button_frame.pack(pady=5)

button = tk.Button(button_frame, text="Selecionar Arquivo de Áudio", command=transcrever_audio)
button.grid(row=0, column=0, padx=5)

toggle_button = tk.Button(button_frame, text="Pausar", command=toggle_audio)
toggle_button.grid(row=0, column=1, padx=5)

stop_button = tk.Button(button_frame, text="Parar", command=stop_audio)
stop_button.grid(row=0, column=2, padx=5)

clear_button = tk.Button(button_frame, text="Limpar Dados", command=clear_data)
clear_button.grid(row=0, column=3, padx=5)

root.mainloop()