"""
高精细度红楼梦【通灵朱玉】图标全套资源生成器
使用 Pillow + Numpy 超采样渲染，生成：
1. assets/icons/icon-512x512.png
2. assets/icons/apple-touch-icon.png (180x180)
3. assets/icons/favicon-32x32.png
4. assets/icons/favicon-16x16.png
5. favicon.ico & assets/icons/favicon.ico (含 16, 32, 48, 64 多层)
6. assets/icons/favicon.svg (深浅色标签页高清晰矢量)
7. assets/icons/brand-logo.svg (顶部导航栏高清国风徽标)
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.makedirs("assets/icons", exist_ok=True)

# 1. 采用超采样技术 (Supersampling at 1024x1024) 绘制极致平滑与温润质感的通灵朱玉佩
SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

cx, cy = 512, 530

# 创建通灵宝玉佩佩身路径点 (上敛下微丰、四角优雅弧度如意方圆璧)
def get_gem_points(scale=1.0, offset_y=0):
    points = []
    # 顶部微凸如意弧
    # 左上角
    w = 340 * scale
    h = 390 * scale
    y_center = cy + offset_y
    
    # 按照古典八角玉牌计算参数化多边形
    # 顶部如意微拱
    for t in np.linspace(-math.pi * 0.4, -math.pi * 0.6, 20):
        # 顶部拱起
        pass
    
    # 构造平滑对称玉佩轮廓
    # 顶部 (cx-w*0.5, y_center-h) 到 (cx+w*0.5, y_center-h)
    pts = [
        # 顶部中央穿环处微凹与拱起
        (cx - w * 0.25, y_center - h * 0.94),
        (cx - w * 0.48, y_center - h * 0.88),
        (cx - w * 0.72, y_center - h * 0.72),
        (cx - w * 0.92, y_center - h * 0.45),
        (cx - w * 0.98, y_center - h * 0.1),
        (cx - w * 0.96, y_center + h * 0.25),
        (cx - w * 0.88, y_center + h * 0.6),
        (cx - w * 0.65, y_center + h * 0.85),
        (cx - w * 0.35, y_center + h * 0.98),
        (cx, y_center + h),
        (cx + w * 0.35, y_center + h * 0.98),
        (cx + w * 0.65, y_center + h * 0.85),
        (cx + w * 0.88, y_center + h * 0.6),
        (cx + w * 0.96, y_center + h * 0.25),
        (cx + w * 0.98, y_center - h * 0.1),
        (cx + w * 0.92, y_center - h * 0.45),
        (cx + w * 0.72, y_center - h * 0.72),
        (cx + w * 0.48, y_center - h * 0.88),
        (cx + w * 0.25, y_center - h * 0.94),
        (cx, y_center - h * 0.92),
    ]
    return pts

# A. 绘制顶部挂绳与同心结
cord_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
cord_draw = ImageDraw.Draw(cord_img)

# 挂绳双线
cord_draw.line([(cx - 10, 30), (cx - 10, 150)], fill=(185, 28, 28, 240), width=18)
cord_draw.line([(cx + 10, 30), (cx + 10, 150)], fill=(220, 38, 38, 240), width=18)
# 同心结纽
cord_draw.ellipse([cx - 70, 70, cx + 70, 120], fill=(160, 20, 20, 255), outline=(230, 180, 50, 240), width=6)
cord_draw.ellipse([cx - 30, 75, cx + 30, 115], fill=(212, 175, 55, 255))
cord_draw.ellipse([cx - 14, 82, cx + 14, 108], fill=(130, 15, 15, 255))

# 金环穿梁
cord_draw.ellipse([cx - 50, 130, cx + 50, 185], fill=(212, 175, 55, 255), outline=(138, 97, 20, 255), width=8)
cord_draw.ellipse([cx - 32, 142, cx + 32, 173], fill=(0, 0, 0, 0))

# B. 佩体阴影
shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_pts = get_gem_points(scale=1.03, offset_y=28)
shadow_draw.polygon(shadow_pts, fill=(0, 0, 0, 140))
shadow = shadow.filter(ImageFilter.GaussianBlur(24))

# C. 外层金镶玉边框 (Imperial Gold Frame)
gold_frame = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
gold_draw = ImageDraw.Draw(gold_frame)
pts_gold = get_gem_points(scale=1.0)
gold_draw.polygon(pts_gold, fill=(212, 175, 55, 255), outline=(138, 97, 20, 255), width=10)

# D. 内层朱砂温润玉芯 (Vermilion Jade Core)
jade_mask = Image.new("L", (SIZE, SIZE), 0)
jade_mask_draw = ImageDraw.Draw(jade_mask)
pts_inner = get_gem_points(scale=0.91, offset_y=4)
jade_mask_draw.polygon(pts_inner, fill=255)

# 生成朱砂红玉髓径向渐变
jade_arr = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
Y, X = np.ogrid[:SIZE, :SIZE]
dist_from_c = np.sqrt((X - cx)**2 + (Y - (cy - 40))**2)
# 渐变从鲜朱砂 #dc2626 到 深殷红 #7f1d1d 到 墨红 #450a0a
r_norm = np.clip(dist_from_c / 460.0, 0, 1.0)

red_channel = (220 * (1 - r_norm) + 75 * r_norm).astype(np.uint8)
green_channel = (38 * (1 - r_norm) + 10 * r_norm).astype(np.uint8)
blue_channel = (38 * (1 - r_norm) + 10 * r_norm).astype(np.uint8)
alpha_channel = np.ones((SIZE, SIZE), dtype=np.uint8) * 255

jade_arr[..., 0] = red_channel
jade_arr[..., 1] = green_channel
jade_arr[..., 2] = blue_channel
jade_arr[..., 3] = alpha_channel
jade_img = Image.fromarray(jade_arr, "RGBA")
jade_img.putalpha(jade_mask)

# E. 玉石高光微泽 (Sheen)
sheen_mask = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
sheen_draw = ImageDraw.Draw(sheen_mask)
sheen_draw.ellipse([cx - 240, cy - 320, cx + 180, cy - 80], fill=(255, 255, 255, 45))
sheen_mask = sheen_mask.filter(ImageFilter.GaussianBlur(36))

# F. 玉内圈金色回字描金线
in_gold = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
in_gold_draw = ImageDraw.Draw(in_gold)
pts_gold_inner = get_gem_points(scale=0.86, offset_y=5)
in_gold_draw.polygon(pts_gold_inner, fill=(0, 0, 0, 0), outline=(243, 229, 171, 160), width=5)

# G. 中心小篆金文“红”字（或者以书法篆刻金石风格呈现）
char_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
char_draw = ImageDraw.Draw(char_img)

# 尝试寻找系统书法中文字体（如华文楷体、楷体、隶书、思源宋体等）
font = None
font_paths = [
    "C:/Windows/Fonts/simkai.ttf",   # 楷体
    "C:/Windows/Fonts/STKAITI.TTF",  # 华文楷体
    "C:/Windows/Fonts/simsun.ttc",   # 宋体
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf"    # 黑体
]
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 360)
            break
        except Exception:
            continue

if font is None:
    font = ImageFont.load_default()

# 绘制烫金质感文字阴影与立体高光
text = "红"
bbox = char_draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = cx - tw / 2 - bbox[0]
ty = (cy + 15) - th / 2 - bbox[1]

# 阴影
char_draw.text((tx, ty + 12), text, font=font, fill=(30, 5, 5, 230))
char_draw.text((tx, ty + 6), text, font=font, fill=(70, 15, 10, 200))
# 金身
char_draw.text((tx, ty), text, font=font, fill=(245, 205, 90, 255))
# 亮金高光
char_draw.text((tx - 2, ty - 2), text, font=font, fill=(255, 245, 180, 180))

# H. 祥云与灵珠点缀 (如意云纹)
cloud_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
cloud_draw = ImageDraw.Draw(cloud_img)
# 顶部祥云护纽
cloud_draw.arc([cx - 180, cy - 350, cx - 80, cy - 250], 180, 360, fill=(245, 205, 90, 160), width=6)
cloud_draw.arc([cx + 80, cy - 350, cx + 180, cy - 250], 180, 360, fill=(245, 205, 90, 160), width=6)
# 底部灵珠
cloud_draw.ellipse([cx - 15, cy + 335, cx + 15, cy + 365], fill=(255, 245, 180, 240), outline=(138, 97, 20, 255), width=3)

# 组合所有图层
final_canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
final_canvas.paste(shadow, (0, 0), shadow)
final_canvas.paste(cord_img, (0, 0), cord_img)
final_canvas.paste(gold_frame, (0, 0), gold_frame)
final_canvas.paste(jade_img, (0, 0), jade_img)
final_canvas.paste(sheen_mask, (0, 0), sheen_mask)
final_canvas.paste(in_gold, (0, 0), in_gold)
final_canvas.paste(cloud_img, (0, 0), cloud_img)
final_canvas.paste(char_img, (0, 0), char_img)

# 导出各规格高清位图 (利用 Lanczos 抗锯齿高质量缩小)
p512 = final_canvas.resize((512, 512), Image.Resampling.LANCZOS)
p512.save("assets/icons/icon-512x512.png", "PNG")

p180 = final_canvas.resize((180, 180), Image.Resampling.LANCZOS)
p180.save("assets/icons/apple-touch-icon.png", "PNG")

p64 = final_canvas.resize((64, 64), Image.Resampling.LANCZOS)
p64.save("assets/icons/favicon-64x64.png", "PNG")

p32 = final_canvas.resize((32, 32), Image.Resampling.LANCZOS)
p32.save("assets/icons/favicon-32x32.png", "PNG")

p16 = final_canvas.resize((16, 16), Image.Resampling.LANCZOS)
p16.save("assets/icons/favicon-16x16.png", "PNG")

# 生成标准多分辨率 Windows/Web Favicon.ico
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
final_canvas.save("favicon.ico", format="ICO", sizes=ico_sizes)
final_canvas.save("assets/icons/favicon.ico", format="ICO", sizes=ico_sizes)

print("位图与 ICO 资源生成成功！")

# 2. 生成专为 SVG Favicon 优化的高质量自适应矢量文件
# SVG 矢量版不仅在任何 DPI 下永不失真，还支持系统深浅色自适应！
svg_favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="100%" height="100%">
  <defs>
    <linearGradient id="gGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fff4c2" />
      <stop offset="35%" stop-color="#d4af37" />
      <stop offset="70%" stop-color="#aa7c11" />
      <stop offset="100%" stop-color="#694803" />
    </linearGradient>
    <radialGradient id="gJade" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="#e53e3e" />
      <stop offset="45%" stop-color="#b91c1c" />
      <stop offset="85%" stop-color="#7f1d1d" />
      <stop offset="100%" stop-color="#450a0a" />
    </radialGradient>
    <filter id="fShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.45" />
    </filter>
  </defs>

  <!-- 顶部红绳纽 -->
  <path d="M 32 1 L 32 8" stroke="#b91c1c" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="32" cy="7" r="3.5" fill="#d4af37" stroke="#7a5509" stroke-width="0.8"/>

  <!-- 金镶玉佩体 (外圈金身) -->
  <path d="M 18 10 
           C 25 8, 39 8, 46 10 
           C 57 12, 60 22, 59 34 
           C 58 48, 51 59, 32 62 
           C 13 59, 6 48, 5 34 
           C 4 22, 7 12, 18 10 Z"
        fill="url(#gGold)"
        stroke="#523602"
        stroke-width="0.8"
        filter="url(#fShadow)" />

  <!-- 朱砂红玉芯 -->
  <path d="M 19 12 
           C 25 10.5, 39 10.5, 45 12 
           C 54.5 14, 57 23, 56 34 
           C 55 46.5, 48.5 56.5, 32 59.5 
           C 15.5 56.5, 9 46.5, 8 34 
           C 7 23, 9.5 14, 19 12 Z"
        fill="url(#gJade)" />

  <!-- 内圈金线 -->
  <path d="M 20 14 
           C 25 13, 39 13, 44 14 
           C 52 16, 54 24, 53 34 
           C 52 44, 46 54, 32 57 
           C 18 54, 12 44, 11 34 
           C 10 24, 12 16, 20 14 Z"
        fill="none"
        stroke="#fef08a"
        stroke-width="0.7"
        opacity="0.75" />

  <!-- 楷意金字“红” (精修笔画，在小尺寸下极其清晰醒目) -->
  <g fill="#ffffff" filter="drop-shadow(0px 1px 1px rgba(0,0,0,0.85))">
    <!-- 绞丝旁 糸 -->
    <!-- 上撇折与绞结 -->
    <path d="M 23 23 C 21 26, 17 28, 20 31 C 22.5 32.5, 25 29, 23.5 26 Z" fill="#fef08a"/>
    <!-- 下撇折与绞结 -->
    <path d="M 20 32 C 17 35, 15 39, 18 42 C 22 43.5, 24 39, 22 36 Z" fill="#fef08a"/>
    <!-- 三点提丝 -->
    <circle cx="17" cy="46" r="1.3" fill="#fde047" />
    <circle cx="21" cy="47" r="1.3" fill="#fde047" />
    <circle cx="25" cy="45" r="1.3" fill="#fde047" />

    <!-- 右侧“工”部 -->
    <!-- 上横 -->
    <path d="M 31 25 C 36 23.5, 42 23.5, 47 25 C 47.5 26.5, 45 27.5, 39 27 C 34 26.5, 31.5 26, 31 25 Z" fill="#fff" />
    <!-- 中竖 -->
    <rect x="37.5" y="26" width="3" height="19" rx="1.2" fill="#fef08a" />
    <!-- 下横 -->
    <path d="M 29.5 45 C 36 43.5, 43 43.5, 48.5 45 C 49 46.5, 46 47.8, 39 47.2 C 33 46.8, 30 46.2, 29.5 45 Z" fill="#fff" />
  </g>
  
  <!-- 宝玉点睛通灵珠 -->
  <circle cx="39" cy="35" r="1.4" fill="#ffffff" />
</svg>
'''

with open("assets/icons/favicon.svg", "w", encoding="utf-8") as f:
    f.write(svg_favicon.strip())

# 3. 生成用于导航栏和展示的大图 Brand Logo SVG
svg_brand = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100%" height="100%">
  <defs>
    <linearGradient id="bgold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fff8d6" />
      <stop offset="25%" stop-color="#e8bf53" />
      <stop offset="60%" stop-color="#caa035" />
      <stop offset="85%" stop-color="#a87a1a" />
      <stop offset="100%" stop-color="#6e4d06" />
    </linearGradient>
    <linearGradient id="bgold2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="50%" stop-color="#d4af37" />
      <stop offset="100%" stop-color="#8a6114" />
    </linearGradient>
    <radialGradient id="bjade" cx="50%" cy="38%" r="65%">
      <stop offset="0%" stop-color="#ef4444" />
      <stop offset="30%" stop-color="#dc2626" />
      <stop offset="65%" stop-color="#991b1b" />
      <stop offset="90%" stop-color="#680b0b" />
      <stop offset="100%" stop-color="#3d0303" />
    </radialGradient>
    <radialGradient id="bsheen" cx="40%" cy="25%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.5" />
      <stop offset="50%" stop-color="#fca5a5" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#dc2626" stop-opacity="0" />
    </radialGradient>
    <filter id="bshadow" x="-20%" y="-15%" width="140%" height="135%">
      <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.55" />
    </filter>
    <filter id="bglow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.2" flood-color="#4a0808" flood-opacity="0.9" />
    </filter>
  </defs>

  <!-- 顶部朱红祥纽与同心结 -->
  <g>
    <!-- 穿梁红绳 -->
    <path d="M 50 2 L 50 14" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="50" cy="8" rx="8" ry="4" fill="#991b1b" stroke="#d4af37" stroke-width="1.2"/>
    <!-- 金佩纽梁 -->
    <ellipse cx="50" cy="14" rx="7" ry="4.5" fill="url(#bgold)" stroke="#6e4d06" stroke-width="0.8"/>
    <ellipse cx="50" cy="14" rx="3.5" ry="2" fill="#2d0505"/>
  </g>

  <!-- 佩体外廓：金镶玉典雅玉璧造型 -->
  <path d="M 28 14 
           C 38 11.5, 62 11.5, 72 14 
           C 89 17, 95 33, 93 52 
           C 91 73, 79 90, 50 94 
           C 21 90, 9 73, 7 52 
           C 5 33, 11 17, 28 14 Z"
        fill="url(#bgold)"
        stroke="#593b04"
        stroke-width="1.2"
        filter="url(#bshadow)" />

  <!-- 朱砂红玉石玉心 -->
  <path d="M 30 17 
           C 39 14.5, 61 14.5, 70 17 
           C 84 20, 89 35, 87 52 
           C 85 70, 74 86, 50 89.5 
           C 26 86, 15 70, 13 52 
           C 11 35, 16 20, 30 17 Z"
        fill="url(#bjade)"
        stroke="#400303"
        stroke-width="0.8" />

  <!-- 内部双层描金回纹圈 -->
  <path d="M 32 20 
           C 40 18, 60 18, 68 20 
           C 80 23, 84 36, 82 52 
           C 80 67, 70 82, 50 85 
           C 30 82, 20 67, 18 52 
           C 16 36, 20 23, 32 20 Z"
        fill="none"
        stroke="url(#bgold2)"
        stroke-width="1"
        stroke-dasharray="3,1.5"
        opacity="0.8" />

  <!-- 玉髓温润高光 -->
  <path d="M 30 17 
           C 39 14.5, 61 14.5, 70 17 
           C 81 19.5, 85 29, 82 42 
           C 72 28, 56 22, 36 24 
           C 24 25, 17 31, 14 40 
           C 13 31, 18 20, 30 17 Z"
        fill="url(#bsheen)" />

  <!-- 祥云如意耳与灵珠点缀 -->
  <g fill="none" stroke="url(#bgold)" stroke-width="1" opacity="0.8">
    <path d="M 18 25 C 13 21, 20 18, 25 20" />
    <path d="M 82 25 C 87 21, 80 18, 75 20" />
    <!-- 底部祥云托珠 -->
    <circle cx="50" cy="83" r="2" fill="#fff5c0" stroke="#8a6114" stroke-width="0.8"/>
  </g>

  <!-- 中心核心金文小篆“红”字（带浮雕微光与纯正书法金石气） -->
  <g filter="url(#bglow)" fill="url(#bgold2)">
    <!-- 绞丝旁 糸 -->
    <!-- 顶纽 -->
    <circle cx="36" cy="35" r="2.6" fill="#fff5c0"/>
    <!-- 绞纽折叠环 1 -->
    <path d="M 35 37 C 32 41, 28 44, 32 48 C 36 50, 40 45, 37 41 Z" />
    <!-- 绞纽折叠环 2 -->
    <path d="M 32 48 C 28 52, 25 56, 30 60 C 35 62, 39 57, 36 53 Z" />
    <!-- 垂绦三丝 -->
    <path d="M 28 63 C 27 68, 24 73, 23 75 C 24.5 75, 26 71, 29 66 Z" fill="#ffeaa7" />
    <path d="M 33 63 L 32.5 76 L 34.5 76 L 34.5 63 Z" fill="#ffeaa7" />
    <path d="M 37 62 C 38 67, 41 72, 43 75 C 43 73, 40 68, 38.5 63 Z" fill="#ffeaa7" />

    <!-- “工”字部 (鼎立天地之姿) -->
    <!-- 上云横 -->
    <path d="M 48 39 C 55 36.5, 63 36.5, 70 39 C 71 40.5, 68 42, 66 41.5 C 61 40, 56 40, 51 41.5 C 49 42, 47.5 40.5, 48 39 Z" fill="#ffffff" />
    <!-- 中悬针竖 -->
    <path d="M 57 39.5 L 61 39.5 L 60.5 67 L 57.5 67 Z" fill="#fff5c0" />
    <!-- 下承重横 -->
    <path d="M 46 68 C 54 66.5, 65 66.5, 72 68 C 73 69.5, 70.5 71, 68 70.5 C 62 69.2, 55 69.2, 49 70.5 C 47.5 71, 45 69.5, 46 68 Z" fill="#ffffff" />
    
    <!-- 宝玉通灵明珠 -->
    <circle cx="59" cy="53" r="2.4" fill="#ffffff" />
    <circle cx="59" cy="53" r="1.2" fill="#fef08a" />
  </g>
</svg>
'''

with open("assets/icons/brand-logo.svg", "w", encoding="utf-8") as f:
    f.write(svg_brand.strip())

print("SVG 图标资源生成成功！")
