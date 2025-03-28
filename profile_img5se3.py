import asyncio
import time
from config import season_color
from io import BytesIO
from typing import Optional, Union

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from collections import Counter
import concurrent.futures


import alchemy
import calendar_panel
from config import season, season_names
from text_assist import text_draw_default,  text_draw_center, text_draw_right
from datetime import datetime, timedelta, timezone

import activity2
import apollo
#import cosmo
import circle
#import nova
#import gravity_panel3



member_color = {
    "seoyeon": (34, 174, 255),
    "hyerin": (146, 0, 255),
    "jiwoo": (255, 248, 0),
    "chaeyeon": (152, 242, 29),
    "yooyeon": (219, 12, 116),
    "soomin": (252, 131, 164),
    "nakyoung": (103, 153, 160),
    "yubin": (255, 227, 226),
    "kaede": (255, 201, 53),
    "dahyun": (255, 154, 214),
    "kotone": (255, 222, 0),
    "yeonji": (89, 116, 255),
    "nien": (255, 149, 63),
    "sohyun": (18, 34, 181),
    "xinyu": (213, 19, 19),
    "mayu": (254, 142, 118),
    "lynn": (172, 98, 183),
    "joobin": (183, 245, 76),
    "hayeon": (82, 217, 187),
    "shion": (255, 66, 138),
    "chaewon": (199, 163, 224),
    "sullin": (123, 186, 141),
    "seoah": (207, 243, 255),
    "jiyeon": (255, 171, 98),
    "heejin": (237, 0, 144),
    'haseul': (0, 166, 82),
    'kimlip': (239, 24, 65),
    'jinsoul': (25, 36, 167),
    'choerry': (90, 43, 146),
    'none': (0,0,0)
}

como_receiver = {
        'triples': "0xc3E5ad11aE2F00c740E74B81f134426A3331D950",
        'artms': '0x8466e6E218F0fe438Ac8f403f684451D20E59Ee3',
    }
async def main(options, forDebug = False):
    # Load base images
    start = time.time()
    base = Image.open('resource/base_profile_temp2.png')
    month = Image.open('./res_profile/month.png')

    """toggle = Image.open(f"res_profile/toggle_{options['artist'].lower()}.png")
    base.paste(toggle, (1920 - 214 - int(toggle.size[0]), 40), toggle)"""

    toggle = Image.open(f"res_profile/toggle2_{options['artist'].lower()}.png")
    base.paste(toggle, (1350, 96), toggle)

    draw = ImageDraw.Draw(base)

    # Extract options
    cosmo_address = options['cosmo_address']
    artist = options['artist'].lower() if options['artist'] == 'ARTMS' else options['artist']
    print(artist)
    cosmo_nickname = options['cosmo_nickname']
    discord_nickname = options['discord_nickname']
    title_objekt_tokenId = options.get('title_objekt_tokenId', None)

    # Define data fetching functions
    async def fetch_objekt_data():
        try:
            return await apollo.objekt_search_all(cosmo_address, {'sort': 'oldest', 'artist': artist})
        except Exception as e:
            print(f"Error fetching objekt data: {e}")
            return None

    async def fetch_trade_data():
        try:
            return await apollo.search_trade_history(cosmo_address)
        except Exception as e:
            print(f"Error fetching trade data: {e}")
            return None

    """async def fetch_gravity_info():
        try:
            return await nova.get_gravity_info()
        except Exception as e:
            print(f"Error fetching gravity info: {e}")
            return None"""

    """async def fetch_user_votes():
        try:
            return await nova.fetch_votes(cosmo_address)
        except Exception as e:
            print(f"Error fetching user votes: {e}")
            return None"""

    async def fetch_como_count():
        try:
            return await alchemy.get_como(cosmo_address, artist)
        except Exception as e:
            print(f"Error fetching como count: {e}")
            return 0

    async def fetch_member_rank(objekt_data):
        try:
            return await member_percent(objekt_data)
        except Exception as e:
            print(f"Error fetching member rank: {e}")
            return {}

    async def fetch_most_common_season(objekt_data):
        try:
            return await get_most_common_season(objekt_data)
        except Exception as e:
            print(f"Error fetching most common season: {e}")
            return ""

    async def fetch_classes(objekt_data):
        try:
            return await get_each_class(objekt_data)
        except Exception as e:
            print(f"Error fetching classes: {e}")
            return {}

    """async def fetch_comos(cosmo_address, artist):
        try:
            return await nova.fetch_comos_data(cosmo_address, artist)
        except Exception as e:
            print(f"Error fetching classes: {e}")
            return {}"""

    # Fetch objekt_data first since other tasks depend on it
    objekt_data = await fetch_objekt_data()
    if not objekt_data:
        print("Failed to fetch objekt data.")
        return None

    objekts_special = []
    for objekt in objekt_data['objekts']:
        if objekt['class'] == 'Special':
            objekts_special.append(objekt)

    async def download_main_image():
        try:
            index = next(
                (i for i, obj in enumerate(objekt_data['objekts']) if obj['tokenId'] == title_objekt_tokenId),
                -1
            )
            image_url = (
                objekt_data['objekts'][index]['frontImage'].rsplit('/', 1)[0] + '/2x'
                if index >= 0 else
                objekt_data['objekts'][-1]['frontImage'].rsplit('/', 1)[0] + '/2x'
            )
            images = await download_images([image_url])
            return images[0] if images else None
        except Exception as e:
            print(f"Error downloading main image: {e}")
            return None



    # Fetch other data in parallel
    data_tasks = [
        fetch_trade_data(),
        #fetch_gravity_info(),
        #fetch_user_votes(),
        fetch_como_count(),
        fetch_member_rank(objekt_data),
        fetch_most_common_season(objekt_data),
        fetch_classes(objekt_data),
        #fetch_comos(options['cosmo_address'], options['artist']),
        download_main_image()
    ]

    #trade_data, gravity_info, user_votes, como_count, member_rank, most_common_season, classes, como_data, main_img = await asyncio.gather(*data_tasks)
    trade_data, como_count, member_rank, most_common_season, classes, main_img = await asyncio.gather(*data_tasks)

    missing_data = []

    if not trade_data:
        missing_data.append('trade_data')
    """if not gravity_info:
        missing_data.append('gravity_info')
    if not user_votes:
        missing_data.append('user_votes')"""

    if missing_data:
        print(f"Essential data missing: {', '.join(missing_data)}")


    cosmo_date = objekt_data['objekts'][0]['receivedAt'].split('T')[0]

    # Draw texts
    size = text_draw_default(draw, (434, 29), 'HalvarBreit-XBd.ttf', 45, cosmo_nickname or 'Error')
    cosmo_date_box = Image.open('resource/cosmo_date_box_mask.png')
    cosmo_date_box_draw = ImageDraw.Draw(cosmo_date_box)

    text_draw_center(cosmo_date_box_draw, (94, 12), 'HalvarBreit-Bd.ttf', 24, cosmo_date)
    base.paste(cosmo_date_box, (int(size[0] + 8) + 434, 37), cosmo_date_box)

    text_draw_default(draw, (434, 73), 'HalvarBreit-XBd.ttf', 30, discord_nickname, txt_color=(88, 101, 242))

    total_size = text_draw_right(draw, (638, 171), 'HalvarBreit-XBd.ttf', 40, str(objekt_data['total']), txt_color=(8, 9, 10))

    # Draw rounded rectangle
    draw.rounded_rectangle((649 - total_size[0] - 84, 172, 649, 217), radius=32, fill=(135, 86, 255), width=0)
    obj_round = Image.open('res_profile/obj_count_l.png')
    base.paste(obj_round, (649 - total_size[0] - 84, 172), obj_round)
    base.paste(ImageOps.mirror(obj_round), (650 - 28, 172), ImageOps.mirror(obj_round))
    text_draw_right(draw, (638, 171), 'HalvarBreit-XBd.ttf', 40, str(objekt_data['total']), txt_color=(8, 9, 10))

    card_icon = Image.open('res_profile/card_icon.png')
    base.paste(card_icon, (649 - total_size[0] - 72, 182), card_icon)

    # Define image creation functions
    def create_circle_img():
        try:
            season_percent_value = season_percent(objekt_data)
            return circle.generate(season_percent_value)
        except Exception as e:
            print(f"Error creating circle image: {e}")
            return None

    def create_activity_img():
        try:
            return activity2.activity(trade_data, cosmo_address, artist)
        except Exception as e:
            print(f"Error creating activity image: {e}")
            return None

    """def create_gravity_img():
        try:
            return gravity_panel3.main(user_votes, gravity_info, options['artist'])
        except Exception as e:
            print(f"Error creating gravity image: {e}")
            return None"""

    """def create_como_info_panel():
        try:
            total_amount = sum(
                int(entry.get("node", {}).get("amount", "0"))
                for entry in user_votes
                if entry.get("node", {}).get("contract") == como_receiver[artist.lower()].lower()
            )

            text_draw_default(draw, (1416, 233), 'HalvarBreit-Bd.ttf', 40, str(total_amount // 10**18), (231, 221, 255))
            text_draw_default(draw, (1416, 279), 'HalvarBreit-Bd.ttf', 40, str(int(como_count)+int(total_amount // 10**18)), (231, 221, 255))
            x, *_ = text_draw_center(draw, (1700, 262), 'HalvarBreit-Bd.ttf', 40, str(classes.get('Special', 0)), (231, 221, 255))
            base.paste(month, (int(1700+x/2), 270), month)
            return
        except Exception as e:
            print(f"Error creating COMO info panel: {e}")
            return None"""

    """def create_como_calender_panel():
        try:
            if como_data:
                # comosConnection의 totalCount 추출
                comos_total = como_data['comosConnection']['totalCount']
                print(f"Comos Total Count: {comos_total}")

                # objekts의 minted 추출 및 날짜 변환 후 출력
                objekts = como_data['objekts']
                print("Objekts Minted Dates:")
                numbers = []
                for obj in objekts:
                    minted_timestamp = obj['minted']
                    minted_date = convert_timestamp_to_date(minted_timestamp)
                    if minted_date is not None:
                        numbers.append(minted_date)
                # 빈 딕셔너리 생성
                counts = {}

                # 숫자 개수 세기
                for number in numbers:
                    if number in counts:
                        counts[number] += 1
                    else:
                        counts[number] = 1
                return calendar_panel.generate_calendar_image(counts)
            else:
                return None
        except Exception as e:
            print(f"Error creating COMO info panel: {e}")
            return None"""

    def create_como_calender_panel():
        try:

            #print(objekts)
            # objekts의 minted 추출 및 날짜 변환 후 출력
            #objekts = objekt_data['objekts']
            #print("Objekts Minted Dates:")
            numbers = []
            for obj in objekts_special:
                minted_timestamp = obj['mintedAt']
                #minted_date = convert_timestamp_to_date(minted_timestamp)
                minted_date = int(minted_timestamp.split('T')[0].split('-')[-1])
                if minted_date is not None:
                    numbers.append(minted_date)
            # 빈 딕셔너리 생성
            counts = {}

            # 숫자 개수 세기
            for number in numbers:
                if number in counts:
                    counts[number] += 1
                else:
                    counts[number] = 1
            return calendar_panel.generate_calendar_image(counts)

        except Exception as e:
            print(f"Error creating COMO info panel: {e}")
            return None

    def run_in_parallel():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 각 작업을 병렬로 실행
            future_activity_img = executor.submit(create_activity_img)
            future_circle_img = executor.submit(create_circle_img)
            como_calender_panel_img = executor.submit(create_como_calender_panel)
            #gravity_img = executor.submit(create_gravity_img)

            # 결과 가져오기
            activity_img_result = future_activity_img.result()
            circle_img_result = future_circle_img.result()
            como_calender_panel_img_result = como_calender_panel_img.result()
            #gravity_img_result = gravity_img.result()

        return activity_img_result, circle_img_result, como_calender_panel_img_result#, gravity_img_result

    #gravity_img.show()
    # 병렬 실행
    #activity_img, circle_img, como_calender_img, gravity_img = run_in_parallel()
    activity_img, circle_img, como_calender_img = run_in_parallel()

    # Paste images onto base
    if circle_img:
        base.paste(circle_img, (-25, 266), circle_img)

    if main_img:
        base.paste(main_img, (669, 172), main_img.convert('RGBA'))

    if activity_img:
        base.paste(activity_img, (49, 532), activity_img)

    """if gravity_img:
        base.paste(gravity_img, (1271, 642), gravity_img)"""

    if como_calender_img:
        base.paste(como_calender_img, (1291, 414), como_calender_img)

    #create_como_info_panel()

    # Draw additional texts and shapes
    if most_common_season:
        season_text = most_common_season[:-2]
        text_draw_center(draw, (162, 400), 'inter.ttf', 32, season_text, txt_color=char_to_num(season_text[0]), variation='Black')

    if member_rank:
        entries = [
            {'percent_pos': (494, 269), 'percent_key': 'first_percent', 'rank_pos': (383, 370), 'rank_key': 'first'},
            {'percent_pos': (554, 269), 'percent_key': 'second_percent', 'rank_pos': (383, 420), 'rank_key': 'second'},
            {'percent_pos': (611, 269), 'percent_key': 'third_percent', 'rank_pos': (383, 465), 'rank_key': 'third'}
        ]

        for entry in entries:
            percent_text = str(member_rank.get(entry['percent_key'], '0')).split('.')[0]
            text_draw_center(draw, entry['percent_pos'], 'inter.ttf', 20, percent_text, txt_color='#bfc0c1', variation='Black')

            rank_member = member_rank.get(entry['rank_key'], 'None')
            if rank_member != 'None':
                txt_color = member_color.get(rank_member.lower(), (0, 0, 0))
                text_draw_center(draw, entry['rank_pos'], 'HalvarBreit-XBd.ttf', 40 if len(rank_member) <= 6 else 44 - len(rank_member), rank_member, txt_color=txt_color)

        for i, rank_label in enumerate(['first', 'second', 'third']):
            x_offset = 58 * i
            draw_member(rank_label, x_offset, base, member_rank, draw)

    # Draw COMO count and icon
    x, *_ = text_draw_default(draw, (1344, 172), 'HalvarBreit-XBd.ttf', 40, str(como_count), (23, 8, 32))
    como_color = {'triples': (231, 221, 255), 'artms': (221, 237, 255)}
    draw.rounded_rectangle((1271, 173, 1271 + 64 + x + 20, 218), radius=32, fill=como_color[artist.lower()], width=0)
    obj_round = Image.open('res_profile/obj_count_l.png')
    obj_round_c = Image.new('RGBA', obj_round.size, como_color[artist.lower()])

    base.paste(obj_round_c, (1271, 173), obj_round)
    base.paste(obj_round_c, (1271 + 64 + x + 20 - 27, 173), ImageOps.mirror(obj_round))

    text_draw_default(draw, (1344, 172), 'HalvarBreit-XBd.ttf', 40, str(como_count), (23, 8, 32))
    como_icon = Image.open(f"res_profile/como_{artist.lower()}_icon.png")
    base.paste(como_icon, (1281, 182), como_icon)

    x, *_ = text_draw_default(draw, (1649, 263-11), 'HalvarBreit-Bd.ttf', 40, str(len(objekts_special)), (231, 221, 255))
    base.paste(month, (1649+x-2, 274), month)


    end = time.time()
    print(f"{end-start} long!!")

    if forDebug:
        base.show()
    # Save and return the final image
    buffered_image = BytesIO()
    base.save(buffered_image, format="png", subsampling=0, quality=100)
    buffered_image.seek(0)
    return buffered_image



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


def char_to_num(c):
    colors = season_color[ord(c.upper()) - ord('A')]  # 색상 설정

    return colors

def season_percent(data):
    # Count the occurrences of each season
    season_counts = Counter([objekt['season'] for objekt in data['objekts']])
    # 모든 시즌 리스트 정의
    all_seasons = season_names

    # Counter에 없는 시즌을 0으로 추가
    for season in all_seasons:
        if season not in season_counts:
            season_counts[season] = 0

    print(season_counts)
    # Sort the seasons based on the first letter in reverse order
    sorted_seasons = sorted(season_counts.keys(), key=lambda s: s[0], reverse=True)
    # Get the counts in that order
    counts_in_order = [season_counts[season] for season in sorted_seasons]
    print(counts_in_order)
    print(len(counts_in_order))
    return counts_in_order


async def member_percent(data):
    member_counts = Counter([objekt['member'] for objekt in data['objekts']])

    # Get the total number of members to calculate percentages
    total_members = sum(member_counts.values())

    # Sort members by count, get the top three
    top_three = member_counts.most_common(3)

    # If there are fewer than 3 members, fill with 'None' and 0 counts
    while len(top_three) < 3:
        top_three.append((None, 0))

    # Calculate the percentage for the top three members
    first, second, third = top_three
    first_percent = (first[1] / total_members) * 100 if total_members else 0
    second_percent = (second[1] / total_members) * 100 if total_members else 0
    third_percent = (third[1] / total_members) * 100 if total_members else 0

    # Prepare the result dictionary
    member_rank = {
        'first': first[0] if first[0] else 'None',
        'second': second[0] if second[0] else 'None',
        'third': third[0] if third[0] else 'None',
        'first_percent': first_percent,
        'second_percent': second_percent,
        'third_percent': third_percent,
    }
    return member_rank

# Define a function to handle drawing for each member
def draw_member(rank_label, x_offset, base, member_rank, draw):
    # Set the circle color
    circle_color = member_color[member_rank[rank_label].lower()]

    # Create a mask image
    mask = Image.new('L', base.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    # Calculate the vertical offset based on the percentage
    percent = member_rank[f'{rank_label}_percent']
    y_offset = percent * -1.94

    # Define bounding boxes for the pieslices
    bbox1 = [471 + x_offset, 448 + y_offset,
                 518 + x_offset, 496 + y_offset]
    bbox2 = [471 + x_offset, 472 - 24,
                 518 + x_offset, 472 + 24]

    # Draw the pieslices
    mask_draw.pieslice(bbox1, start=180, end=360, fill=255)
    mask_draw.pieslice(bbox2, start=0, end=180, fill=255)

    # Apply the blur filter
    blurred_mask = mask.filter(ImageFilter.GaussianBlur(radius=0.8))

    # Paste the colored shape onto the base image using the blurred mask
    base.paste(circle_color, mask=blurred_mask)

    # Draw the rectangle
    rect_top = 496 + y_offset - 24
    draw.rectangle([(471 + x_offset, rect_top), (518 + x_offset, 472)], fill=circle_color)

async def get_most_common_season(data):
    # Count the occurrences of each season
    season_counts = Counter([objekt['season'] for objekt in data['objekts']])
    # Find the season with the highest count
    most_common_season = season_counts.most_common(1)[0][0]
    return most_common_season

async def get_each_class(data):
    # Count the occurrences of each season
    season_counts = Counter([objekt['class'] for objekt in data['objekts']])
    # Find the season with the highest count

    return season_counts
def convert_timestamp_to_date(timestamp_str):
    """
    타임스탬프 문자열(밀리초 단위)을 한국 시간 기준 datetime 객체의 일(day)으로 변환합니다.
    예: "1703911523000" -> 29
    """
    try:
        # 문자열을 정수로 변환
        timestamp_ms = int(timestamp_str)
        # 밀리초를 초로 변환
        timestamp_sec = timestamp_ms / 1000
        # datetime 객체로 변환 (UTC 기준)
        date = datetime.fromtimestamp(timestamp_sec, timezone.utc)
        # 한국 시간대로 변환
        kst_date = date.astimezone(timezone(timedelta(hours=9)))
        # day를 정수로 반환
        return kst_date.day
    except Exception as e:
        print(f"Timestamp 변환 오류: {e}")
        return None  # 유효하지 않은 타임스탬프는 무시하거나 다른 방식으로 처리할 수 있습니다.

options = {
    'cosmo_nickname': 'ILoveYouyeon',
    'discord_nickname': 'hj_sss',
    'cosmo_address': '0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380',
    'artist': 'tripleS',
    'title_objekt_tokenId': None
}


if __name__ == "__main__":
    a = asyncio.run(main(options, True))

