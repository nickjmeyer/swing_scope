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
    ord("a"): labels.Pose.Head,
    ord("s"): labels.Pose.Hips,
    ord("d"): labels.Pose.Hands,
    ord("f"): labels.Pose.LeftShoulder,
    ord("g"): labels.Pose.RightShoulder,
    ord("w"): None,
}


Colors = {
    labels.Pose.Head: (0, 255, 0),
    labels.Pose.Hips: (255, 0, 0),
    labels.Pose.Hands: (0, 0, 255),
    labels.Pose.LeftShoulder: (120, 0, 120),
    labels.Pose.RightShoulder: (0, 120, 120),
    None: (180, 37, 123),
}


def default_labels():
    return labels.Labels(pose={}, swing=labels.Swing.Other)


@dataclasses.dataclass(frozen=False)
class LabelManager:
    pose: Optional[labels.Pose]
    position: labels.Coordinate
    is_done: bool
    label_set: labels.LabelSet
    labels_file: str
    image_paths: List[Path]
    index: int


    def __init__(self, image_dir: Path):
        self.swing = labels.Swing.Start
        self.pose = None
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

        current_labels = self.label_set.get(path, default_labels())

        # Pose being labeled
        cv2.putText(frame,
                    "<None>" if self.pose is None else self.pose.name,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    Colors[self.pose],
                    2)

        # Frame counter
        cv2.putText(frame,
                    f"{self.index} / {len(self.image_paths)}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2)

        # Swing stage
        cv2.putText(frame,
                    f"{current_labels.swing.name} ({self.swing.name})",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2)


        for f, c in current_labels.pose.items():
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
            self.pose = Keys[key]

            self.render()

        elif key == ord(" "):
            print("register")
            if self.pose is not None:
                path = self.image_paths[self.index]
                current_labels = self.label_set.setdefault(path, default_labels())
                current_labels.pose[self.pose] = self.position

            self.next()


        elif key == 8: # backspace
            print("backspace")
            path = self.image_paths[self.index]
            current_labels = self.label_set.setdefault(path, default_labels())
            if self.pose in current_labels.pose:
                del current_labels.pose[self.pose]

            self.prev()


        elif key == ord("j"):
            path = self.image_paths[self.index]
            current_labels = self.label_set.setdefault(path, default_labels())
            current_labels.swing = self.swing

            # Bump to next swing state
            self.swing = labels.Swing(self.swing.value + 1)
            if self.swing == labels.Swing.Other:
                self.swing = labels.Swing.Start

            self.render()


        elif key == ord("l"):
            path = self.image_paths[self.index]
            current_labels = self.label_set.setdefault(path, default_labels())
            current_labels.swing = labels.Swing.Other

            self.render()


        elif key == ord("q"):
            print("quit")
            self.is_done = True

            self.save_labels()


        elif key == ord("z"):
            print("prev")
            self.prev()

        elif key == ord("x") or key == ord("k"):
            print("next")
            self.next()

        else:
            print(key)



@click.command()
@click.option("-d", "--directory", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True))
def main(directory):
    directory = Path(directory)

    files = list(directory.glob("*.jpg"))

    poses = ["head", "hips", "hands", "left shoulder", "right shoulder"]
    keys = ["a", "s", "d", "f", "g"]

    cv2.namedWindow("image")

    manager = LabelManager(directory)
    cv2.setMouseCallback("image", manager.mouse_callback)

    while not manager.is_done:
        key = cv2.waitKey(0)
        manager.key_press(key)



if __name__ == "__main__":
    main()
