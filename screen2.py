import os
import json
from datasets import load_dataset
from PIL import Image, ImageDraw, ImageFont
import random

# 加载 ios-app-icons 数据集
dataset = load_dataset("ppierzc/ios-app-icons")
images = [example['image'] for example in dataset['train']]  # 提取图像数据
captions = dataset['train']['caption']  # 提取caption数据

def create_rounded_corners(image, radius):
    """创建圆角效果"""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, *image.size], radius=radius, fill=255)
    image.putalpha(mask)
    return image

def add_text_to_image_centered(image, text, center_position, font_path=None, font_size=30, color=(255, 255, 255), y_offset=-100):
    """
    在图像上基于中间坐标添加文字，并调整纵坐标
    
    参数:
    - image: PIL.Image 对象, 需要添加文字的图像
    - text: str, 需要添加的文字
    - center_position: tuple, 文字中间的(x, y)坐标位置
    - font_path: str, 字体文件的路径（可选）, 如果不提供，将使用默认字体
    - font_size: int, 字体大小，默认30
    - color: tuple, 文字颜色，默认为白色 (255, 255, 255)
    - y_offset: int, 调整纵坐标的偏移量，默认为 -100，向上移动100像素
    
    返回:
    - image: 添加文字后的图像
    """
    # 创建一个可编辑的图像对象
    draw = ImageDraw.Draw(image)
    
    # 加载字体
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print("字体文件未找到，使用默认字体")
            font = ImageFont.load_default(font_size)
    else:
            font = ImageFont.load_default(font_size)
    
    # 获取文字的边界框
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 计算左上角的坐标（基于中间坐标），并将纵坐标减去y_offset
    x = center_position[0] - text_width // 2
    y = center_position[1] - text_height // 2 + 70  # 调整纵坐标
    
    # 在指定位置绘制文字
    draw.text((x, y), text, font=font, fill=color)
    
    return image

def select_random_images(image_list, caption_list, new_size):
    """随机选择1到24张图片，并返回调整大小后的图像和对应的caption"""
    num_images = random.randint(1, 24)  # 随机选择1到24张图片
    selected = random.sample(list(zip(image_list, caption_list)), num_images)  # 随机选择图像和对应的caption
    selected_resized = [(img.resize(new_size), caption) for img, caption in selected]  # 调整图像大小
    return selected_resized

def compose_images(background_path, selected_images_with_captions, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, idx, corner_radius=25, font_path=None, font_size=30):
    """将选择的图片组合到背景图片上，添加固定的"app"文字，保存位置信息和caption到JSON文件"""
    background = Image.open(background_path)
    positions = []
    row, col = 0, 0

    for img, caption in selected_images_with_captions:
        img = create_rounded_corners(img.convert("RGBA"), corner_radius)  # 转换图像为RGBA并应用圆角
        x_pos, y_pos = x_start + col * x_step, y_start + row * y_step  # 计算每张图片的位置
        background.paste(img, (x_pos, y_pos), img)  # 将图片粘贴到背景上
        
        # 计算文字的位置 (在图片的中心)，并减去100像素的纵坐标偏移
        text_center_position = (x_pos + img.width // 2, y_pos + img.height // 2)
        
        # 在图片上添加固定的 "app" 文字
        background = add_text_to_image_centered(background, "app", text_center_position, font_path, font_size, color=(255, 255, 255), y_offset=-100)
        
        # 保存JSON中的caption，依然使用从数据集中获取的caption
        positions.append({
            "caption": caption,  # 保存数据集中的caption
            "coordinates": [x_pos, y_pos, x_pos + img.width, y_pos + img.height],
            "background_image": os.path.basename(background_path)
        })
        col = (col + 1) % rowMaxImages  # 控制每行的图片数量
        if col == 0: row += 1

    background = background.convert("RGB")  # 将背景图像从RGBA转换回RGB格式
    background.save(os.path.join(output_dir, f"combined_image_{idx}.jpg"))  # 保存组合后的图像

    # 保存JSON文件
    json_filename = f"image_data_{idx}.json"
    json_file_path = os.path.join(output_dir, json_filename)
    with open(json_file_path, "w") as f:
        json.dump(positions, f, indent=4)

def generate_images_for_each_background(idx, background_path, num_images, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius, font_path=None, font_size=30):
    """为文件夹中的每张背景图片生成组合图片，添加固定的"app"文字，并保存caption到JSON"""
    os.makedirs(output_dir, exist_ok=True)

    # 遍历背景图片文件夹中的每张图片
    if os.path.isfile(background_path) and background_path.lower().endswith(('.png', '.jpg', '.jpeg')):  # 确保文件是图片
        for i in range(1, num_images + 1):
            selected_images_with_captions = select_random_images(images, captions, new_size)  # 选择随机图片及其对应的caption
            compose_images(background_path, selected_images_with_captions, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, f"{idx}_{i}", corner_radius, font_path, font_size)

# 主程序
if __name__ == "__main__":
    # 固定参数
    background_dir = "/Users/westyu/Desktop/background2"  # 背景图片文件夹路径
    output_dir = "/Users/westyu/Desktop/iphone"  # 输出目录
    generateNum = 5  # 为每张背景图生成图片的数量
    font_path = "/System/Library/Fonts/SFNS.ttf"  # 字体文件路径
    font_size = 40  # 字体大小

    # 图片和布局参数
    original_bg_width = 1170.  # 背景图片的原始宽度
    original_bg_height = 2532.  # 背景图片的原始高度
    listofbackground = os.listdir(background_dir)
    listofbackground = sorted(listofbackground)
    # 遍历背景图片，自动根据每张背景图的尺寸调整
    for idx, background_filename in enumerate(listofbackground):
        background_path = os.path.join(background_dir, background_filename)
        if os.path.isfile(background_path) and background_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            bg_width, bg_height = Image.open(background_path).size  # 实际背景图片尺寸
            width_factor = bg_width / original_bg_width  # 宽度比例因子
            height_factor = bg_height / original_bg_height  # 高度比例因子
            new_size = (int(180 * width_factor), int(180 * height_factor))  # 小图片调整后的大小
            convertor = width_factor * font_size

            # 布局参数（x和y坐标起始点和步长）
            x_start = int(90 * width_factor)
            y_start = int(231 * height_factor)
            x_step = int(270 * width_factor)
            y_step = int(294 * height_factor)
            rowMaxImages = 4  # 每行的最大图片数

            # 圆角半径
            corner_radius = 25

            # 为每张背景图片生成组合图片
            generate_images_for_each_background(idx,background_path, generateNum, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius, font_size=convertor, font_path=font_path)
