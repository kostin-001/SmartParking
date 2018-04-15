from skimage.draw import polygon
from scipy.spatial import distance
import numpy as np
import cv2


class PicLabeler:
    def __init__(self, model, config):
        self.model = model
        self.slots = config

    def run(self, image):

        self.image = image
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        self.pts2 = np.float32([[0, 60], [0, 0], [40, 0], [40, 60]])
        slots = []  # list of preprocessed slot images
        ids = []  # list of slot ids

        for index, space in enumerate(self.slots):
            slot, _ = self.process_slot(space)
            ids.append(index + 1)
            slots.append(slot)

        return self.predict(slots, ids)

    def preprocess_coords(self, xs, ys):
        distances = []
        # calculate all side lengths of the quadrilateral
        for i in range(4):
            distances.append(
                distance.euclidean(
                    np.float32([xs[i], ys[i]]),
                    np.float32([xs[(i + 1) % 4], ys[(i + 1) % 4]])))
        # which one is the longest?
        starting_point = np.argmax(np.array(distances))
        # rearrange coordinates cyclically, so that longest side goes first
        new_xs = xs[starting_point:] + xs[:starting_point]
        new_ys = ys[starting_point:] + ys[:starting_point]
        return new_xs, new_ys

    def predict(self, slots, ids):
        answer = {}
        if not slots:
            print("answer empty")
            return answer
        # batch_size = 16
        # Verbosity mode: 1 = progress bar
        pred = self.model.predict(np.array(slots), 16, 1)

        # construct a JSON entity with results
        pred = pred.ravel().tolist()
        for i, one_id in enumerate(ids):
            answer[one_id] = 'Occupied' if pred[i] else 'Empty'
        return answer

    def process_slot(self, space):
        xs = []
        ys = []
        for point in space:
            xs.append(point[0])
            ys.append(point[1])
        # ensure contour is a quadrilateral. This assertion failed once.
        assert len(xs) == 4
        assert len(ys) == 4
        # preprocess and save coordinates
        xs, ys = self.preprocess_coords(xs, ys)
        xs = np.float32(xs)
        ys = np.float32(ys)
        coords = np.vstack((xs, ys)).T
        # get a matrix for perspective transformation
        M = cv2.getPerspectiveTransform(coords, self.pts2)

        # transform a quadrilateral into a solid rectangle
        dst = cv2.warpPerspective(self.image, M, (40, 60))
        # apply the perspective transformation matrix to a slot
        # and return as 40x60x1 NumPy array
        return np.reshape(dst, (40, 60, 1)), coords
