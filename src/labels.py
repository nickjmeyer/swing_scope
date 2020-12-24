import pydantic.dataclasses
import pathlib
import json
from pathlib import Path
from typing import Dict
from enum import Enum


class Feature(Enum):
    Head = 1
    Hips = 2
    Hands = 3
    LeftShoulder = 4
    RightShoulder = 5


@pydantic.dataclasses.dataclass
class Coordinate:
    x: int
    y: int


Labels = Dict[Feature, Coordinate]
LabelSet = Dict[Path, Labels]


class LabelSetSchema(pydantic.BaseModel):
    label_set: Dict[str, Dict[str, Coordinate]]


def dump_label_set(label_set: LabelSet):
    converted_label_set = LabelSetSchema(label_set={})
    for path, labels in label_set.items():
        converted_labels = {}
        for feature, coordinate in labels.items():
            converted_labels[feature.name] = coordinate

        converted_label_set.label_set[str(path)] = converted_labels

    return json.dumps(converted_label_set.json(), indent=4, sort_keys=True)


def load_label_set(s: str):
    label_set_raw = LabelSetSchema.parse_raw(json.loads(s))

    feature_map = {}
    for f in Feature:
        feature_map[f.name] = f.value

    label_set: LabelSet = {}
    for path, labels_raw in label_set_raw.label_set.items():
        labels: Labels = {}
        for feature, coordinate in labels_raw.items():
            labels[Feature(feature_map[feature])] = coordinate

        label_set[Path(path)] = labels

    return label_set


def main():
    c = Coordinate(x=3, y=7)
    labels = {Feature.Head: c}
    label_set = {Path("."): labels}

    print(dump_label_set(label_set))
    print(load_label_set(dump_label_set(label_set)))




if __name__ == "__main__":
    main()
