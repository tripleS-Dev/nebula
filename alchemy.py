import os

import requests
import json
import asyncio
import aiohttp

from config import como_contract, objekt_contract, gravity_address

alchemy_api = os.getenv('alchemy_api')

url = f"https://polygon-mainnet.g.alchemy.com/v2/{alchemy_api}"



async def get_como(address, artist):
    artist = artist.lower()
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [address, "erc20"]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()

    token_balance_hex = None
    for token in data["result"]["tokenBalances"]:
        if token["contractAddress"].lower() == como_contract[artist].lower():
            token_balance_hex = token["tokenBalance"]
            break

    if token_balance_hex is not None:
        token_balance_decimal = int(token_balance_hex, 16)
        token_balance_decimal_adjusted = token_balance_decimal / (10 ** 18)
        return str(int(token_balance_decimal_adjusted))
    else:
        print(f"Contract address {como_contract[artist]} not found.")


from decimal import Decimal


async def get_total_tokens_sent(artist: str, from_address: str):
    contract_address = como_contract[artist.lower()].lower()
    from_address = from_address.lower()
    to_address = gravity_address[artist.lower()].lower()

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    total_amount = Decimal('0')
    page_key = None

    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "fromAddress": from_address,
                "toAddress": to_address,
                "contractAddresses": [contract_address],
                "category": ["erc20"],
                "excludeZeroValue": True,
                "withMetadata": False,
                "maxCount": "0x3e8"  # 한 번에 최대 1000개의 전송 내역 조회
            }
            if page_key:
                params['pageKey'] = page_key
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_getAssetTransfers",
                "params": [params]
            }
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()

            transfers = data.get('result', {}).get('transfers', [])
            for transfer in transfers:
                value_str = transfer['value']
                value_decimal = Decimal(value_str)
                total_amount += value_decimal

            page_key = data.get('result', {}).get('pageKey', None)
            if not page_key:
                break  # 더 이상의 페이지가 없으면 종료

    return total_amount



async def ownerByTokenId(artist: str, tokenId, address: str):
    if not tokenId:
        return False

    urls = url + "/getOwnersForToken"


    params = {
        "contractAddress": objekt_contract[artist.lower()],
        "tokenId": tokenId
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(urls, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print(f"\nToken ID {tokenId}의 소유자 목록:")
                for owner in data.get("owners", []):
                    print(owner)
                    if str(owner).lower() == address.lower():
                        return True
            else:
                print(f"오류 발생: {response.status} - {await response.text()}")
                return False
    return False

async def get_nft_metadata(artist: str, tokenId):
    urls = url + "/getNFTMetadata"

    params = {
        "contractAddress": objekt_contract[artist.lower()],
        "tokenId": tokenId
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(urls, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print(f"\nToken ID {tokenId}의 정보:")
                print(data)
            else:
                print(f"오류 발생: {response.status} - {await response.text()}")


if __name__ == "__main__":
    """# 사용 예시
    from_address = "0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380"
    to_address = "0xc3E5ad11aE2F00c740E74B81f134426A3331D950"


    async def main():
        total_transferred = await get_total_tokens_sent('triples', from_address, to_address)
        print(f"총 전송된 토큰 수: {total_transferred}")


    # 비동기 함수 실행
    asyncio.run(main())


    a = asyncio.run(get_como('0xF5570fAa026789fC128A9bBD01679c013F7b012a', 'tripleS'))
    print(a)"""


    a = asyncio.run(get_nft_metadata('tripleS', 8350493))





