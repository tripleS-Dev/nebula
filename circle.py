import matplotlib.pyplot as plt
import matplotlib

from config import season

matplotlib.use('Agg')
from PIL import Image
from io import BytesIO
from config import season_color

def generate(sizes: list):
    #colors = ['#f6dc4a', '#81fb4c', '#e9867c', '#a126f5'][::-1]  # 색상 설정
    colors = season_color[0:len(sizes)][::-1]  # 색상 설정

    # 도넛형 그래프 생성
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(
        sizes,
        colors=colors,
        wedgeprops=dict(width=0.24),
        startangle=90
    )

    # 그래프를 메모리(RAM) 내에 저장
    buffer = BytesIO()
    plt.savefig(buffer, format='PNG', transparent=True)
    buffer.seek(0)  # 버퍼의 시작 지점으로 이동

    # Pillow로 이미지 열기
    image = Image.open(buffer)
    resized_image = image.resize((364, 273), Image.Resampling.LANCZOS)


    return resized_image