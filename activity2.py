from PIL import Image, ImageDraw, ImageFont, ImageFilter
import apollo
from typing import Optional, Union
from text_assist import text_draw_default,  text_draw_center, text_draw_right

import asyncio


def activity(data, my_address, artist):
    # 거래 기록 데이터 가져오기

    # 기본 이미지와 바 이미지 불러오기
    base = Image.open('res_profile/activity_base2.png')
    bar = Image.open('res_profile/activity_bar.png')
    draw = ImageDraw.Draw(base)

    # 초기 y 위치 설정
    y_pos = 408
    current_nickname = None
    previous_nickname = None
    one = False
    #print(current_nickname, previous_nickname)
    for i in range(len(data)):

        if not data[i]['collection']['artist'].lower() == artist.lower():
            continue


        # 닉네임 설정
        if data[i]['transfer']['from'] == '0x0000000000000000000000000000000000000000':
            current_nickname = 'MODHAUS'
        else:
            current_nickname = data[i].get('nickname', 'Error')
        if one == False:
            previous_nickname = current_nickname
            one = True
        #print(current_nickname, previous_nickname)




        # 닉네임이 변경되었는지 확인
        if current_nickname != previous_nickname:
            #print('bar')
            # 바 이미지 붙여넣기
            base.paste(bar, (-8, y_pos), bar)

            # 닉네임 그리기
            if previous_nickname == 'MODHAUS':
                text_draw_default(
                    draw,
                    (20, y_pos + 33),
                    'BMjapan.TTF',
                    27,
                    previous_nickname,
                    (255, 255, 255)
                )
            else:
                text_draw_default(
                    draw,
                    (20, y_pos + 26),
                    'HalvarBreit-Bd.ttf',
                    30,
                    previous_nickname,
                    (255, 255, 255)
                )

            # 날짜 텍스트 그리기
            date_text = data[i]['transfer']['timestamp'].split('T')[0].replace('-', '/')
            text_draw_center(
                draw,
                (523, y_pos + 41),
                'inter.ttf',
                17,
                date_text,
                (148, 153, 156),
                'Medium'
            )
            y_pos -= 60




        # 텍스트 색상과 강조 색상 설정
        txt_color = hex2rgb(data[i]['collection']['textColor'])
        accent_color = hex2rgb(data[i]['collection']['accentColor'])

        # 전송 여부 확인
        is_send = data[i]['transfer']['from'].lower() == my_address.lower()

        # 전송 또는 수신 마스크 이미지 선택
        box_mask_path = './res_profile/send_mask.png' if is_send else './res_profile/receive_mask.png'
        box_mask = Image.open(box_mask_path)

        # 색상 혼합 및 박스 이미지 생성
        outline_color = color_mix(txt_color, accent_color)
        box_main = Image.new('RGBA', box_mask.size, accent_color)
        draw_box_main = ImageDraw.Draw(box_main)

        # 멤버 이름 그리기
        x_pos_member = 10 if is_send else 14
        text_draw_default(
            draw_box_main,
            (x_pos_member, 4),
            'inter.ttf',
            39,
            data[i]['collection']['member'],
            txt_color,
            'SemiBold Italic'
        )

        # 시리얼 번호 크기 계산 및 그리기
        x_pos_serial = box_mask.size[0] - (14 if is_send else 10)
        serial_text = f"#{str(data[i]['serial']).zfill(5)}"
        serial_size = text_draw_right(
            draw_box_main,
            (x_pos_serial, 10),
            'MatrixSSK_custom.ttf',
            40,
            serial_text,
            txt_color
        )

        # 컬렉션 번호 그리기
        x_pos_collection_no = x_pos_serial - serial_size[0]
        text_draw_right(
            draw_box_main,
            (x_pos_collection_no, 4),
            'inter.ttf',
            39,
            data[i]['collection']['collectionNo'],
            txt_color,
            'Black'
        )

        # 메인 이미지에 박스 붙여넣기
        x_paste = 91 if is_send else 15
        base.paste(box_main, (x_paste, y_pos), box_mask)

        # 시간 텍스트 그리기
        time_text = data[i]['transfer']['timestamp'].split('T')[1][:-8]
        if is_send:
            text_draw_right(
                draw,
                (89, y_pos + 30),
                'inter.ttf',
                21,
                time_text,
                (81, 85, 88),
                'Regular'
            )
        else:
            text_draw_default(
                draw,
                (513, y_pos + 30),
                'inter.ttf',
                21,
                time_text,
                (81, 85, 88),
                'Regular'
            )

        # y 위치 업데이트
        y_pos -= 60



        # 이전 닉네임 업데이트
        previous_nickname = current_nickname

        # y 위치가 화면을 벗어나면 반복문 종료
        if y_pos < -14:
            break

    # 아웃라인 이미지 붙여넣기
    outline = Image.open('res_profile/outline.png')
    base.paste(outline, (0, 0), outline)

    # 결과 이미지 보여주기
    base.save('acct.png')
    return base


def hex2rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def color_mix(*args):
    color = [0, 0, 0]
    for arg in args:
        color = [color[0]+arg[0], color[1]+arg[1], color[2]+arg[2]]
    color = [color[0] / len(args), color[1] / len(args), color[2] / len(args)]
    for i in range(3):
        color[i] = int(color[i])
    return tuple(color)



if __name__ == "__main__":
    address = '0x9550260F8512eB592061eBE7632f38ab763A29d2'
    address = '0xe87d5FbFd20323952383675e54673dAF9d97624a'
    address = '0xaa5069Ff5185C1D549726b8521768aE36236e93B'
    address = '0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380'
    img = asyncio.run(activity(address, 'tripleS'))
