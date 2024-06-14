from pytube import YouTube

def startDownload(youtube_id):
    try:
        url = f"https://www.youtube.com/watch?v={youtube_id}"
        yt = YouTube(url)
        name = yt.title
        audio = yt.streams.get_audio_only()
        output_path = "./downloads"
        audio.download(output_path=output_path)
        return print(f"finished downloading {name}")
    except:
        return print("error downloading")



