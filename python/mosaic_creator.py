import os, random
from PIL import Image
import numpy as np

def getImages(images_directory):
    files = os.listdir(images_directory)
    images = []
    for file in files:
        filePath = os.path.abspath(os.path.join(images_directory, file))
        try:
            fp = open(filePath, "r+b")
            im = Image.open(fp).convert("RGBA")
            img = Image.new("RGBA", im.size, "WHITE")
            img.paste(im, (0, 0), im)
            img.convert('RGB')
            images.append(img)
            im.load()
            fp.close()
        except Exception as e:
            print(f"{e}\nInvalid image: {filePath}")
    return (images)


def getAverageRGB(image):
    im = np.array(image)
    w, h, d = im.shape
    return (tuple(np.average(im.reshape(w * h, d), axis=0)))


def splitImage(image, size):
    W, H = image.size[0], image.size[1]
    m, n = size
    w, h = int(W / n), int(H / m)
    imgs = []
    for j in range(m):
        for i in range(n):
            imgs.append(image.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)))
    return (imgs)


def getBestMatchIndex(input_avg, avgs):
    avg = input_avg
    index = 0
    min_index = 0
    min_dist = float("inf")
    for val in avgs:
        dist = ((val[0] - avg[0]) * (val[0] - avg[0]) +
                (val[1] - avg[1]) * (val[1] - avg[1]) +
                (val[2] - avg[2]) * (val[2] - avg[2]))
        if dist < min_dist:
            min_dist = dist
            min_index = index
        index += 1
    return (min_index)


def createImageGrid(images, dims, color = None):
    m, n = dims
    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])
    grid_img = Image.new('RGB', (n * width, m * height), color)
    for index in range(len(images)):
        row = int(index / n)
        col = index - n * row
        grid_img.paste(images[index], (col * width, row * height))
    return (grid_img)


def createPhotomosaic(target_image, input_images, grid_size,
                      reuse_images=True):
    target_images = splitImage(target_image, grid_size)

    output_images = []
    count = 0
    batch_size = int(len(target_images) / 10)
    avgs = []
    for img in input_images:
        try:
            avgs.append(getAverageRGB(img))
        except ValueError:
            continue

    for img in target_images:
        avg = getAverageRGB(img)
        match_index = getBestMatchIndex(avg, avgs)
        output_images.append(input_images[match_index])
        if count > 0 and batch_size > 10 and count % batch_size is 0:
            print('processed %d of %d...' % (count, len(target_images)))
        count += 1
        # remove selected image from input if flag set
        if not reuse_images:
            input_images.remove(match_index)

    mosaic_image = createImageGrid(output_images, grid_size)
    return (mosaic_image)