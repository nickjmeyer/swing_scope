import cv2
from pathlib import Path
from progressbar import progressbar

def main():
    video_dir = Path("data/videos")

    for video_file in progressbar(list(video_dir.glob("*.mp4"))):
        v = cv2.VideoCapture(str(video_file))
        success, frame = v.read()
        i = 0
        while success:
            frame_file = Path(f"data/images/{video_file.stem}/img_{str(i).zfill(6)}.jpg")
            frame_file.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(frame_file), frame)

            success, frame = v.read()
            i += 1


if __name__ == "__main__":
    main()
