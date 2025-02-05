import os
import re
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import PhotoImage
import yt_dlp
import ffmpeg

cancel_flag = False
download_thread = None
download_speed = "Download speed: 0B/s"

dark_mode = False

script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to imgs for light/dark mode btn
dark_mode_img_path = os.path.join(script_dir, "img", "drk_mode.png")
light_mode_img_path = os.path.join(script_dir, "img", "light_mode.png")

# Create the user interface
root = tk.Tk()
root.title("VideoDownloader")
root.geometry("500x500")

# Load light/dark mode images
dark_mode_img = PhotoImage(file=dark_mode_img_path)
light_mode_img = PhotoImage(file=light_mode_img_path)

# Light/dark mode functionality
def toggle_dark_mode():
    global dark_mode
    if dark_mode:
        root.config(bg="white")
        for widget in root.winfo_children():
            widget.config(bg="white", fg="black")
        dark_mode = False
        mode_button.config(image=dark_mode_img)  # Change image to dark mode
    else:
        root.config(bg="#2c2f36")
        for widget in root.winfo_children():
            widget.config(bg="#2c2f36", fg="white")
        dark_mode = True
        mode_button.config(image=light_mode_img)  # Change image to light mode

# Format the time into a readable format
def format_eta(eta):
    if eta > 60:
        minutes = eta // 60
        seconds = eta % 60
        return f"Wait time: {minutes} minute(s) {seconds} second(s)"
    return f"Wait time: {eta} second(s)"

def update_speed(d):
    speed = d.get('speed', None)
    if speed:
        formatted_speed = format_speed(speed)
        root.after(0, lambda: speed_label.config(text=f"Downloading at: {formatted_speed}"))
    else:
        root.after(0, lambda: speed_label.config(text="Calculating download speed..."))

def format_speed(speed):
    if speed > 1024**2:
        return f"{speed / 1024**2:.2f} MB/s"
    elif speed > 1024:
        return f"{speed / 1024:.2f} KB/s"
    return f"{speed} B/s"

def update_progress(d):
    if d['status'] == 'downloading':
        update_speed(d)

    elif d['status'] == 'starting':
        # Show starting download message
        root.after(0, lambda: speed_label.config(text="Starting download..."))
    elif d['status'] in ['finished', 'error']:
        handle_download_complete(d)

def handle_download_complete(d):
    global download_speed
    if cancel_flag:
        download_speed = "Download cancelled"
    else:
        download_speed = "Converting/merging formats, please wait..."
    root.after(0, lambda: speed_label.config(text=download_speed))

def download_vid():
    global cancel_flag, download_thread
    cancel_flag = False

    url = url_entry.get()
    name_vid = name_entry.get().strip()

    # If the user does not provide a URL display an error
    if not url:
        messagebox.showerror("Error", "Please provide a valid URL.")
        return

    # If user does not provide a name for the video display error
    if not name_vid:
        messagebox.showerror("Error", "Please enter a name for the video.")
        return

    # Let the user choose where to save the video
    folder_path = filedialog.askdirectory(title="Select a folder to save your video")
    if not folder_path:
        # If a folder was not selected to save the video, display an error
        messagebox.showerror("Error", "Please select a folder to save the video.")
        return

    # Avoid these symbols in the name of the video
    folder_path = folder_path.replace("\\", "/")
    name_vid = re.sub(r'[<>:"/\\|?*]', '_', name_vid.strip())

    # Choose format based on audio selection
    if include_audio_var.get() == 'audio':
        format = 'bestvideo+bestaudio/best'  
    else:
    # If no audio option is selected    
        format = 'bestvideo[ext=mp4]'  

    options = {
        'outtmpl': f'{folder_path}/{name_vid}.mp4',  # Output file template
        'format': format,  # Format of video to download
        'progress_hooks': [update_progress],  # Hook to track download progress
        'preferredformat': 'mp4',
        'quiet': True,
        'retries': 3,
        'continue': True,
        'max_downloads': 3,
        'concurrent_fragment_downloads': 3,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'verbose': True,
        'postprocessor_args': [
            '-c:v', 'libx264',  # Video codec (libx264)
            '-c:a', 'aac',  # Audio codec (AAC)
            '-b:a', '192k',
            '-movflags', '+faststart',
        ]
    }

    def run_download():
        global cancel_flag
        try:
            # Start the download
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            # Update the status to "video downloaded"
            root.after(0, lambda:speed_label.config(text="All done"))

            # Check if the video is in AV1 format, and if so, convert it
            input_video = f"{folder_path}/{name_vid}.mp4"
            output_video = f"{folder_path}/{name_vid}_converted.mp4"

            # Verify if the video download requires to be converted
            if "av1" in input_video.lower():
                root.after(0, lambda:speed_label.config(text="converting/merging..."))
                # Convert AV1 to H.264 using FFmpeg to prevent the "file is not supported" message after download
                ffmpeg.input(input_video).output(output_video, vcodec='libx264', acodec='aac').run()

                root.after(0, lambda:speed_label.config(text="All done."))
                messagebox.showinfo("Success", f"Your video has been converted and saved as {name_vid}_converted.mp4")
            else:
                messagebox.showinfo("Success", f"Your video: {name_vid} has been downloaded")

            #Clear the URL & Video name fields after a sucessfull download
            root.after(0, lambda: url_entry.delete(0, tk.END))
            root.after(0, lambda: name_entry.delete(0, tk.END))    

        except yt_dlp.utils.DownloadError as e:
            messagebox.showerror("Download Error", f"Download failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    # Run the download in a separate thread to avoid blocking the GUI
    download_thread = threading.Thread(target=run_download, daemon=True)
    download_thread.start()

def cancel_download():
    global cancel_flag
    cancel_flag = True
    messagebox.showinfo("Download Aborted", "The download is being cancelled.")

    if download_thread is not None:
        download_thread.join(timeout=5)
    else:
        messagebox.showinfo("Download Aborted", "No active download to cancel.")

# Set context menu to allow user to paste URL's using mouse
def show_context_mnu(event):
    context_menu.post(event.x_root, event.y_root)
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="paste URL", command=lambda: url_entry.insert(tk.END, root.clipboard_get()))  


# URL label
url_label = tk.Label(root, text="Paste a link: ")
url_label.pack(pady=10)

# URL entry field
url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=10)

# Set right mouse button to show context menu
url_entry.bind("<Button-3>", show_context_mnu)

# Video name label
name_label = tk.Label(root, text="Name your video: ")
name_label.pack(pady=5)

# Video name entry field
name_entry = tk.Entry(root, width=40)
name_entry.pack(pady=5)

# Radio options to check if user wants audio or not
include_audio_var = tk.StringVar(value="audio")
include_audio_radio_audio = tk.Radiobutton(root, text="Include audio", variable=include_audio_var, value="audio")
include_audio_radio_audio.pack(pady=5)

include_audio_radio_mute = tk.Radiobutton(root, text="Don't include audio", variable=include_audio_var, value="no_audio")
include_audio_radio_mute.pack(pady=5)

# Start download button
dwnld_button = tk.Button(root, text="Download", command=download_vid)
dwnld_button.pack(pady=20)

# Cancel download button
cancel_button = tk.Button(root, text="Cancel", command=cancel_download)
cancel_button.pack(pady=10)

# Show download speed
speed_label = tk.Label(root, text="Waiting to start download...")
speed_label.pack(side='left', padx=10, pady=10)

# Button to toggle light/dark mode with icon
mode_button = tk.Button(root, image=dark_mode_img, command=toggle_dark_mode)
mode_button.place(x=10, y=10)

root.mainloop()