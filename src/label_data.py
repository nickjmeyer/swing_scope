import cv2
from pathlib import Path
import click
import pydantic
import pydantic.dataclasses
import dataclasses
import labels
from enum import Enum
from typing import Any, Dict, List, Optional

Keys = {
    ord("a"): labels.Feature.Head,
    ord("s"): labels.Feature.Hips,
    ord("d"): labels.Feature.Hands,
    ord("f"): labels.Feature.LeftShoulder,
    ord("g"): labels.Feature.RightShoulder,
    ord("w"): None,
}

Colors = {
    labels.Feature.Head: (0, 255, 0),
    labels.Feature.Hips: (255, 0, 0),
    labels.Feature.Hands: (0, 0, 255),
    labels.Feature.LeftShoulder: (120, 0, 120),
    labels.Feature.RightShoulder: (0, 120, 120),
    None: (180, 37, 123),
}


@dataclasses.dataclass(frozen=False)
class LabelManager:
    feature: Optional[labels.Feature]
    position: labels.Coordinate
    is_done: bool
    label_set: labels.LabelSet
    labels_file: str
    image_paths: List[Path]
    index: int

    def __init__(self, image_dir: Path):
        self.feature = None
        self.position = labels.Coordinate(0, 0)
        self.is_done = False
        self.label_set = {}

        self.labels_file = image_dir / "labels.json"
        if self.labels_file.exists():
            with self.labels_file.open("r") as f:
                self.label_set = labels.load_label_set(f.read())

        self.image_paths = sorted(list(image_dir.glob("*.jpg")))

        self.index = 0
        self.render()


    def next(self):
        self.index = min(self.index + 1, len(self.image_paths) - 1)
        self.render()


    def prev(self):
        self.index = max(self.index - 1, 0)
        self.render()


    def mouse_callback(self, event, x, y, flags, param):
        self.position = labels.Coordinate(x, y)


    def render(self):
        path = self.image_paths[self.index]
        frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
        circle_size = 5

        cv2.putText(frame,
                    "<None>" if self.feature is None else self.feature.name,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    Colors[self.feature],
                    2)
        cv2.putText(frame,
                    f"{self.index} / {len(self.image_paths)}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2)

        for f, c in self.label_set.get(path, {}).items():
            cv2.circle(frame,
                       (c.x, c.y),
                       circle_size,
                       Colors[f],
                       -1)
            cv2.putText(frame,
                        f.name,
                        (c.x+7, c.y+7),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        Colors[f],
                        2)

        cv2.imshow("image", frame)


    def save_labels(self):
        with self.labels_file.open("w") as f:
            f.write(labels.dump_label_set(self.label_set))


    def key_press(self, key):
        if key in Keys:
            print("switch")
            self.feature = Keys[key]

            self.render()

        elif key == ord(" "):
            print("register")
            if self.feature is not None:
                path = self.image_paths[self.index]
                self.label_set.setdefault(path, {})[self.feature] = self.position

            self.next()


        elif key == 8: # backspace
            print("backspace")
            path = self.image_paths[self.index]
            labels = self.label_set.setdefault(path, {})
            if self.feature in labels:
                del labels[self.feature]

            self.prev()


        elif key == ord("q"):
            print("quit")
            self.is_done = True

            self.save_labels()


        elif key == ord("z"):
            print("prev")
            self.prev()

        elif key == ord("x"): # right arrow
            print("next")
            self.next()

        else:
            print(key)



@click.command()
@click.option("-d", "--directory", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True))
def main(directory):
    directory = Path(directory)

    files = list(directory.glob("*.jpg"))

    features = ["head", "hips", "hands", "left shoulder", "right shoulder"]
    keys = ["a", "s", "d", "f", "g"]

    cv2.namedWindow("image")

    manager = LabelManager(directory)
    cv2.setMouseCallback("image", manager.mouse_callback)

    while not manager.is_done:
        key = cv2.waitKey(0)
        manager.key_press(key)



if __name__ == "__main__":
    main()
