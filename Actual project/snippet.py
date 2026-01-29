from pydub import AudioSegment
import requests
from io import BytesIO


def preview(preview_url):
    if preview_url is None:
        raise ValueError("No preview available for this track")

    # Download preview audio
    audio = AudioSegment.from_file(
        BytesIO(requests.get(preview_url).content),
        format="mp3"
    )

    check = input("Play preview? (y/n): ")
    if check.lower() == "y":



