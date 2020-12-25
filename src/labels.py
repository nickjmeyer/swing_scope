import pydantic.dataclasses
import pathlib
import json
from pathlib import Path
from typing import Dict
from enum import Enum

class Swing(Enum):
    Start = 1
    Back = 2
    Impact = 3
    Finish = 4
    Other = 5


class Pose(Enum):
    Head = 1
    Hips = 2
    Hands = 3
    LeftShoulder = 4
    RightShoulder = 5


@pydantic.dataclasses.dataclass
class Coordinate:
    x: int
    y: int


@pydantic.dataclasses.dataclass
class Labels:
    pose: Dict[Pose, Coordinate]
    swing: Swing


LabelSet = Dict[Path, Labels]


class LabelsSchema(pydantic.BaseModel):
    pose: Dict[str, Coordinate]
    swing: str


class LabelSetSchema(pydantic.BaseModel):
    label_set: Dict[str, LabelsSchema]


def dump_label_set(label_set: LabelSet):
    converted_label_set = LabelSetSchema(label_set={})
    for path, labels in label_set.items():
        converted_labels = LabelsSchema(pose={}, swing=labels.swing.name)
        for pose, coordinate in labels.pose.items():
            converted_labels.pose[pose.name] = coordinate

        converted_label_set.label_set[str(path)] = converted_labels

    return converted_label_set.json(indent=4, sort_keys=True)


def load_label_set(s: str):
    label_set_raw = LabelSetSchema.parse_raw(s)

    pose_map = {}
    for f in Pose:
        pose_map[f.name] = f.value

    swing_map = {}
    for f in Swing:
        swing_map[f.name] = f.value

    label_set: LabelSet = {}
    for path, labels_raw in label_set_raw.label_set.items():
        labels = Labels(pose={}, swing=swing_map[labels_raw.swing])
        for pose, coordinate in labels_raw.pose.items():
            labels.pose[Pose(pose_map[pose])] = coordinate

        label_set[Path(path)] = labels

    return label_set


def main():
    labels_file = Path("data/images/PXL_20201004_205920682/labels.json")
    with labels_file.open("r") as f:
        d = load_label_set(f.read())

    with labels_file.open("w") as f:
        f.write(dump_label_set(d))




if __name__ == "__main__":
    main()
