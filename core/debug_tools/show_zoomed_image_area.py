import matplotlib.pyplot as plt


def show_zoomed_image_area(img, x_coordinate, y_range):
    fig, axes = plt.subplots(1, 2)
    axes[0].imshow(img)
    axes[0].set_xlim(x_coordinate - 100, x_coordinate + 100)
    axes[0].set_ylim(y_range[1], y_range[0])
    axes[1].imshow(img)
    axes[1].set_xlim(x_coordinate - 20, x_coordinate + 20)
    axes[1].set_ylim(y_range[1] - 50, y_range[0] + 50)
    axes[1].axvline(x_coordinate, linewidth=1, color='r')
