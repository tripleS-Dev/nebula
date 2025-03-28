from PIL import Image, ImageDraw, ImageFont, ImageFilter
from text_assist import text_draw_default,  text_draw_center, text_draw_right





def main(have, used, rank, monthly):
    base = Image.new('RGBA', (351, 470), (0, 0, 0, 0))

    draw = ImageDraw.Draw(base)
    text_draw_right(draw, (330, 149+62), 'Helvetica_Neue_LT_Std_75B.otf', 33, str(have))
    text_draw_right(draw, (330, 149+43+62), 'Helvetica_Neue_LT_Std_75B.otf', 33, str(rank))
    text_draw_right(draw, (330, 149+43+43+62), 'Helvetica_Neue_LT_Std_75B.otf', 33, str(used))
    text_draw_right(draw, (330, 149+43+43+43+62), 'Helvetica_Neue_LT_Std_75B.otf', 33, str(int(have)+int(used)))
    text_draw_right(draw, (330, 149+43+43+43+43+62), 'Helvetica_Neue_LT_Std_75B.otf', 33, str(monthly))
    #base.show()
    return base