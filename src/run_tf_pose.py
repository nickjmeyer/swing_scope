import tensorflow as tf
import numpy as np
from PIL import Image, ImageDraw
import time

from pathlib import Path

def main():

    image_dir = Path("data/images/PXL_20201004_205920682")

    interpreter = tf.lite.Interpreter(model_path="data/models/posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite")
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    input_width = input_details[0]["shape"][1]
    input_height = input_details[0]["shape"][2]

    output_details = interpreter.get_output_details()

    mean_image = np.load(image_dir / "mean_image.npy")
    std_image = np.load(image_dir / "std_image.npy")

    std_image[std_image == 0] = 0.1

    print(output_details)

    for i, image_file in enumerate(image_dir.glob("*.jpg")):
        if i != 8000:
            continue

        original_image = Image.open(str(image_file))

        img = np.array(original_image.resize((input_width, input_height))).astype(np.float64)

        img -= mean_image
        img /= std_image

        img = np.expand_dims(img, axis=0)

        img = img.astype(np.float32)

        interpreter.set_tensor(input_details[0]['index'], img)

        start_time = time.time()
        interpreter.invoke()
        stop_time = time.time()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        results = np.squeeze(output_data)
        print(results.shape)

        print(results[:,:,7])

        draw = ImageDraw.Draw(original_image)

        points = []
        for i in range(17):
            conf = results[:,:,i]
            index = np.unravel_index(np.argmax(conf), conf.shape)

            rel_coordinate = np.array(index).astype(np.float) / np.array(conf.shape)
            coordinate = rel_coordinate * np.array(original_image.size)

            tl = coordinate - 5
            br = coordinate + 5

            draw.ellipse((tl[1], tl[0], br[1], br[0]), outline="red", fill="red", width=1)

        original_image.show()


        print('time: {:.3f}ms'.format((stop_time - start_time) * 1000))










if __name__ == "__main__":
    main()
