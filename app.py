import os
import subprocess
import requests
import pysilk
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from typing import Optional


def download_audio_segment(mp3_url: str) -> str:
    filename = mp3_url.split('/')[-1]
    save_path = os.path.join(".", filename)

    response = requests.get(mp3_url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

    return save_path


def check_mp3_corruption(audio_path: str) -> bool:
    try:
        audio = AudioSegment.from_mp3(audio_path)
        return len(audio) == 0
    except CouldntDecodeError:
        return True


def get_duration(audio_file_path: str) -> float:
    file_extension = os.path.splitext(audio_file_path)[1].lower().replace('.', '')

    if file_extension == 'pcm':
        audio = AudioSegment(
            data=open(audio_file_path, 'rb').read(),
            sample_width=2,
            frame_rate=24000,
            channels=1
        )
    else:
        audio = AudioSegment.from_file(audio_file_path, format=file_extension)

    duration_in_ms = len(audio)
    duration_in_s = duration_in_ms / 1000
    return duration_in_s


def convert_mp3_to_silk(mp3_file_path: str, silk_file_path: str) -> bool:
    try:
        ffmpeg = "ffmpeg"
        pcm_file_path = "intermediate.pcm"
        command = [ffmpeg, "-y", "-i", mp3_file_path, "-f", "s16le", "-ar", "24000", "-ac", "1", pcm_file_path]
        subprocess.run(command, check=True)

        with open(pcm_file_path, 'rb') as pcm_file:
            pcm_data = pcm_file.read()

        silk_data = pysilk.encode(pcm_data, 24000)
        with open(silk_file_path, 'wb') as silk_file:
            silk_file.write(silk_data)
            return True
    except Exception as e:
        print(f"转换失败：{e}")
        return False


def main(**kwargs) -> Optional[float]:
    save_path = download_audio_segment(kwargs.get("mp3_url"))
    print("downloads audio segment")
    if not os.path.exists(save_path):
        return None
    check_result = check_mp3_corruption(save_path)
    print("check mp3 corruption")
    if check_result:
        return None
    convert_bool = convert_mp3_to_silk(save_path, kwargs.get("silk_file_path"))
    print("convert mp3 to silk")
    if not convert_bool:
        return None
    duration = get_duration("intermediate.pcm")
    print("get duration")
    print(f"转换成功：{save_path} -> {kwargs.get('silk_file_path')}")
    print(f"mp3时间是 {duration} 秒.")
    return duration


if __name__ == '__main__':
    main(mp3_url="https://private.vhost205.dlvip.com.cn/silk/Aria.mp3",
         silk_file_path="test.silk")
