import os
import sys
import requests
from tkinter import Tk, Label, Button, Checkbutton, StringVar, Entry, filedialog, OptionMenu, messagebox, ttk
from threading import Thread
from pytube import YouTube, Playlist
import subprocess

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")

        self.label_url = Label(root, text="URL:")
        self.label_url.grid(row=0, column=0, sticky="e")

        self.entry_url = Entry(root, width=40)
        self.entry_url.grid(row=0, column=1, columnspan=2, pady=10)

        self.label_output_path = Label(root, text="Ruta de descarga:")
        self.label_output_path.grid(row=1, column=0, sticky="e")

        self.output_path = StringVar(value=os.path.expanduser("~") + "/Downloads")
        self.entry_output_path = Entry(root, textvariable=self.output_path, width=30)
        self.entry_output_path.grid(row=1, column=1, pady=5)

        self.button_browse = Button(root, text="Seleccionar Ruta", command=self.browse_path)
        self.button_browse.grid(row=1, column=2, pady=5)

        self.label_format = Label(root, text="Formato de descarga:")
        self.label_format.grid(row=2, column=0, sticky="e")

        self.formats = ["mp3", "ogg", "wav", "mp4", "mpeg", "avi"]
        self.selected_format = StringVar(value=self.formats[0])
        self.option_menu = OptionMenu(root, self.selected_format, *self.formats)
        self.option_menu.grid(row=2, column=1, pady=5)

        self.button_download = Button(root, text="Descargar", command=self.download_thread)
        self.button_download.grid(row=3, column=1, columnspan=2, pady=10)

        self.progress_label = Label(root, text="Progreso:")
        self.progress_label.grid(row=4, column=0, sticky="e")

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=4, column=1, columnspan=2, pady=5)

        self.button_check_update = Button(root, text="Verificar Actualizaciones", command=self.check_for_update)
        self.button_check_update.grid(row=5, column=1, columnspan=2, pady=10)

        self.download_thread = None

    def browse_path(self):
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.output_path.set(selected_path)

    def download_thread(self):
        # Verificar si ya hay una descarga en progreso
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("Descarga en Progreso", "Ya hay una descarga en curso.")
            return

        # Iniciar un nuevo hilo para la descarga
        self.download_thread = Thread(target=self.download)
        self.download_thread.start()

    def download(self):
        url = self.entry_url.get()

        if not url:
            self.show_error("Error", "Por favor, ingresa una URL válida.")
            return

        try:
            if "playlist" in url.lower():
                playlist = Playlist(url)
                for video_url in playlist.video_urls:
                    self.download_video(video_url)
            else:
                self.download_video(url)
        except Exception as e:
            self.show_error("Error", f"Error: {str(e)}")

    def download_video(self, video_url):
        try:
            yt = YouTube(video_url, on_progress_callback=self.show_progress)

            if self.selected_format.get() in ["mp3", "ogg", "wav"]:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                stream = yt.streams.first()

            output_folder = self.output_path.get()
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = int(stream.filesize)

            self.root.after(100, self.update_progress)  # Programar la actualización periódica de la interfaz

            messagebox.showinfo("Descargando", f"Iniciando descarga de: {yt.title}")
            stream.download(output_path=output_folder, filename=f"{yt.title}.{self.selected_format.get()}")
            messagebox.showinfo("Completado", "Descarga completada.")
        except Exception as e:
            self.show_error("Error", f"Error al descargar el video: {str(e)}")

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_progress(self, stream, chunk, remaining):
        downloaded = stream.filesize - remaining
        self.progress_bar["value"] = downloaded

    def update_progress(self):
        if self.download_thread and self.download_thread.is_alive():
            self.root.after(100, self.update_progress)  # Programar la actualización periódica de la interfaz
        else:
            self.progress_bar["value"] = 0  # Restablecer la barra de progreso cuando la descarga ha finalizado

    def check_for_update(self):
        try:
            github_repo = 'hyperdownload/YoutubeDownloader'
            releases_url = f'https://api.github.com/repos/{github_repo}/releases/latest'

            response = requests.get(releases_url)
            data = response.json()
            latest_version = data['tag_name'][1:]  # Ignora el prefijo 'v'

            current_version = '1.0.0'  # Reemplaza con la versión actual de tu aplicación
            if latest_version > current_version:
                message = f"¡Nueva versión disponible!\n\nActual: {current_version}\nNueva: {latest_version}\n\n¿Deseas actualizar?"
                if messagebox.askyesno("Actualización Disponible", message):
                    self.update_application(data['assets'][0]['browser_download_url'])
        except Exception as e:
            print(f"Error al comprobar actualizaciones: {e}")

    def update_application(self, download_url):
        try:
            download_path = os.path.join(os.path.expanduser("~"), "Downloads", "update.exe")
            response = requests.get(download_url, stream=True)

            with open(download_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

            subprocess.Popen([download_path, 'install', '--silent'], shell=True)
            sys.exit()
        except Exception as e:
            print(f"Error al descargar e instalar la actualización: {e}")

if __name__ == "__main__":
    root = Tk()
    downloader = YouTubeDownloader(root)
    root.mainloop()
