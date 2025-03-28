import asyncio
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
from text_assist import *



# Month information
month_end = [31,28,31,30,31,30,31,31,30,31,30,31]
month_start = [4,7,7,3,5,1,3,6,2,    3,6,1] #2025, 2024


data_count = {29: 5, 11: 1, 23: 1, 7: 1, 5: 1, 6: 2, 12: 1, 16: 3, 26: 3, 27: 3, 15: 2, 17: 1, 19: 1, 20: 5, 8: 1, 9: 2, 22: 3, 25: 2, 3: 1, 30: 2, 1: 1}

colors = {
    0: ['#22262B', '#E7DDFF'], #꼬모수: [배경색, 글자색]
    1: ['#48464D', '#C7BFDB'],
    2: ['#706C7A', '#DBD2F1'],
    3: ['#9892A6', '#171C20'],
    4: ['#C0B8D3', '#292C33'],
    5: ['#E7DDFF', '#40424D'],
}

def generate_calendar_image(data_count):


    x = 7  # Number of columns (days in a week)
    y = 5  # Number of rows (weeks in a month)

    # Load the day mask image
    day_mask = Image.open('./calendar/day.png')
    base = Image.new('RGBA', (day_mask.size[0] * x, day_mask.size[1] * y), (0, 0, 0, 0))


    # Set timezone to Asia/Seoul
    korean_timezone = ZoneInfo('Asia/Seoul')
    now_korean = datetime.now(korean_timezone)
    current_month = now_korean.month
    month_current = current_month



    days_in_month = month_end[month_current - 1]

    # Adjust data_count for days beyond the current month's end
    total_to_add = 0
    for day in list(data_count.keys()):
        if day > days_in_month:
            total_to_add += data_count[day]
            del data_count[day]

    if total_to_add > 0:
        data_count[days_in_month] = data_count.get(days_in_month, 0) + total_to_add

    # Generate the calendar image
    for row in range(y):
        for col in range(x):
            day_count = col + x * row + 1 - month_start[month_current - 1] + 2
            if day_count <= 0 or day_count > days_in_month:
                continue

            count = data_count.get(day_count, 0)
            color = colors[min(count, 5)]

            rgb = hex2rgb(color[0])
            rgb_txt = hex2rgb(color[1])

            # Calculate the top-left corner of the day's box
            top_left = (col * day_mask.size[0], row * day_mask.size[1])
            day = Image.new('RGBA', day_mask.size, rgb)
            draw = ImageDraw.Draw(day)

            # Draw the day number
            text_draw_default(draw, (4, 0), 'HalvarBreit-XBd.ttf', 18, str(day_count), rgb_txt)

            # Paste the day image onto the base image
            base.paste(day, top_left, day_mask)

    return base

if __name__ == "__main__":
    generate_calendar_image(data_count).show()