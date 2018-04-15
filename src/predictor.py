import json
import datetime
from multiprocessing import Queue
from pathlib import Path
from time import sleep

from keras.models import load_model

from src.labeler import PicLabeler


def run_predictor(model_file: Path,
                  config_file: Path,
                  images_queue: Queue,
                  predictions_queue: Queue):
    # TODO check paths before

    model = load_model(str(model_file))
    dateFormat="%Y-%m-%d %H:%M:%S"
    with config_file.open() as file:
        config = json.load(file)

    labeler = PicLabeler(model, config)

    while True:
        image_cur = images_queue.get()

        if image_cur is None:
            sleep(1)
            continue

        result = labeler.run(image_cur)
        with open('log/%s.json'%(datetime.datetime.now().strftime(dateFormat)), 'w') as f:
            f.write(json.dumps(result))
        predictions_queue.put(result)
