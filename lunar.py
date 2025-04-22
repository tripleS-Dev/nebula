import os

import aiohttp
import asyncio
import translate
import difflib
from urllib.parse import quote
import aiohttp
import difflib
from typing import List, Tuple
from config import como_contract, objekt_contract





async def user_search_by_name(name: str, locale) -> Tuple[List[str], List[str]]:
    if len(name) < 4:
        if locale:
            return [str(translate.translate('Enter at least 4 characters', locale))], []
        else:
            return ['Enter at least 4 characters'], []

    url = f"https://lunar-cosmo.vercel.app/api/user/search?query={name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # 요청 성공
                result = await response.json()
                print("Response from API:", result)  # 디버그: API 응답 출력
                users = result.get("results", [])
                if users:
                    # 유사도 계산 및 정렬
                    # difflib의 SequenceMatcher를 사용하여 유사도 비율 계산
                    def similarity(nickname: str) -> float:
                        return difflib.SequenceMatcher(None, name.lower(), nickname.lower()).ratio()

                    # 사용자 리스트를 유사도에 따라 정렬 (높은 유사도 순)
                    sorted_users = sorted(users, key=lambda user: similarity(user.get('nickname', '')), reverse=True)

                    # 상위 25개 결과 추출
                    top_users = sorted_users[:25]

                    # 닉네임과 주소 리스트 생성
                    result_list = [user['nickname'] for user in top_users]
                    result_address = [user['address'] for user in top_users]
                    return result_list, result_address
                else:
                    return [str(translate.translate('No user', locale))], []
            else:  # 요청 실패
                error_text = await response.text()
                print(f"Failed request: Status {response.status}, Response: {error_text}")  # 디버그: 에러 출력
                return [str(translate.translate('User not found', locale))], []
