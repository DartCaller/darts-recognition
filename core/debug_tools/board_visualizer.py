import matplotlib.pyplot as plt
import math
from datetime import datetime


def _setup_plot():
    fig, axes = plt.subplots(1, 2)
    for ax in axes:
        ax.set_facecolor((0, 0, 0))
        ax.set_aspect('equal', adjustable='box')
    axes[0].set_xlim(-200, 200)
    axes[0].set_ylim(-200, 200)
    return fig, axes


def _draw_sections(ax, point, length):
    x, y = point
    for i in range(0, 360, 18):
        angle = i + 9
        end_y = length * math.sin(math.radians(angle))
        end_x = length * math.cos(math.radians(angle))
        col = 'red' if (angle + 9) % 90 == 0 else 'white'
        ax.plot([x, end_x], [y, end_y], color=col, linewidth=1)


def _draw_rings(ax, center, scale):
    ring_sizes = [7, 17, 96, 106, 161, 171]
    for ringSize in ring_sizes:
        ring = plt.Circle(center, ringSize * scale, color='white', fill=False, linewidth=1)
        ax.add_patch(ring)
    ax.add_patch(plt.Circle(center, 15, linewidth=1, color='black', zorder=3))
    ax.add_patch(plt.Circle(center, 6, linewidth=1, color='white', fill=False, zorder=4))
    ax.add_patch(plt.Circle(center, 4, linewidth=1, color='black', zorder=5))


def _draw_dartboard(ax, center=(0, 0), scale=1):
    _draw_rings(ax, center, scale)
    _draw_sections(ax, center, 180)


def _draw_dart(ax, point):
    # Rotate Point to fit rotated board
    angle = math.radians(-9)
    qx = math.cos(angle) * point.x - math.sin(angle) * point.y
    qy = math.sin(angle) * point.x + math.cos(angle) * point.y
    ax.plot(qx, qy, 'ro', zorder=6)


def draw_point_on_dartboard(point):
    fig, axes = _setup_plot()
    for ax in axes:
        _draw_dartboard(ax)
        _draw_dart(ax, point)
    axes[1].set_xlim(point.x - 50, point.x + 50)
    axes[1].set_ylim(point.y - 50, point.y + 50)
    axes[0].set_ylabel('Pos in mm')
    axes[0].set_title('Dart at ' + datetime.now().strftime("%c"))
    fig.show()
