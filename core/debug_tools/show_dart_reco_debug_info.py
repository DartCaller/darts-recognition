import matplotlib.pyplot as plt


def show_dart_reco_debug_info(base_img, dart_img, diff_img, x_coordinate):
    fig, axes = plt.subplots(2, 2)
    axes[0][0].imshow(base_img)
    # draw_y_bounds(axes[0][0])
    axes[0][1].imshow(dart_img)
    # draw_y_bounds(axes[0][1])
    axes[1][0].imshow(diff_img)
    axes[1][1].imshow(dart_img)
    axes[1][1].set_xlim(x_coordinate - 300, x_coordinate + 300)
    axes[1][1].axvline(x_coordinate, linewidth=1, color='r')
    axes[1][1].annotate(f'  {x_coordinate})', (x_coordinate, base_img.shape[0] - 130), color='r')
    fig.show()
