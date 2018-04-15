from multiprocessing import Process, Queue
from time import sleep
from pathlib import Path

from src.predictor import run_predictor
from src.stream import run_stream


def main():
    images_queue = Queue(1)
    predictions_queue = Queue(1)

    model_path = Path('model')
    video_path = Path('pltd.mp4')
    config_path = Path('coords.json')

    predictor_p = Process(target=run_predictor,
                          args=(model_path, config_path, images_queue, predictions_queue))
    stream_p = Process(target=run_stream,
                       args=(video_path, config_path, images_queue, predictions_queue))

    predictor_p.start()
    stream_p.start()

    while True:
        if not stream_p.is_alive():
            predictor_p.terminate()
            exit(0)

        sleep(1)


if __name__ == '__main__':
    main()
