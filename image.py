import cv2
import sys
import os

# 取得参数列表
argvs = sys.argv

# 参数校验
if len(argvs) < 5:
    sys.exit('参数不符合要求')


def blur_image(img, layer=10):
    """
    图片模糊
    :param img: 添加模糊效果的图片
    :param layer: 模糊滤镜层数
    :return: 模糊后的图片
    """
    ksize = (80, 80)
    i = 0
    while i < layer:
        img = cv2.blur(img, ksize)
        i += 1

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


# 解析参数
original_image = argvs[1]
resized_width = int(argvs[2])
resized_height = int(argvs[3])
resized_size = int(argvs[4])

# 获取图片的原始宽、高、大小
original_img = cv2.imread(original_image)
shape = original_img.shape
original_width = shape[1]
original_height = shape[0]
original_size = os.path.getsize(original_image)

# 计算缩放比例
width_ratio = resized_width / original_width
height_ratio = resized_height / original_height
dim = (int(original_width * min(width_ratio, height_ratio)), int(original_height * min(width_ratio, height_ratio)))

# 根据模板裁剪或放大
if width_ratio == height_ratio:
    # 等比缩放
    if original_width > resized_width:
        based_img = cv2.resize(original_img, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
    elif original_width < resized_width:
        based_img = cv2.resize(original_img, (resized_width, resized_height), interpolation=cv2.INTER_CUBIC)
elif width_ratio < 1 and height_ratio < 1:
    # 裁剪底图
    based_img = cv2.resize(original_img, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    based_img = blur_image(based_img)
    resized_img = cv2.resize(original_img, dim, interpolation=cv2.INTER_AREA)
    based_img = composite_image(based_img, resized_img)
else:
    # 放大底图
    based_img = cv2.resize(original_img, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
    based_img = blur_image(based_img)
    resized_img = cv2.resize(original_img, dim, interpolation=cv2.INTER_CUBIC)
    based_img = composite_image(based_img, resized_img)

# 保存图片
based_dir = original_image.split("/")
based_dir[-1] = based_dir[-1].split(".")[0]
based_dir = '/' . join(based_dir)
if not os.path.exists(based_dir):
    os.makedirs(based_dir)

based_image = based_dir + '/' + str(resized_width) + 'x' + str(resized_height) + '_v1.' + original_image.split('.')[-1]
cv2.imwrite(based_image, based_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
print(based_image)

# 如果图片 size 超限，则通过降低图片质量的方法限制 size
if os.path.getsize(based_image) > resized_size * 1024:
    quality = 100
    while os.path.getsize(based_image) > resized_size * 1024 and quality > 0:
        quality -= 1
        cv2.imwrite(based_image, based_img, [cv2.IMWRITE_JPEG_QUALITY, quality])

    print(quality)

