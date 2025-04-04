import matplotlib.pyplot as plt
import matplotlib

from config import season

matplotlib.use('Agg')
from PIL import Image
from io import BytesIO
from config import season_color

def generate_colors(input_dict, season_color_dict):
    colors = []
    for key in input_dict:
        # 키에서 숫자를 제거 (예: Divine01 → Divine)
        cleaned_key = ''.join([i for i in key if not i.isdigit()])
        # 소문자로 변환하여 색상 찾기
        color_code = season_color_dict.get(cleaned_key.lower(), None)
        if color_code is None:
            raise KeyError(f"Key {key} does not match any season color")
        colors.append(color_code)
    return colors

size = {
    'Atom01': '0',
    'Binary01': '2',
    'Cream01': '3',
    'Divine01': '4',
    'Ever01': '5',
}

def generate(sizes):

    # 도넛형 그래프 생성
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(
        list(sizes.values())[::-1],
        colors=season_color[::-1],
        wedgeprops=dict(width=0.24),
        startangle=90
    )

    # 그래프를 메모리(RAM) 내에 저장
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', transparent=True)
    buffer.seek(0)  # 버퍼의 시작 지점으로 이동

    # Pillow로 이미지 열기
    image = Image.open(buffer)
    #image.show()
    resized_image = image.resize((364, 273), Image.Resampling.LANCZOS)


    return resized_image

if __name__ == "__main__":
    generate(size)