import matplotlib.pyplot as plt
import matplotlib

from config import season

matplotlib.use('Agg')
from PIL import Image
from io import BytesIO
from config import season_color_dict

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


def generate(sizes: dict):
    # 키의 첫 글자 기준 정렬 (키 전체 정렬도 첫 글자 기준이지만, 명시적으로 첫 글자 기준으로 정렬)
    sizes = dict(sorted(sizes.items(), key=lambda item: item[0][0]))
    print(f"!!!!!!!! {sizes}")
    #colors = ['#f6dc4a', '#81fb4c', '#e9867c', '#a126f5'][::-1]  # 색상 설정
    #colors = season_color[0:len(sizes)][::-1]  # 색상 설정

    colors = []
    colors = generate_colors(sizes, season_color_dict)

    print(colors)
    # 도넛형 그래프 생성
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(
        list(sizes.values())[::-1],
        colors=colors[::-1],
        wedgeprops=dict(width=0.24),
        startangle=90
    )

    # 그래프를 메모리(RAM) 내에 저장
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', transparent=True)
    buffer.seek(0)  # 버퍼의 시작 지점으로 이동

    # Pillow로 이미지 열기
    image = Image.open(buffer)
    image.show()
    resized_image = image.resize((364, 273), Image.Resampling.LANCZOS)


    return resized_image

if __name__ == "__main__":
    generate({'Divine01': 121, 'Cream01': 113, 'Ever01': 87, 'Binary01': 45, 'Atom01': 6})