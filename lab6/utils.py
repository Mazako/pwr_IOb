import math

import numpy as np


def clamp(val, min_val=0, max_val=255) -> int:
    return int(min(max(val, min_val), max_val))


def find_closest_pixel(val, k):
    return clamp(round((k - 1) * val / 255) * 255 / (k - 1))


def floyd_steinberg_single_channel(img, k=2) -> None:
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            old_pixel = img[y][x]
            new_pixel = find_closest_pixel(old_pixel, k)
            img[y][x] = new_pixel
            quent_error = old_pixel - new_pixel
            if x + 1 < img.shape[1]:
                img[y][x + 1] = img[y][x + 1] + quent_error * 7 / 16
            if y + 1 < img.shape[0]:
                img[y + 1][x] = img[y + 1][x] + quent_error * 5 / 16
                if x - 1 > 0:
                    img[y + 1][x - 1] = img[y + 1][x - 1] + quent_error * 3 / 16
                if x + 1 < img.shape[1]:
                    img[y + 1][x + 1] = img[y + 1][x + 1] + quent_error / 16


def floyd_steinberg(transform_image, k=3):
    floyd_steinberg_single_channel(transform_image[:, :, 0], k)
    floyd_steinberg_single_channel(transform_image[:, :, 1], k)
    floyd_steinberg_single_channel(transform_image[:, :, 2], k)


#
# Funkcja rysująca punkt
#
# NOTE(sdatko): punkt 0,0 to lewy dolny róg obrazu
#
def draw_point(image, x, y, color=(255, 255, 255)):
    image[image.shape[0] - 1 - y, x, :] = color


def draw_line(image, x1, y1, x2, y2, c1=None, c2=None):
    delta_x, delta_y = int(math.fabs(x2 - x1)), int(math.fabs(y2 - y1))
    x_i, y_i = np.sign(x2 - x1), np.sign(y2 - y1)

    points = []

    if delta_x >= delta_y:
        d = 2 * delta_y - delta_x
    else:
        d = 2 * delta_x - delta_y

    current_x, current_y = x1, y1
    points.append((current_x, current_y))
    while current_x != x2 or current_y != y2:
        if delta_x >= delta_y:
            current_x += x_i
            d += 2 * delta_y
        if delta_y > delta_x:
            current_y += y_i
            d += 2 * delta_x
        if d >= 0:
            if delta_x >= delta_y:
                current_y += y_i
                d -= 2 * delta_x
            if delta_y > delta_x:
                current_x += x_i
                d -= 2 * delta_y
        points.append((current_x, current_y))
    if c1 is not None and c2 is not None:
        t_space = np.linspace(0, 1, len(points))
        colors = [c1 + t * (c2 - c1) for t in t_space]
        for point, color in zip(points, colors):
            draw_point(image, point[0], point[1], color)
    else:
        for point in points:
            draw_point(image, point[0], point[1])


def _area_of_triangle(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])


def _process_color_triangle(image, p, a, b, c, color_a=None, color_b=None, color_c=None):
    a_1 = _area_of_triangle(a, b, p)
    a_2 = _area_of_triangle(b, c, p)
    a_3 = _area_of_triangle(c, a, p)

    sign = np.sign(a_1) + np.sign(a_2) + np.sign(a_3)
    if math.fabs(sign) == 3:
        if color_a is not None and color_b is not None and color_c is not None:
            a = _area_of_triangle(a, b, c)
            color = a_1 / a * color_c + a_2 / a * color_a + a_3 / a * color_b
        else:
            color = (255, 255, 255)
        draw_point(image, p[0], p[1], color)


def draw_triangle(image, a, b, c, color_a=None, color_b=None, color_c=None):
    x_min = min(a[0], b[0], c[0])
    x_max = max(a[0], b[0], c[0])
    y_min = min(a[1], b[1], c[1])
    y_max = max(a[1], b[1], c[1])

    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if x_min <= x <= x_max and y_min <= y <= y_max:
                _process_color_triangle(image, (x, y), a, b, c, color_a, color_b, color_c)


def scale_down(image, scale):
    big_image = image.copy()
    image.resize((image.shape[0] // scale, image.shape[1] // scale, 3), refcheck=False)
    image[:, :, :] = np.zeros((big_image.shape[0] // scale, big_image.shape[1] // scale, 3), dtype=int)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            box = big_image[y * scale: (y + 1) * scale, x * scale: (x + 1) * scale]
            image[y][x] = np.array([np.mean(box[:, :, 0]), np.mean(box[:, :, 1]), np.mean(box[:, :, 2])])


def draw_line_ssaa(image, x1, y1, x2, y2, c1=None, c2=None, scale=2):
    x1 *= 2
    y1 *= 2
    x2 *= 2
    y2 *= 2
    np.ndarray.resize(image, (image.shape[0] * scale, image.shape[1] * scale, 3), refcheck=False)
    draw_line(image, x1, y1, x2, y2, c1, c2)
    scale_down(image, scale)


def draw_triangle_ssaa(image, a, b, c, color_a=None, color_b=None, color_c=None, scale=2):
    a = a * scale
    b = b * scale
    c = c * scale
    np.ndarray.resize(image, (image.shape[0] * scale, image.shape[1] * scale, 3), refcheck=False)
    draw_triangle(image, a, b, c, color_a, color_b, color_c)
    scale_down(image, scale)
