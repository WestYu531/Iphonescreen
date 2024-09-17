import os
import json
from datasets import load_dataset
from PIL import Image, ImageDraw
import random

# 加载 ios-app-icons 数据集
dataset = load_dataset("ppierzc/ios-app-icons")
images = [example['image'] for example in dataset['train']]  # 提取图像数据

def create_rounded_corners(image, radius):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, *image.size], radius=radius, fill=255)
    image.putalpha(mask)
    return image

def select_random_images(image_list, new_size):
    num_images = random.randint(1, 24)  # 随机选择1到24张图片
    return random.sample([img.resize(new_size) for img in image_list], num_images)

def compose_images(background_path, selected_images, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, idx, corner_radius=25):
    background = Image.open(background_path)
    positions = []
    row, col = 0, 0

    for img in selected_images:
        img = create_rounded_corners(img.convert("RGBA"), corner_radius)
        x_pos, y_pos = x_start + col * x_step, y_start + row * y_step
        background.paste(img, (x_pos, y_pos), img)
        positions.append({
            "caption": f"Image {len(positions) + 1}",
            "coordinates": [x_pos, y_pos, x_pos + img.width, y_pos + img.height],
            "background_image": os.path.basename(background_path)
        })
        col = (col + 1) % rowMaxImages
        if col == 0: row += 1

    # 将背景图片从 RGBA 转换为 RGB 模式并保存
    background = background.convert("RGB")
    background.save(os.path.join(output_dir, f"combined_image_{idx}.jpg"))

    # 保存json数据
    json_filename = f"image_data_{idx}.json"
    json_file_path = os.path.join(output_dir, json_filename)
    with open(json_file_path, "w") as f:
        json.dump(positions, f, indent=4)

def generate_images(num_images, background_path, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius):
    os.makedirs(output_dir, exist_ok=True)

    for idx in range(1, num_images + 1):
        selected_images = select_random_images(images, new_size)
        compose_images(background_path, selected_images, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, idx, corner_radius)

# 主程序
if __name__ == "__main__":
    # 固定参数
    background_path = "/Users/westyu/Desktop/1.png"  # 背景图片路径
    output_dir = "/Users/westyu/Desktop/iphone"  # 输出目录
    generateNum = 5  # 生成图片的数量

    # 图片和布局参数
    original_bg_width = 1170  # 背景图片的原始宽度
    original_bg_height = 2532  # 背景图片的原始高度
    bg_width, bg_height = Image.open(background_path).size  # 实际背景图片尺寸
    width_factor = bg_width / original_bg_width  # 宽度比例因子
    height_factor = bg_height / original_bg_height  # 高度比例因子
    new_size = (int(180 * width_factor), int(180 * height_factor))  # 小图片调整后的大小

    # 布局参数（x和y坐标起始点和步长）
    x_start = int(90 * width_factor)
    y_start = int(231 * height_factor)
    x_step = int(270 * width_factor)
    y_step = int(294 * height_factor)
    rowMaxImages = 4  # 每行的最大图片数

    # 圆角半径
    corner_radius = 25

    # 生成组合图片
    generate_images(generateNum, background_path, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius)
