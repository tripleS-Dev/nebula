from PIL import Image, ImageDraw, ImageFont, ImageFilter

#import nova

mask = Image.open('gravity_panel2/mask1.png')
island = Image.open('gravity_panel/island.png')
mask2 = Image.open('test/mask2.png')
outline = Image.open('gravity_panel2/outline.png')
como_logo = Image.open('gravity_panel2/como_logo.png')
from text_assist import text_draw_default, text_draw_center, text_draw_right

import asyncio
import aiohttp
import io
async def download_and_open_image(session: aiohttp.ClientSession, url: str) -> Image.Image:
    """
    주어진 URL에서 이미지를 비동기로 다운로드하고 PIL.Image 객체로 반환합니다.

    :param session: aiohttp.ClientSession 객체
    :param url: 이미지의 URL
    :return: PIL.Image 객체
    """
    try:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"이미지 다운로드 실패: 상태 코드 {response.status}")
            image_bytes = await response.read()
            image = Image.open(io.BytesIO(image_bytes))
            return image
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def getPollid(user_votes, gravity_info, i):
    poll_id = int(user_votes[i]['node']['poll'])
    # 빠른 조회를 위한 매핑 생성
    gravity_info_dict = {int(info['polls'][0]['pollIdOnChain']): info for info in gravity_info}

    # 매칭되는 gravity_info 아이템 가져오기
    gravity_item = gravity_info_dict.get(poll_id)
    return gravity_item, poll_id


def main(user_votes, gravity_info, artist):
    base = Image.open('gravity_panel2/base.png')


    ongoing = False

    gravity_info_ongoing = gravity_info['ongoing']
    gravity_info = gravity_info['past']
    if not user_votes:
        return


    for i in range(len(user_votes)):
        gravity_item, poll_id = getPollid(user_votes, gravity_info, i)
        if not gravity_item:
            return
        if gravity_item['artist'].lower() == artist.lower():
            break




    gravity_title = gravity_item['title']
    gravity_banner = gravity_item['bannerImageUrl']

    # 제목을 두 부분으로 분할
    words = gravity_title.split()
    midpoint = len(words) // 2
    title_parts = [' '.join(words[:midpoint]), ' '.join(words[midpoint:])]

    async def fetch_data():
        async with aiohttp.ClientSession() as session:
            # 배너 이미지 다운로드와 gravity_poll 데이터 fetch를 병렬로 실행
            banner_task = asyncio.create_task(download_and_open_image(session, gravity_banner))
            gravity_poll_task = asyncio.create_task(nova.get_gravity_poll(
                gravity_item['polls'][0]['id'],
                artist=gravity_item['polls'][0]['artist']
            ))

            # 배너 이미지와 gravity_poll 데이터 동시 가져오기
            banner_image, gravity_poll = await asyncio.gather(banner_task, gravity_poll_task)
            return banner_image, gravity_poll

    # 이벤트 루프 실행하여 비동기 함수 호출
    banner_image, gravity_poll = asyncio.run(fetch_data())

    # 사용자 투표 중 해당 poll ID와 매칭되는 것 필터링
    matching_votes = [vote for vote in user_votes if int(vote['node']['poll']) == poll_id]
    print(matching_votes)
    count = len(matching_votes)
    print(f"The poll {poll_id} appears {count} times.")

    selected_content = gravity_poll[0]['pollViewMetadata']['selectedContent']

    # 배너 이미지 처리
    resized_image = banner_image.resize(mask.size, Image.Resampling.LANCZOS)
    base.paste(resized_image, (0, 0), mask)
    draw = ImageDraw.Draw(base)

    # 이미지 URL과 금액 수집
    tasks = {}
    for i in range(count):
        vote = matching_votes[count - 1 - i]  # 역순으로 처리
        candidate = vote['node']['candidate']
        if not ongoing:
            selected_option = selected_content[candidate]['content']['title']
        else:
            selected_option = 'Unknown'
        amount = vote['node']['amount'][:-18]
        amount = int(amount)  # 필요에 따라 float로 변환

        # 각 selected_option에 금액 누적
        if selected_option in tasks:
            tasks[selected_option] += amount
        else:
            tasks[selected_option] = amount

    print(tasks)

    # 금액 기준으로 내림차순 정렬
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1], reverse=True)

    # 상위 2개의 selected_option 가져오기
    top_two = sorted_tasks[:2]

    i = 0
    # 이름 추출 및 출력
    for option, amount in top_two:
        text_draw_default(draw, (20, 286 + i * 73), 'inter.ttf', 26, option, variation='Black Italic')
        text_draw_right(draw, (235, 286 + i * 71), 'inter.ttf', 28, str(amount), variation='ExtraBold')
        base.paste(como_logo, (236, 293 + i * 72), como_logo)

        if not ongoing:
            for k in range(len(gravity_item['polls'][0]['result']['voteResults'])):
                if gravity_item['polls'][0]['result']['voteResults'][k]['votedChoice']['choiceName'] == option:
                    comoUsed = gravity_item['polls'][0]['result']['voteResults'][k]['votedChoice']['comoUsed']
                    effort = (amount / comoUsed) * 100
                    text_draw_right(draw, (270, 300 + 23 + i * 72), 'inter.ttf', 16, f"Effort: {effort:.3f}%", variation='ExtraBold')
                    text_draw_default(draw, (20, 300 + 23 + i * 72), 'inter.ttf', 16, f"Total: {comoUsed}", variation='ExtraBold')
        else:
            text_draw_right(draw, (270, 300 + 23 + i * 72), 'inter.ttf', 16, f"Effort: Unknown %", variation='ExtraBold')
            text_draw_center(draw, (145, 300 + 23 + 1 * 72), 'inter.ttf', 16, "Ongoing gravity is private")
        i += 1

    base.paste(outline, (0, 0), outline)
    return base

if __name__ == "__main__":
    async def fetch_gravity_info():
        try:
            return await nova.get_gravity_info()
        except Exception as e:
            print(f"Error fetching gravity info: {e}")
            return None

    async def fetch_user_votes(cosmo_address):
        try:
            return await nova.fetch_votes(cosmo_address)
        except Exception as e:
            print(f"Error fetching user votes: {e}")
            return None

    address = '0xAdB74B3aD794fFbA171bB8accbC15FC95a278c01'
    address = '0xe87d5FbFd20323952383675e54673dAF9d97624a'
    address = 'c'
    artist = 'artms'
    maina = main(asyncio.run(fetch_user_votes(address)), asyncio.run(fetch_gravity_info()), artist)
    maina.show()