import asyncio

import activity2
import apollo
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from text_assist import text_draw_default, text_draw_center, text_draw_right



async def main(cosmo_user, cosmo_address, discord_nickname, artist_name):
    base = Image.open('activity/base.png')
    data = await apollo.search_trade_history(cosmo_address)
    img = activity2.activity(data, cosmo_address, artist_name)
    draw = ImageDraw.Draw(base)

    text_draw_default(draw, (297, 15), 'HalvarBreit-XBd.ttf', 32, cosmo_user)
    text_draw_default(draw, (297, 47), 'HalvarBreit-XBd.ttf', 24, discord_nickname, (88, 101, 242))

    base.paste(img, (49, 123), img)

    # Save and return the final image
    buffered_image = BytesIO()
    base.save(buffered_image, format="jpeg", subsampling=0, quality=100)
    buffered_image.seek(0)
    return buffered_image


if __name__ == "__main__":
    asyncio.run(main('dsdd','0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380', '121','tripleS'))