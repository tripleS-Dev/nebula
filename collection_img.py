import cosmo
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp
import asyncio
from text_assist import *
import time

# Main function to create the image
async def create_image(options, objekt_search_result, start_after, page, objekt_per_page, title='collect'):
    total_start = time.time()
    print("Starting create_image...")

    # process_images 단계 측정
    start_proc_images = time.time()
    img = await process_images(objekt_search_result, start_after, objekt_per_page, title)
    print(f"process_images took {time.time() - start_proc_images:.2f} seconds")

    draw = ImageDraw.Draw(img)
    draw_user_info(draw, options, objekt_per_page)

    # offset 결정
    match objekt_per_page:
        case 9:
            offset = (0, 0)
        case 18:
            offset = (1002, -122)
        case _:
            offset = (0, 0)

    # total count 그리기
    start_total = time.time()
    draw_total(draw, objekt_search_result['total'], offset)
    print(f"draw_total took {time.time() - start_total:.2f} seconds")

    # 옵션 텍스트 그리기
    start_options = time.time()
    draw_options_text(draw, options, offset)
    print(f"draw_options_text took {time.time() - start_options:.2f} seconds")

    # 페이지 번호 그리기
    start_page_num = time.time()
    draw_page_number(draw, page, img.size)
    print(f"draw_page_number took {time.time() - start_page_num:.2f} seconds")

    # 하단 정보 그리기
    start_bottom = time.time()
    if options.get('gridable') and options.get('transferable'):
        transferable_gridable_image = Image.open('resource/transferable_gridable.png')
        img.paste(transferable_gridable_image, (48, 1849), transferable_gridable_image)
    elif options.get('gridable'):
        gridable_image = Image.open('resource/gridable.png')
        img.paste(gridable_image, (48, 1849), gridable_image)
    elif options.get('transferable'):
        transferable_image = Image.open('resource/transferable.png')
        img.paste(transferable_image, (48, 1849), transferable_image)
    print(f"Drawing bottom info took {time.time() - start_bottom:.2f} seconds")

    total_end = time.time()
    print(f"Total create_image time before: {total_end - total_start:.2f} seconds")

    # 이미지 저장
    buffered_image = BytesIO()
    #img.save(buffered_image, format="webp", subsampling=10, quality=90)
    img.convert('RGB').save(buffered_image, format="jpeg", subsampling=10, quality=90)
    #img.save(buffered_image, format="png", optimize=False)
    buffered_image.seek(0)

    total_end = time.time()
    print(f"Total create_image time: {total_end - total_start:.2f} seconds")
    return buffered_image

# Function to draw user information
def draw_user_info(draw, options, objekt_per_page):
    match objekt_per_page:
        case 9:
            pos = [(474, 29), (474, 75)]
        case 18:
            pos = [(494, 29), (494, 75)]
        case _:
            pos = [(474, 29), (474, 75)]

    font_nickname = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 45)
    font_discord = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 30)
    if options['cosmo_nickname']:
        draw.text(pos[0], options['cosmo_nickname'], (255, 255, 255), font=font_nickname)
    if options['discord_nickname']:
        draw.text(pos[1], options['discord_nickname'], (88, 101, 242), font=font_discord)

# Function to draw the total count
def draw_total(draw, total, offset):
    font_total = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 40)
    txt = str(total)
    txt_bbox = font_total.getbbox(txt)
    text_size = (txt_bbox[2] - txt_bbox[0], txt_bbox[3] - txt_bbox[1])
    draw.text(((906 - text_size[0] / 2) + offset[0], (212 - text_size[1] / 2) + offset[1]),
              txt, (231, 221, 255), font=font_total)

# Function to draw options text (artist, member, season, class)
def draw_options_text(draw, options, offset):
    x_pos = 145
    y_pos = 198
    text_color = (255, 255, 255)
    texts = []

    font_member = ImageFont.truetype("font/inter.ttf", 40)
    font_member.set_variation_by_name('ExtraBold')
    font_season = ImageFont.truetype("font/inter.ttf", 40)
    font_season.set_variation_by_name('Medium Italic')
    font_class = ImageFont.truetype("font/inter.ttf", 40)
    font_class.set_variation_by_name('Black Italic')

    # Build the texts to display
    if options.get('list_name'):
        texts.append((options['list_name'], font_class, text_color))
    else:
        if options.get('artist'):
            texts.append((options['artist'], font_member, text_color))
        elif options.get('member'):
            texts.append((options['member'], font_member, text_color))
        else:
            texts.append(('All', font_member, text_color))

        if options.get('season'):
            texts.append((" · ", font_member, text_color))
            texts.append((options['season'], font_season, (182, 182, 182)))

        if options.get('class'):
            texts.append((" · ", font_member, text_color))
            texts.append((options['class'], font_class, (148, 148, 148)))

    # Draw the texts sequentially
    for txt, font, color in texts:
        draw.text((x_pos + offset[0], y_pos + offset[1]), txt, color, font=font)
        txt_bbox = font.getbbox(txt)
        text_width = txt_bbox[2] - txt_bbox[0]
        x_pos += text_width

# Function to draw page number
def draw_page_number(draw, page, img_size):
    font_page = ImageFont.truetype("font/inter.ttf", 40)
    font_page.set_variation_by_name('Black')
    txt = f'{page[0]} of {page[1]}'
    txt_bbox = font_page.getbbox(txt)
    text_width = txt_bbox[2] - txt_bbox[0]
    text_height = txt_bbox[3] - txt_bbox[1]
    draw.text((img_size[0] - 48 - text_width, img_size[1] - 43 - text_height), txt, (255, 255, 255), font=font_page)

import os
import re


# Asynchronously download an image from a URL
async def download_image(session, url):
    # 파일이 이미 존재하는 경우 건너뜁니다.
    pattern = r'/([^/]+)/[^/]+$'
    match = re.search(pattern, url)
    if match:
        if os.path.exists(f"./image_resize/{match.group(1)}.png"):
            print(f"'{match.group(1)}' 파일이 ./image_resize 디렉토리에 존재합니다.")
            return Image.open(f"./image_resize/{match.group(1)}.png")

    async with session.get(url) as response:
        if response.status == 200:
            data = await response.read()
            return Image.open(BytesIO(data))
        else:
            raise Exception(f"Failed to download image: {url}")

# Asynchronously download multiple images
async def download_images(image_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in image_urls]
        return await asyncio.gather(*tasks)

mask = Image.open('resource/mask.png')

# Process images and overlay them onto the base image
async def process_images(objekt_search_result, start_after, objekt_per_page, title):
    proc_start = time.time()
    print("Starting process_images...")

    base_image = Image.open(f'resource/base_{title.lower()}_{objekt_per_page}.png')
    objekts = objekt_search_result['objekts'][start_after:start_after + objekt_per_page]

    image_urls = []
    image_colors = []
    image_names = []

    for objekt in objekts:
        url_raw = objekt['frontImage']
        last_slash_index = url_raw.rfind('/')
        url = url_raw[:last_slash_index + 1] + '2x'
        image_urls.append(url)
        image_colors.append(objekt['textColor'])
        image_names.append(objekt['collectionNo'])

    print("Image URLs:", image_urls)
    print("Image colors:", image_colors)
    print("Image names:", image_names)

    # 이미지 다운로드 측정
    start_download = time.time()
    overlay_images = await download_images(image_urls)
    print(f"Downloading images took {time.time() - start_download:.2f} seconds")

    positions9 = [
        (49, 292), (383, 292), (717, 292),
        (49, 798), (383, 798), (717, 798),
        (49, 1304), (383, 1304), (717, 1304)
    ]
    positions18 = [
        (49, 170), (383, 170), (717, 170), (1051, 170), (1385, 170), (1719, 170),
        (49, 676), (383, 676), (717, 676), (1051, 676), (1385, 676), (1719, 676),
        (49, 1182), (383, 1182), (717, 1182), (1051, 1182), (1385, 1182), (1719, 1182),
    ]
    position = {9: positions9, 18: positions18}

    # --- 비동기 리사이징 처리 ---
    async def resize_image(image):
        # 이미지 크기가 이미 (314, 486)인 경우, 건너뛰고 그대로 반환
        if image.size == (314, 486):
            return image
        # 그렇지 않은 경우, 비동기로 리사이징 처리
        return await asyncio.to_thread(image.resize, (314, 486), Image.Resampling.LANCZOS)

    start_resize = time.time()
    resized_images = await asyncio.gather(*[resize_image(img) for img in overlay_images])
    print(f"Resizing images took {time.time() - start_resize:.2f} seconds")
    # -----------------------------

    start_paste = time.time()
    for i, (overlay_image, color, name) in enumerate(zip(resized_images, image_colors, image_names)):
        base_image.paste(overlay_image, position[objekt_per_page][i], mask)
    print(f"Pasting images took {time.time() - start_paste:.2f} seconds")

    # 회전 및 후처리
    base_image = base_image.rotate(90, expand=True)
    draw = ImageDraw.Draw(base_image)

    positions_text9 = [
        (534, 733), (534, 400), (534, 66),
        (1041, 733), (1041, 400), (1041, 66),
        (1548, 733), (1548, 400), (1548, 66)
    ]
    positions_text18 = [
        (412, 1732+1+1+1+1+1), (412, 1399+1+1+1+1), (412, 1066+1+1+1), (412, 733+1+1), (412, 400+1), (412, 66),
        (919, 1732+1+1+1+1+1), (919, 1399+1+1+1+1), (919, 1066+1+1+1), (919, 733+1+1), (919, 400+1), (919, 66),
        (1426, 1732+1+1+1+1+1), (1426, 1399+1+1+1+1), (1426, 1066+1+1+1), (1426, 733+1+1), (1426, 400+1), (1426, 66)
    ]

    positions_text = {
        9: positions_text9,
        18: positions_text18
    }

    for i in range(len(image_names)):
        text_draw_center(draw, positions_text[objekt_per_page][i], 'spaceX.ttf', 24, image_names[i], image_colors[i])


    base_image = base_image.rotate(-90, expand=True)

    print(f"process_images total time: {time.time() - proc_start:.2f} seconds")
    return base_image

# Function to parse the ISO 8601 date string
def parse_iso_date(date_str):
    from datetime import datetime
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

# Function to draw and rotate the objekt name (현재 사용되지 않음)
def draw_objekt_name(text, hex_color):
    font = ImageFont.truetype("font/spaceX.ttf", 18)
    text_bbox = font.getbbox(text)
    text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

    text_img = Image.new('RGBA', text_size, (255, 255, 255, 0))
    draw_text = ImageDraw.Draw(text_img)
    draw_text.text((0, 0), text, hex2rgb(hex_color), font=font)

    rotated_text = text_img.rotate(-90, expand=True)
    return rotated_text

# Convert hex color to RGB tuple
def hex2rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

if __name__ == "__main__":
    import apollo

    options = {
        "artist": 'tripleS',
        'cosmo_address': '0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380',
        'cosmo_nickname': 'dsddsd',
        'discord_nickname': 'discord_nickname',
    }
    filters = {k: str(v) for k, v in options.items() if v is not None}

    objekt_search_result = asyncio.run(apollo.objekt_search('0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380', filters))
    asyncio.run(create_image(options, objekt_search_result, 0, (0, 10), 18))
