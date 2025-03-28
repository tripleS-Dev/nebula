import cosmo
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp
import asyncio
from text_assist import *

# Main function to create the image
async def create_image(options, objekt_search_result, start_after, page, title='collect'):


    img = await process_images(objekt_search_result, start_after, title)
    draw = ImageDraw.Draw(img)

    # Draw user information
    draw_user_info(draw, options)

    # Draw total count
    draw_total(draw, objekt_search_result['total'])

    # Draw options text
    draw_options_text(draw, options)

    # Draw page number
    draw_page_number(draw, page)

    # Draw bottom info
    if options.get('gridable') and options.get('transferable'):
        transferable_gridable_image = Image.open('resource/transferable_gridable.png')
        img.paste(transferable_gridable_image, (48, 1849), transferable_gridable_image)
    elif options.get('gridable'):
        gridable_image = Image.open('resource/gridable.png')
        img.paste(gridable_image, (48, 1849), gridable_image)
    elif options.get('transferable'):
        transferable_image = Image.open('resource/transferable.png')
        img.paste(transferable_image, (48, 1849), transferable_image)

    #img.show()
    # Save image to BytesIO
    buffered_image = BytesIO()
    img.save(buffered_image, format="webp", subsampling=0, quality=100)
    buffered_image.seek(0)
    return buffered_image


# Function to draw user information
def draw_user_info(draw, options):
    font_nickname = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 45)
    font_discord = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 30)
    if options['cosmo_nickname']:
        draw.text((474, 29), options['cosmo_nickname'], (255, 255, 255), font=font_nickname)
    if options['discord_nickname']:
        draw.text((474, 75), options['discord_nickname'], (88, 101, 242), font=font_discord)

# Function to draw the total count
def draw_total(draw, total):
    font_total = ImageFont.truetype("font/HalvarBreit-XBd.ttf", 40)
    txt = str(total)
    txt_bbox = font_total.getbbox(txt)
    text_size = (txt_bbox[2] - txt_bbox[0], txt_bbox[3] - txt_bbox[1])
    draw.text((906 - text_size[0] / 2, 212 - text_size[1] / 2), txt, (231, 221, 255), font=font_total)

# Function to draw options text (artist, member, season, class)
def draw_options_text(draw, options):
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
        draw.text((x_pos, y_pos), txt, color, font=font)
        txt_bbox = font.getbbox(txt)
        text_width = txt_bbox[2] - txt_bbox[0]
        x_pos += text_width

# Function to draw page number
def draw_page_number(draw, page):
    font_page = ImageFont.truetype("font/inter.ttf", 40)
    font_page.set_variation_by_name('Black')
    txt = f'{page[0]} of {page[1]}'
    txt_bbox = font_page.getbbox(txt)
    text_width = txt_bbox[2] - txt_bbox[0]
    draw.text((1030 - text_width, 1841), txt, (255, 255, 255), font=font_page)

# Asynchronously download an image from a URL
async def download_image(session, url):
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
async def process_images(objekt_search_result, start_after, title):
    # Sort the 'objekts' list by 'receivedAt' in ascending order
    #sorted_objekts = sorted(objekt_search_result['objekts'], key=lambda x: parse_iso_date(x['receivedAt']))

    # Update the data with sorted objekts
    #objekt_search_result['objekts'] = sorted_objekts

    import json


    base_image = Image.open(f'resource/base_{title}.png')

    # Extract image data
    objekts = objekt_search_result['objekts'][start_after:start_after + 9]

    #print(len(objekt_search_result['objekts']))

    #image_urls = [objekt['thumbnailImage'] for objekt in objekts]

    image_urls = []
    image_colors = []
    image_names = []

    for objekt in objekts:
        url_raw = objekt['frontImage']
        last_slash_index = url_raw.rfind('/')
        # 마지막 '/'까지의 부분과 '2x'를 결합
        url = url_raw[:last_slash_index + 1] + '2x'

        image_urls.append(url)
        image_colors.append(objekt['textColor'])
        image_names.append(objekt['collectionNo'])

    print(image_colors, image_names)
    #image_colors = [objekt['textColor'] for objekt in objekts]
    #image_names = [objekt['collectionNo'] for objekt in objekts]

    # Download images asynchronously
    overlay_images = await download_images(image_urls)

    # Define positions for overlaying images
    positions = [
        (49, 292), (383, 292), (717, 292),
        (49, 798), (383, 798), (717, 798),
        (49, 1304), (383, 1304), (717, 1304)
    ]
    positions_text = [
        (534, 69-3), (1041, 69-3), (1548, 69-3),
        (534, 69+331), (1041, 69+331), (1548, 69+331),
        (534, 69+331+331+2), (1041, 69+331+331+2), (1548, 69+331+331+2)
    ]
    positions_text = [
        (534, 69+331+331+2), (534, 69+331), (534, 69-3),
        (1041, 69+331+331+2), (1041, 69+331), (1041, 69-3),
        (1548, 69+331+331+2), (1548, 69+331), (1548, 69-3)
    ]
    # Overlay each image onto the base image
    for i, (overlay_image, color, name) in enumerate(zip(overlay_images, image_colors, image_names)):
        overlay_image = overlay_image.resize((314, 486), Image.Resampling.LANCZOS)
        #rotated_text = draw_objekt_name(name, color)
        #overlay_image.paste(rotated_text, (290, 219), rotated_text)
        base_image.paste(overlay_image, positions[i], mask)

    base_image = base_image.rotate(90, expand=True)
    draw = ImageDraw.Draw(base_image)

    for i in range(len(image_names)):
        text_draw_center(draw, positions_text[i], 'spaceX.ttf', 24, image_names[i], image_colors[i])


    base_image = base_image.rotate(-90, expand=True)

    return base_image
# Function to parse the ISO 8601 date string
def parse_iso_date(date_str):
    from datetime import datetime
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
# Function to draw and rotate the objekt name
def draw_objekt_name(text, hex_color):
    font = ImageFont.truetype("font/spaceX.ttf", 18)
    text_bbox = font.getbbox(text)
    text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])

    # Create text image
    text_img = Image.new('RGBA', text_size, (255, 255, 255, 0))
    draw_text = ImageDraw.Draw(text_img)
    draw_text.text((0, 0), text, hex2rgb(hex_color), font=font)

    # Rotate text image
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

    objekt_search_result = asyncio.run(apollo.objekt_search_all('0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380', filters))

    asyncio.run(create_image(options, objekt_search_result, 0, (0, 10)))