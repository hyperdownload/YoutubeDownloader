import os
from tkinter import Tk, Label, Button, Checkbutton, StringVar, Entry, filedialog, OptionMenu, messagebox, ttk
from threading import Thread
from pytube import YouTube, Playlist

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

        self.download_thread = None

        # Enlace a GitHub y Botón de Ayuda
        self.label_github = Label(root, text="Visita nuestro GitHub:")
        self.label_github.grid(row=5, column=0, sticky="e")
        
        self.button_github = Button(root, text="GitHub", command=self.open_github)
        self.button_github.grid(row=5, column=1, pady=5)

        self.button_help = Button(root, text="Ayuda", command=self.show_help)
        self.button_help.grid(row=5, column=2, pady=5)

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

    def open_github(self):
        # Abre el enlace a GitHub en el navegador predeterminado
        import webbrowser
        webbrowser.open("https://github.com/hyperdownload/YoutubeDownloader/releases")

    def show_help(self):
        # Muestra la guía de ayuda (puedes personalizar el contenido)
        help_message = (
            "Guía de Ayuda:\n\n"
            "1. Ingresa la URL del video de YouTube en el campo 'URL'.\n"
            "2. Selecciona la ruta de descarga y el formato de descarga.\n"
            "3. Haz clic en 'Descargar' para iniciar la descarga.\n"
            "4. Si es una lista de reproducción, se descargarán todos los videos en la lista.\n"
            "5. Puedes verificar el progreso en la barra de progreso.\n"
            "6. Puedes actualizar el programa visitando el github y descargando en el apartado de releases."
        )
        messagebox.showinfo("Ayuda", help_message)

if __name__ == "__main__":
    root = Tk()
    downloader = YouTubeDownloader(root)
    root.mainloop()
