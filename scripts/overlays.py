from PIL import Image, ImageDraw, ImageFont
import os

def create_scene_overlay(
    scene_idx,
    total_scenes,
    title,
    subtitle,
    highlights,
    output_path,
    width=1920,
    height=1080
):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_header_bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
        font_header = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 28)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 19)
        font_bullet = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 17)
    except:
        font_header_bold = font_header = font_badge = font_title = font_sub = font_bullet = ImageFont.load_default()

    # 1. Top Bar / Header Branding (Pill at Top Left)
    header_x, header_y = 40, 28
    draw.rounded_rectangle(
        [(header_x, header_y), (header_x + 380, header_y + 44)],
        radius=8,
        fill=(8, 18, 32, 230),
        outline=(0, 180, 255, 180),
        width=1
    )
    draw.text((header_x + 14, header_y + 9), "FlatEarthMap", font=font_header_bold, fill=(0, 220, 255, 255))
    draw.text((header_x + 185, header_y + 11), "v6.4.2  Обзор проекта", font=font_header, fill=(210, 230, 245, 255))

    # 2. Bottom-Right Sleek Floating Card with Scene Info
    card_w = 460
    card_h = 160 + len(highlights) * 26
    card_x = width - card_w - 40
    card_y = height - card_h - 40

    # Frosted glass panel with double outline and subtle glow
    draw.rounded_rectangle(
        [(card_x, card_y), (card_x + card_w, card_y + card_h)],
        radius=14,
        fill=(7, 16, 28, 235),
        outline=(0, 160, 230, 220),
        width=2
    )

    # Accent top border inside card
    draw.line(
        [(card_x + 15, card_y + 2), (card_x + card_w - 15, card_y + 2)],
        fill=(0, 225, 255, 255),
        width=3
    )

    # Scene badge: "РАЗДЕЛ 01 / 10"
    badge_text = f"РАЗДЕЛ {scene_idx:02d} / {total_scenes:02d}"
    draw.rounded_rectangle(
        [(card_x + 24, card_y + 18), (card_x + 160, card_y + 44)],
        radius=6,
        fill=(0, 100, 180, 180),
        outline=(0, 190, 255, 220),
        width=1
    )
    draw.text((card_x + 34, card_y + 22), badge_text, font=font_badge, fill=(255, 255, 255, 255))

    # Scene Title
    draw.text((card_x + 24, card_y + 54), title, font=font_title, fill=(255, 255, 255, 255))

    # Subtitle
    draw.text((card_x + 24, card_y + 92), subtitle, font=font_sub, fill=(130, 205, 245, 255))

    # Separator
    draw.line(
        [(card_x + 24, card_y + 124), (card_x + card_w - 24, card_y + 124)],
        fill=(40, 75, 110, 200),
        width=1
    )

    # Bullets
    by = card_y + 134
    for b in highlights:
        draw.text((card_x + 26, by), "•", font=font_bullet, fill=(0, 220, 255, 255))
        draw.text((card_x + 44, by), b, font=font_bullet, fill=(230, 240, 250, 240))
        by += 26

    # Subtle bottom progress bar
    progress_ratio = scene_idx / total_scenes
    bar_w = card_w - 48
    draw.rounded_rectangle(
        [(card_x + 24, card_y + card_h - 16), (card_x + 24 + bar_w, card_y + card_h - 10)],
        radius=3,
        fill=(20, 40, 65, 255)
    )
    draw.rounded_rectangle(
        [(card_x + 24, card_y + card_h - 16), (card_x + 24 + int(bar_w * progress_ratio), card_y + card_h - 10)],
        radius=3,
        fill=(0, 210, 255, 255)
    )

    img.save(output_path, "PNG")
    return output_path

if __name__ == "__main__":
    p = create_scene_overlay(
        1, 10,
        "Введение и обзор",
        "Азимутальная эквидистантная проекция",
        ["D3.js картографический движок", "Интерактивная небесная сфера", "Реальные астрономические данные"],
        "test_overlay_card.png"
    )
    print("Overlay created:", p)
