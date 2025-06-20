import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import sys
import threading
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from PIL import Image
from src.flp_file import FLPFile
from src.flp_manager import FLPManager
from src.audio_manager import AudioManager

class FLPSampleExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.flp_manager = FLPManager()
        self.audio_manager = AudioManager()
        pygame.mixer.init()

        # basic settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("FLP-Sample-Extractor")
        self.geometry("900x500") #"800x450"
        self.resizable(False, False)
        self.update_idletasks()

        # setup variables
        self.folder_icon = None
        self.play_icon = None
        self.stop_icon = None

        self.flp_buttons = {}
        self.active_flp = None 
        self.destination_folder = None
        self.extraction_window = None

        self.load_icons()
        self.setup_gui()

    def load_icons(self):
        # important for PyInstaller to find the icons
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except AttributeError:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)

        self.folder_icon = ctk.CTkImage(
            light_image=Image.open(resource_path("icons/folder_icon.png")),
            dark_image=Image.open(resource_path("icons/folder_icon.png")),
            size=(20, 20)
        )

        self.play_icon = ctk.CTkImage(
            light_image=Image.open(resource_path("icons/play_icon.png")),
            dark_image=Image.open(resource_path("icons/play_icon.png")),
            size=(20, 20)
        )

        self.stop_icon = ctk.CTkImage(
            light_image=Image.open(resource_path("icons/stop_icon.png")),
            dark_image=Image.open(resource_path("icons/stop_icon.png")),
            size=(20, 20)
        )

        self.iconbitmap(resource_path("icons/app_icon.ico"))

    def setup_gui(self):
        self.root = ctk.CTkFrame(master=self)
        self.root.pack(pady=5, padx=5, fill="both", expand=True)


        # DnD area (scrollable)
        self.dnd_area_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        self.dnd_area_frame.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)

        self.dnd_area_frame.drop_target_register(DND_FILES)
        self.dnd_area_frame.dnd_bind('<<Drop>>', self.drop)

        self.dnd_area_content = None

        self.dnd_area_label = ctk.CTkLabel(master=self.dnd_area_frame, text="Drag and drop '.flp' files\nor folders here.", fg_color="transparent", text_color="white")
        self.dnd_area_label.pack(pady=5, padx=5, fill="x", expand=True)


        # sample area (scrollable)
        self.sample_area_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        self.sample_area_frame.place(relx=0.3, rely=0, relwidth=0.7, relheight=0.9)

        self.sample_area_content = ctk.CTkScrollableFrame(master=self.sample_area_frame, fg_color="gray30")
        self.sample_area_content.pack(pady=5, padx=5, fill="both", expand=True)

    
        # destination area (width=1 forces buttons to be minimal width)
        self.destination_area_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        self.destination_area_frame.place(relx=0.3, rely=0.9, relwidth=0.7, relheight=0.1)

        self.destination_area_entry = ctk.CTkEntry(master=self.destination_area_frame, placeholder_text="Choose destination folder for extracted samples", text_color="white", fg_color="gray30")
        self.destination_area_entry.pack(pady=5, padx=5, fill="both", side="left", expand=True)

        self.destination_area_button = ctk.CTkButton(master=self.destination_area_frame, image=self.folder_icon, text="", width=1, height=50, command=self.add_destination_folder)
        self.destination_area_button.pack(pady=5, padx=5, fill="both", side="left")

        self.extract_button = ctk.CTkButton(master=self.destination_area_frame, text="Extract Selection", width=1, height=50, command=self.extract_samples_from_active_flp)
        self.extract_button.pack(pady=5, padx=5, fill="both", side="right")

    def add_destination_folder(self):

        destination_folder = ctk.filedialog.askdirectory(title="Choose destination folder")
        if destination_folder:
            self.destination_area_entry.delete(0, tk.END)
            self.destination_area_entry.insert(0, destination_folder)
            self.destination_folder = destination_folder

    def drop(self, event):
        
        files = self.tk.splitlist(event.data)
        valid_flps, already_loaded_flps = self.flp_manager.add_candidates(files)

        if len(valid_flps) == 0 and len(already_loaded_flps) == 0:
            self.error_window("No valid files detected.\nPlease drop '.flp' files or\nfolders containing .flp files.")
            return

        # setup DnD area after first time of adding files
        if self.dnd_area_content is None:
            self.dnd_area_label.destroy()
            self.dnd_area_content = ctk.CTkScrollableFrame(master=self.dnd_area_frame, fg_color="transparent")
            self.dnd_area_content.pack(pady=5, padx=5, fill="both", expand=True)
            self.dnd_area_content._scrollbar.configure(width=12)

        # add button for each valid FLP file
        for flp in valid_flps:
            button = ctk.CTkButton(master=self.dnd_area_content, text=flp.file_name, fg_color="darkgray", text_color="black",
                            hover_color="gray30", anchor="w", command=lambda f = flp: self.on_select(f))
            button.pack(pady=1, fill="x", expand=True)
            self.flp_buttons[flp.file_path] = button

        if len(already_loaded_flps) > 0:
            self.on_select(already_loaded_flps[0])
        else:
            self.on_select(valid_flps[0])

    def on_select(self, flp: FLPFile):

        # highlight the selected FLP file
        self.active_flp = flp

        for option, button in self.flp_buttons.items():
            if option == flp.file_path:
                button.configure(fg_color="gray", text_color="white")
            else:
                button.configure(fg_color="darkgray", text_color="black")

        # clear screen and refresh samples
        for widget in self.sample_area_content.winfo_children():
            widget.destroy()

        flp.refresh_paths()
        samples = flp.samples

        # no samples found
        if samples == []:
            no_samples_frame = ctk.CTkFrame(master=self.sample_area_content, fg_color="gray90")
            no_samples_frame.pack(pady=1, fill="x")
            no_samples_label = ctk.CTkLabel(master=no_samples_frame, text="No samples found. Re-save the project in your DAW and reload it here if this is unexpected.", fg_color="transparent", text_color="black")
            no_samples_label.pack(pady=5, padx=5, fill="x")
            return

        # sample frame: 50 char name, play/stop button, checkbox
        for sample in samples:
            
            file_name = sample.file_name
            if len(file_name) > 50:
                file_name = file_name[:50] + "..."

            sample_frame = ctk.CTkFrame(master=self.sample_area_content, fg_color="gray90")
            sample_frame.pack(pady=1, fill="x")

            sample_label = ctk.CTkLabel(master=sample_frame, text=file_name, fg_color="transparent", text_color="black")
            sample_label.pack(padx=5, pady=5, side="left")

            sample_checkbox = ctk.CTkCheckBox(master=sample_frame, text="", width=1, variable = tk.BooleanVar(value=sample.extract), command=lambda s = sample: s.toggle_extract())
            sample_checkbox.pack(padx=5, pady=5, side="right")

            sample_stop_button = ctk.CTkButton(master=sample_frame, image=self.stop_icon, text="", width=1, command=self.audio_manager.stop_audio)
            sample_stop_button.pack(pady=1, padx=1, side="right")

            sample_play_button = ctk.CTkButton(master=sample_frame, image=self.play_icon, text="", width=1, command=lambda p = sample.path: self.audio_manager.play_audio(p))
            sample_play_button.pack(pady=1, padx=1, side="right")

    def extract_samples_from_active_flp(self):
        
        # ensure that at least one FLP file is loaded
        if self.flp_manager.flp_objects == {}:
            self.error_window("Please load at least one FLP by\ndrag-and-dropping it into the left frame.")
            return

        # ensure that current path is set even when user manually changes the destination entry
        self.destination_folder = self.destination_area_entry.get()

        # ensure that a destination folder is set
        if self.destination_folder is None or self.destination_folder == "":
            self.error_window("Please choose a destination folder\nfor the extracted samples.")
            return

        # ensure that the destination folder exists
        if not os.path.exists(self.destination_area_entry.get()):
            self.error_window("The selected destination folder does not exist.\nPlease choose a valid folder.")
            return


        self.active_flp.refresh_paths()


        # ensure that the active FLP has existing samples
        if self.active_flp.samples == []:
            self.error_window("The selected FLP does not contain\nany extractable samples.")
            return

        # ensure that at least on sample is selected for extraction
        counter = 0
        for sample in self.active_flp.samples:
            if sample.extract:
                counter += 1
                break

        if counter == 0:
            self.error_window("Please select at least one sample.\n\nIf this error persists after selecting a sample,\ntry reselecting or reloading the FLP file.")
            return


        # create extraction window and start extraction in a separate thread
        self.extraction_window = self.extraction_window_create()

        threading.Thread(
            target=self.active_flp.extract_samples,
            args=(self.destination_folder,),
            kwargs={"callback": lambda value: self._update_extraction_gui(value)},
            daemon=True
        ).start()

    def error_window(self, message):

        #setup window in foreground and block main window
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.resizable(False, False)

        error_window.transient(self)
        error_window.grab_set()
        error_window.focus_force()


        # center window on the main window
        self._config_toplevel_geometry(error_window, 300, 150)

        # error message
        label = ctk.CTkLabel(error_window, text=message)
        label.pack(pady=20)

        ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)

    def extraction_window_create(self):
        #setup window in foreground and black main window
        self.extraction_window = ctk.CTkToplevel(self)
        self.extraction_window.title("Extraction Progress")
        self.extraction_window.resizable(False, False)

        self.extraction_window.transient(self)
        self.extraction_window.grab_set()
        self.extraction_window.focus_force()

        self.extraction_window.protocol("WM_DELETE_WINDOW", lambda: None)


        # center window on the main window
        self._config_toplevel_geometry(self.extraction_window, 300, 150)

        # extraction message
        self.label = ctk.CTkLabel(self.extraction_window, text="Samples are being extracted...\nPlease wait.")
        self.label.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.extraction_window, mode="determinate")
        self.progress_bar.pack(pady=10, padx=10, fill="x", expand=True)
        self.progress_bar.set(0)

        self.ok_button = ctk.CTkButton(self.extraction_window, text="OK", command=self.extraction_window.destroy, state="disabled")
        self.ok_button.pack(pady=10)

        return self.extraction_window

    def _update_extraction_gui(self, progress):
        self.after(0, lambda: self._apply_extraction_progress(progress)) # ensures that the GUI update happens in the main thread (not in the extraction thread)

    def _apply_extraction_progress(self, progress):
        self.progress_bar.set(progress)
        if progress >= 1.0:
            self.label.configure(text="Extraction complete!\nSamples have been extracted successfully.")
            self.ok_button.configure(state="normal")
            self.extraction_window.protocol("WM_DELETE_WINDOW", self.extraction_window.destroy)

    def _config_toplevel_geometry(self, window, window_w, window_h):
        self.update_idletasks()
        x = self.winfo_x()
        y = self.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()

        pos_x = x + (w - window_w) // 2
        pos_y = y + (h - window_h) // 2

        window.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
