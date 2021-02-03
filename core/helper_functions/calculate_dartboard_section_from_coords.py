from find_first_index import find_first_index
import math


def calculate_dartboard_section_from_coords(vector):
    degree = math.degrees(math.atan2(vector.y, vector.x))
    print('degree ', degree)
    bull_dist = (((vector.x ** 2) + (vector.y ** 2)) ** 0.5)
    print('bullDist ', bull_dist)

    if degree < 0:
        degree += 360
    if degree > 360:
        degree -= 360

    rings = [7, 17, 96, 106, 161, 171]
    sections = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]

    ring_index = find_first_index(rings, lambda ring: ring > bull_dist)
    section = sections[math.floor(degree / 18)]

    if ring_index == 0:
        return 'Bulls Eye'
    elif ring_index == 1:
        return 'Single Bull'
    elif ring_index == 3:
        return 'Triple ' + str(section)
    elif ring_index == 5:
        return 'Double ' + str(section)
    elif ring_index is None:
        return '0'
    return section
