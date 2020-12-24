import tensorflow as tf
import numpy as np
from PIL import Image
import click
from progressbar import progressbar

from pathlib import Path

@click.command()
@click.option("-d", "--directory", required=True, type=click.Path(dir_okay=True, file_okay=False, exists=True))
def main(directory: str):
    directory = Path(directory)

    sum_image = None
    sum_sq_image = None
    count = None

    dims = (257, 257)

    for i, image_file in progressbar(list(enumerate(directory.glob("*.jpg")))):
        img = np.float64(np.array(Image.open(str(image_file)).resize(dims)))
        if i == 0:
            sum_image = img
            sum_sq_image = img*img
        else:
            sum_image += img
            sum_sq_image += img*img

        count = i + 1

    mean_image = sum_image / count
    std_image = ((sum_sq_image / count) - (mean_image * mean_image)) ** 0.5 * (count - 1.0) / count

    np.save(directory / "mean_image.npy", mean_image)
    np.save(directory / "std_image.npy", std_image)

if __name__ == "__main__":
    main()
