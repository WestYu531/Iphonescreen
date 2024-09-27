import os
import json
from PIL import Image, ImageDraw, ImageFont
import random
import requests
from io import BytesIO


class AppInfo:
    def __init__(self, title, icon, description):
        self.title = title
        self.icon = icon
        self.description = description  

    def __repr__(self):
        return f"AppInfo(title={self.title}, icon={self.icon}, description={self.description})"


def load_apps_as_objects(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    apps = []
    for entry in data:
        app = AppInfo(
            title=entry.get('title', 'No Title'),
            icon=entry.get('icon', 'No Icon'),
            description=entry.get('description', 'No Description')  
        )
        apps.append(app)
    
    return apps

def download_image_from_url(url):
    """从远程URL下载图像"""
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def create_rounded_corners(image, radius):
    """创建圆角效果"""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, *image.size], radius=radius, fill=255)
    image.putalpha(mask)
    return image

def add_text_to_image_centered(image, text, center_position, font_path=None, font_size=30, color=(255, 255, 255), y_offset=-100):
    """在图像上基于中间坐标添加文字，并调整纵坐标"""
    draw = ImageDraw.Draw(image)
    
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print("字体文件未找到，使用默认字体")
            font = ImageFont.load_default(font_size)
    else:
        font = ImageFont.load_default(font_size)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = center_position[0] - text_width // 2
    y = center_position[1] - text_height // 2 + 70
    
    draw.text((x, y), text, font=font, fill=color)
    
    return image

def select_random_images(app_list, new_size):
    """随机选择1到24个应用，并返回调整大小后的图像和对应的description、title和icon"""
    num_images = random.randint(1, 24)
    selected = random.sample(app_list, num_images)
    
    selected_resized = []
    for app in selected:
        try:
            if app.icon.startswith('http'):  # 如果图标是远程URL，先下载
                img = download_image_from_url(app.icon).resize(new_size)
            else:  # 如果是本地文件路径，直接打开
                img = Image.open(app.icon).resize(new_size)
            selected_resized.append((img, app))  # 将图像和 AppInfo 对象一起存储
        except Exception as e:
            print(f"无法处理图标 {app.icon}: {e}")
    
    return selected_resized

def compose_images(background_path, selected_images_with_apps, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, idx, corner_radius=25, font_path=None, font_size=30, add_text=False):
    """将选择的图片组合到背景图片上，添加第一个词作为标题（可选），并保存位置信息和description到JSON文件"""
    background = Image.open(background_path)
    positions = []
    row, col = 0, 0

    for img, app in selected_images_with_apps:  # 这里的 app 是 AppInfo 对象
        img = create_rounded_corners(img.convert("RGBA"), corner_radius)
        x_pos, y_pos = x_start + col * x_step, y_start + row * y_step
        background.paste(img, (x_pos, y_pos), img)
        
        if add_text:
            text_center_position = (x_pos + img.width // 2, y_pos + img.height // 2)
            
            # 只提取 title 的第一个词
            first_word_of_title = app.title.split()[0]
            
            # 将标题的第一个词作为文字添加到图像上
            background = add_text_to_image_centered(background, first_word_of_title, text_center_position, font_path, font_size, color=(255, 255, 255), y_offset=-100)
        
        positions.append({
            "title": app.title,  # 保存完整的 title
            "icon": app.icon,  # 保存 AppInfo 中的 icon
            "description": app.description,  # 保存 AppInfo 中的 description
            "coordinates": [x_pos, y_pos, x_pos + img.width, y_pos + img.height],  # 保存图像的位置
            "background_image": os.path.basename(background_path)  # 背景图片的文件名
        })
        col = (col + 1) % rowMaxImages
        if col == 0: row += 1

    background = background.convert("RGB")
    background.save(os.path.join(output_dir, f"combined_image_{idx}.jpg"))

    json_filename = f"image_data_{idx}.json"
    json_file_path = os.path.join(output_dir, json_filename)
    with open(json_file_path, "w") as f:
        json.dump(positions, f, indent=4)

def generate_images_for_each_background(idx, background_path, num_images, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius, font_path=None, font_size=30, add_text=False):
    """为文件夹中的每张背景图片生成组合图片，控制是否添加应用标题文字，并保存description到JSON"""
    
    os.makedirs(output_dir, exist_ok=True)

    if os.path.isfile(background_path) and background_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        for i in range(1, num_images + 1):
            selected_images_with_apps = select_random_images(apps, new_size)
            compose_images(background_path, selected_images_with_apps, x_start, y_start, x_step, y_step, rowMaxImages, output_dir, f"{idx}_{i}", corner_radius, font_path, font_size, add_text=add_text)

# 主程序
if __name__ == "__main__":
    json_file_path = '/Users/westyu/Desktop/cccjson/merged_unique_apps.json'  # JSON 文件路径
    apps = load_apps_as_objects(json_file_path)  # 加载 AppInfo 对象列表

    
    user_input = input("add app name under the icon? (yes/no): ").strip().lower()
    add_text = user_input == "yes"

    # 固定参数
    background_dir = "/Users/westyu/Desktop/background"  # 背景图片文件夹路径
    output_dir = "/Users/westyu/Desktop/iphone"  # 输出目录
    generateNum = 2  # 为每张背景图生成图片的数量
    font_path = "/System/Library/Fonts/SFNS.ttf"  # 字体文件路径
    font_size = 40  # 字体大小

    # 图片和布局参数
    original_bg_width = 1170.  # 背景图片的原始宽度
    original_bg_height = 2532.  # 背景图片的原始高度
    listofbackground = os.listdir(background_dir)
    listofbackground = sorted(listofbackground)
    
    for idx, background_filename in enumerate(listofbackground):
        background_path = os.path.join(background_dir, background_filename)
        if os.path.isfile(background_path) and background_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            bg_width, bg_height = Image.open(background_path).size
            width_factor = bg_width / original_bg_width
            height_factor = bg_height / original_bg_height
            new_size = (int(180 * width_factor), int(180 * height_factor))
            convertor = width_factor * font_size

            x_start = int(90 * width_factor)
            y_start = int(231 * height_factor)
            x_step = int(270 * width_factor)
            y_step = int(294 * height_factor)
            rowMaxImages = 4  # 每行的最大图片数

            corner_radius = 25

            generate_images_for_each_background(idx, background_path, generateNum, output_dir, new_size, x_start, y_start, x_step, y_step, rowMaxImages, corner_radius, font_size=convertor, font_path=font_path, add_text=add_text)