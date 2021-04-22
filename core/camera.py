from config import config


class Camera:
    def __init__(self, axis, pos, y_bounds_min):
        self.last_taken_image = None
        self.empty_board_image = None
        self.pos = pos
        self.axis = axis
        self.y_bounds_min = 0
        self.y_bounds_max = 0
        self.set_y_bounds_min(y_bounds_min)

    def set_y_bounds_min(self, y_bounds_min):
        self.y_bounds_min = y_bounds_min
        self.y_bounds_max = y_bounds_min + config['y_bounds_height']

    def crop_image(self, image):
        return image[self.y_bounds_min:self.y_bounds_max, :]

    def update_last_taken_image(self, new_last_image):
        self.last_taken_image = new_last_image

    def set_empty_dart_board_image(self, empty_board_image):
        self.empty_board_image = empty_board_image
