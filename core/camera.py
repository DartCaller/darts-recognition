from config import config


class Camera:
    def __init__(self, axis, pos, y_bounds_min):
        self.last_taken_img = None
        self.empty_board_img = None
        self.pos = pos
        self.axis = axis
        self.y_bounds_min = 0
        self.y_bounds_max = 0
        self.set_y_bounds_min(y_bounds_min)

    def set_y_bounds_min(self, y_bounds_min):
        self.y_bounds_min = y_bounds_min
        self.y_bounds_max = y_bounds_min + config['y_bounds_height']

    def crop_img(self, img):
        return img[self.y_bounds_min:self.y_bounds_max, :]

    def update_last_taken_img(self, new_last_img):
        self.last_taken_img = new_last_img

    def set_empty_dart_board_img(self, empty_board_img):
        self.empty_board_img = empty_board_img

    def get_last_img(self):
        return self.last_taken_img.get_img()
