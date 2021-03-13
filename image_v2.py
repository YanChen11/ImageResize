from skimage import io, img_as_ubyte
from skimage.transform import resize, pyramid_reduce
from skimage.filters import gaussian
import sys, os
from os.path import getsize
from PIL import Image

argvs = sys.argv
if len(argvs) < 5:
    exit("参数格式不正确")


def convert(img):
    """
    float64 转 uint8
    :param img:
    :return:
    """
    for channel in img:
        for arr in channel:
            i = 0
            while i < len(arr):
                if arr[i] > 1.0:
                    arr[i] = 1.0
                elif arr[i] < -1.0:
                    arr[i] = -1.0
                i += 1

    img = img_as_ubyte(img)

    return img


def composite_image(based_img, resized_img):
    """
    合并图片与背景图片
    :param based_img: 背景图片
    :param resized_img: 变形图片
    :return: 合并后的图片
    """
    based_shape = based_img.shape
    resized_shape = resized_img.shape
    start_horizonal = (based_shape[1] - resized_shape[1]) // 2
    end_horizonal = start_horizonal + resized_shape[1]
    start_vertical = (based_shape[0] - resized_shape[0]) // 2
    end_vertical = start_vertical + resized_shape[0]
    based_img[start_vertical:end_vertical, start_horizonal:end_horizonal] = resized_img

    return based_img


def blur_image(base_img, layer=10):
    """
        图片模糊
        :param img: 添加模糊效果的图片
        :param layer: 模糊滤镜层数
        :return: 模糊后的图片
        """
    truncate = 3.5
    i = 0
    while i < layer:
        base_img = gaussian(base_img, sigma=18.0, multichannel=True, truncate=truncate)
        i += 1

    return base_img


original_image = io.imread(argvs[1])
original_width = original_image.shape[1]
original_height = original_image.shape[0]
resized_width = int(argvs[2])
resized_height = int(argvs[3])
upper_size = int(argvs[4])

# 计算变形比例
width_ratio = resized_width / original_width
height_ratio = resized_height / original_height

if width_ratio > height_ratio:
    dim = (resized_height, int(original_width * height_ratio))
elif width_ratio < height_ratio:
    dim = (int(original_height * width_ratio), resized_width)
else:
    dim = (resized_height, resized_width)

if dim[0] == original_height and dim[1] == original_width:
    resized_image = resize(original_image, dim, order=1)
    # 原图不需要缩放，只需要变形底图
    if width_ratio != height_ratio:
        base_image = resize(original_image, (resized_height, resized_width), order=1, anti_aliasing=True)
        base_image = blur_image(base_image)
        resized_image = composite_image(base_image, resized_image)
else:
    # 原图需要缩放
    if min(width_ratio, height_ratio) < 1:
        resized_image = resize(original_image, dim, order=1, anti_aliasing=True)
    else:
        resized_image = resize(original_image, dim, order=1)

    if width_ratio != height_ratio:
        base_image = resize(original_image, (resized_height, resized_width), order=1, anti_aliasing=True)
        base_image = blur_image(base_image)
        resized_image = composite_image(base_image, resized_image)

resized_image = convert(resized_image)

based_dir = argvs[1].split("/")
based_dir[-1] = based_dir[-1].split(".")[0]
based_dir = '/' . join(based_dir)
if not os.path.exists(based_dir):
    os.makedirs(based_dir)

based_image = based_dir + '/' + str(resized_width) + 'x' + str(resized_height) + '_v2.' + argvs[1].split('.')[-1]
print(based_image)

io.imsave(based_image, resized_image)

image_size = getsize(based_image)

if image_size > 1024 * upper_size:
    image = Image.open(based_image)
    quality = 100
    while getsize(based_image) > upper_size * 1024 and quality > 0:
        quality -= 1
        image.save(based_image, optimize=True, quality=quality)

    print(quality)
