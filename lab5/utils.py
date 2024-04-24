"""Function definitions that are used in LSB steganography."""
from matplotlib import pyplot as plt
import numpy as np
import binascii
import cv2 as cv
import math

plt.rcParams["figure.figsize"] = (18, 10)


def encode_as_binary_array(msg):
    """Encode a message as a binary string."""
    msg = msg.encode("utf-8")
    msg = msg.hex()
    msg = [msg[i:i + 2] for i in range(0, len(msg), 2)]
    msg = ["{:08b}".format(int(el, base=16)) for el in msg]
    return "".join(msg)


def decode_from_binary_array(array):
    """Decode a binary string to utf8."""
    array = [array[i:i + 8] for i in range(0, len(array), 8)]
    if len(array[-1]) != 8:
        array[-1] = array[-1] + "0" * (8 - len(array[-1]))
    array = ["{:02x}".format(int(el, 2)) for el in array]
    array = "".join(array)
    result = binascii.unhexlify(array)
    return result.decode("utf-8", errors="replace")


def load_image(path, pad=False):
    """Load an image.

    If pad is set then pad an image to multiple of 8 pixels.
    """
    image = cv.imread(path)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    if pad:
        y_pad = 8 - (image.shape[0] % 8)
        x_pad = 8 - (image.shape[1] % 8)
        image = np.pad(
            image, ((0, y_pad), (0, x_pad), (0, 0)), mode='constant')
    return image


def save_image(path, image):
    """Save an image."""
    plt.imsave(path, image)


def clamp(n, minn, maxn):
    """Clamp the n value to be in range (minn, maxn)."""
    return max(min(maxn, n), minn)


def hide_message(image, message, nbits=1, spos=0):
    """Hide a message in an image (LSB).

    nbits: number of least significant bits
    """
    nbits = clamp(nbits, 1, 8)
    shape = image.shape
    image = np.copy(image).flatten()
    if len(message) > len(image[spos:]) * nbits:
        raise ValueError("Message is to long :(")

    chunks = [message[i:i + nbits] for i in range(0, len(message), nbits)]
    for i, chunk in enumerate(chunks):
        byte = "{:08b}".format(image[i + spos])
        new_byte = byte[:-nbits] + chunk
        image[i + spos] = int(new_byte, 2)

    return image.reshape(shape)


def reveal_message(image, nbits=1, length=0, spos=0):
    """Reveal the hidden message.

    nbits: number of least significant bits
    length: length of the message in bits.
    """
    nbits = clamp(nbits, 1, 8)
    shape = image.shape
    image = np.copy(image).flatten()[spos:]
    length_in_pixels = math.ceil(length / nbits)
    if len(image) < length_in_pixels or length_in_pixels <= 0:
        length_in_pixels = len(image)

    message = ""
    i = 0
    while i < length_in_pixels:
        byte = "{:08b}".format(image[i])
        message += byte[-nbits:]
        i += 1

    mod = length % -nbits
    if mod != 0:
        message = message[:mod]
    return message


def mse(img_1, img_2) -> float:
    w, h, c = img_1.shape
    ms = np.sum((img_1.astype(float) - img_2.astype(float)) ** 2)
    return ms / (w * h * c)


def hide_image(image, secret_image_path, nbits=1):
    with open(secret_image_path, "rb") as file:
        secret_img = file.read()

    secret_img = secret_img.hex()
    secret_img = [secret_img[i:i + 2] for i in range(0, len(secret_img), 2)]
    secret_img = ["{:08b}".format(int(el, base=16)) for el in secret_img]
    secret_img = "".join(secret_img)
    return hide_message(image, secret_img, nbits), len(secret_img)


def reveal_image(image, length, nbits):
    decoded_bytes_str = reveal_message(image, nbits, length)
    bytes_image = [
        int.to_bytes(
            int(decoded_bytes_str[i: i + 8], 2),
            1,
            byteorder='little'
        )
        for i in range(0, len(decoded_bytes_str), 8)
    ]
    file = b''.join(bytes_image)
    array = np.frombuffer(file, np.uint8)
    return cv.cvtColor(cv.imdecode(array, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)


def reveal_image_no_len(image, nbits):
    found_header = False
    image = np.copy(image).flatten()
    i = 0
    byte_str_tmp = ''
    byte_list = []
    while not found_header and i < len(image):
        _bytes = "{:08b}".format(image[i])[-nbits:]
        byte_str_tmp += _bytes
        if len(byte_str_tmp) >= 8:
            full_byte = byte_str_tmp[:8]
            byte_str_tmp = byte_str_tmp[8:]
            byte_list.append(
                int.to_bytes(
                    int(full_byte, 2),
                    1,
                    byteorder='little'
                )
            )
            if len(byte_list) > 1:
                h1, h2 = byte_list[-2:]
                if h1 == b'\xff' and h2 == b'\xd9':
                    found_header = True
        i += 1

    if not found_header:
        raise ValueError('JPEG file not found')
    file = b''.join(byte_list)
    array = np.frombuffer(file, np.uint8)
    return cv.cvtColor(cv.imdecode(array, cv.IMREAD_COLOR), cv.COLOR_BGR2RGB)
