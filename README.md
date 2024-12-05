# video downloader

Python program that allows the user to download videos using a URL with support for audio options and light/dark mode
 
## Requirements
-Python 3.x
-yt-dlp
-ffmpeg
-tkinter

## Installation and setup of FFmpeg
For windows:
1. Download FFmpeg here: https://ffmpeg.org/download.html](https://www.gyan.dev/ffmpeg/builds/
2. Extract the zip file.
3. **Open the start menu** and search for "Environment Variables".
4. In the **System properties** window, click on **Environment Variables**.
5. Under **System variables**, scroll down and select `path`, then click **edit**.
6. Click **New** and add the path to the `bin` folder inside the FFmpeg folder (e.g., `C:\ffmpeg\bin`).
7. Click **OK** to save the changes.

## Verify FFmpeg installation
```bash
ffmpeg -version
```
 
## Installation
1. Clone the repository:
```bash
git clone https:github.com/Luisjauregui6/video-downloader.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
python thedownloader.py
```

## Use:
1. Enter a video link.
2. Name your video.
3. Choose if you want audio included in your video or not.
4. Click "download".
5. Wait for the video to download.

## Screenshots

![video downloader screenshot](img/screenshot1.png)

## License 

MIT License 
