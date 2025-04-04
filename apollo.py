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


async def search_objekt_list(address: str, locale):

    url = f'https://apollo.cafe/api/objekt-list/for-user/{address}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200: # 요청 성공
                result = await response.json()
                print("Response from API:", result)  # Debug: Print the API response
                users = result.get("results", [])
                if users:
                    # Sorting the users based on nickname similarity
                    # Slicing the first 25 sorted nicknames
                    name_list = [user['name'] for user in users[:25]]
                    slug_list = [user['slug'] for user in users[:25]]
                    return name_list, slug_list
                return None, None
            else: # 요청 실패
                print(f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None, None

async def objekt_list_search_all(address, slug, filters):
    all_objekts = {}
    all_objekts['objekts'] = []
    has_next = True
    next_start_after = None

    # Remove any keys with None values from filters
    clean_filters = {k: v for k, v in filters.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        while has_next:
            url = f"https://apollo.cafe/api/objekt-list/entries/{slug}/{address}"
            params = clean_filters.copy()
            if next_start_after:
                params['start_after'] = next_start_after

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    all_objekts['total'] = int(data['total'])
                    all_objekts['objekts'].extend(data.get("objekts", []))
                    has_next = data.get("hasNext", False)
                    next_start_after = data.get("nextStartAfter")
                else:
                    response.raise_for_status()
    return all_objekts

async def objekt_list_search(address, slug, filters):
    # Remove any keys with None values from filters
    clean_filters = {k: v for k, v in filters.items() if v is not None}
    url = f"https://apollo.cafe/api/objekt-list/entries/{slug}/{address}"
    params = clean_filters.copy()

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                response.raise_for_status()

async def search_objekt_meta(info):
    url = f"https://apollo.cafe/api/objekts/metadata/{info['season'].lower()}-{info['member'].lower()}-{info['number']}{info['line'].lower()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200: # 요청 성공
                result = await response.json()
                return result
            else: # 요청 실패
                print(f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None

async def search_objekt_by_slug(info):
    url = f"https://apollo.cafe/api/objekts/by-slug/{info['season'].lower()}-{info['member'].lower()}-{info['number']}{info['line'].lower()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200: # 요청 성공
                result = await response.json()
                return result
            else: # 요청 실패
                print(f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None

async def search_trade_history(address: str):
    url = f"https://apollo.cafe/api/transfers/{address}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200: # 요청 성공
                result = await response.json()
                return result["results"]
            else: # 요청 실패
                print(f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None


async def user_search_by_name(name: str, locale) -> Tuple[List[str], List[str]]:
    if len(name) < 4:
        if locale:
            return [str(translate.translate('Enter at least 4 characters', locale))], []
        else:
            return ['Enter at least 4 characters'], []

    url = f"https://apollo.cafe/api/user/v1/search?query={name}"
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
            else:  # 요청 실패
                error_text = await response.text()
                print(f"Failed request: Status {response.status}, Response: {error_text}")  # 디버그: 에러 출력
                return [str(translate.translate('User not found', locale))], []



import aiohttp

# Your authorization token
apollo_api = os.getenv('apollo_api')
AUTH_TOKEN = apollo_api

async def user_search_byaddress(address: str):
    url = f'https://apollo.cafe/api/user/by-address/{address}'
    print("doit!!!")
    headers = {
        'Authorization': AUTH_TOKEN
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:  # Request successful
                result = await response.json()
                if not result:
                    return None
                print("Response from API:", result)  # Debug: Print the API response
                answer = result.get('result', {}).get('nickname')
                return answer
            else:  # Request failed
                error_text = await response.text()
                print(f"Failed request: Status {response.status}, Response: {error_text}")  # Debug: Print the error
                return None

async def user_search_byaddressssss(address: str):
    url = f'https://apollo.cafe/api/objekts/by-address/{address}'
    print("doit!!!")
    headers = {
        'Authorization': AUTH_TOKEN
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:  # Request successful
                result = await response.json()
                if not result:
                    return None
                print("Response from API:", result)  # Debug: Print the API response
                answer = result.get('result', {}).get('nickname')
                return answer
            else:  # Request failed
                error_text = await response.text()
                print(f"Failed request: Status {response.status}, Response: {error_text}")  # Debug: Print the error
                return None

async def objekt_search_all(address: str, options: dict):

    print(options)
    data = await objekt_search(address, options)
    hasNext = data['hasNext']
    print(data)
    nextStartAfter = data.get('nextStartAfter')

    while hasNext:
        options['page'] = nextStartAfter
        print(options)
        data_new = await objekt_search(address, options)
        print(data_new)
        data['objekts'].extend(data_new['objekts'])
        hasNext = data_new['hasNext']
        nextStartAfter = data_new.get('nextStartAfter')

    return data
"""async def objekt_search_new(address: str, options: dict):

    print(options)
    data = await objekt_search(address, options)
    total = data['total']
    if total / 60 == total // 60:
        count = total / 60
    else:
        count = (total // 60) + 1
    while hasNext:
        options['page'] = nextStartAfter
        print(options)
        data_new = await objekt_search(address, options)
        print(data_new)
        data['objekts'].extend(data_new['objekts'])
        hasNext = data_new['hasNext']
        nextStartAfter = data_new.get('nextStartAfter')

    return data"""
async def objekt_search(address: str, options: dict):

    base_url = f'https://apollo.cafe/api/objekts/by-address/{address}'

    # Create query parameters from options
    query_params = []
    for key, value in options.items():
        if value is not None:
            if value == 'ARTMS':
                value = 'artms'
            query_params.append(f"{key}={value}")

    # Join the parameters to form the query string
    query_string = "&".join(query_params)
    url = f"{base_url}?{query_string}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # Request successful
                result = await response.json()
                return result
            else:  # Request failed
                print(
                    f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None

async def stats(address: str):
    base_url = f'https://apollo.cafe/api/user/by-address/{address}/stats'

    url = f"{base_url}"
    headers = {
        'Authorization': AUTH_TOKEN
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:  # Request successful
                result = await response.json()
                return result
            else:  # Request failed
                print(
                    f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None

async def como(address: str, artist: str):
    base_url = f'https://apollo.cafe/api/user/by-address/{address}/como'

    url = f"{base_url}"
    headers = {
        'Authorization': AUTH_TOKEN
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:  # Request successful
                result = await response.json()

                new_dict = {}

                for i in result:
                    for k in range(len(list(result[i].keys()))):

                        if list(result[i].keys())[k] == objekt_contract[artist.lower()].lower():
                            new_dict[int(i)] = result[i][objekt_contract[artist.lower()].lower()]['count']

                return new_dict

            else:  # Request failed
                print(
                    f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None

"""if __name__ == "__main__":
    # Run the function and print results
    options = {
            "artist": 'tripleS',
            'cosmo_address': '0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380',
            'sort': 'newest',
            'size': '30'
        }
    filters = {k: str(v) for k, v in options.items() if v is not None}
    r = asyncio.run(user_search_by_name('iloveyouyeon',"ko_KR"))
    print(r[1][0])
    #print(len(r.get('objekts')))"""


if __name__ == "__main__":
    r = asyncio.run(como('0x1F38b8c3a5965704a6Ff6E9b750F771DD1C3C9D4', 'tripleS'))
    """ print(r)

    artist = 'artms'
    from config import season_percent_value

    for i in r:
        if not i['artistName'] == artist:
            pass
        else:
            for season in i['seasons']:
                season_percent_value[season['name']] = season['count']"""
    print(r)
    #print(sum(r.values()))







