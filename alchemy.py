import os

import requests
import json
import asyncio
import aiohttp

como_contract = {
    'triples': "0x58AeABfE2D9780c1bFcB713Bf5598261b15dB6e5",
    'artms': '0x8254D8D2903B20187cBC4Dd833d49cECc219F32E',
}

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

como_contract = {
    'triples': "0x58AeABfE2D9780c1bFcB713Bf5598261b15dB6e5",
    'artms': '0x8254D8D2903B20187cBC4Dd833d49cECc219F32E',
}



async def get_total_tokens_sent(contract_name, from_address, to_address):
    contract_address = como_contract[contract_name].lower()
    from_address = from_address.lower()
    to_address = to_address.lower()

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




if __name__ == "__main__":
    # 사용 예시
    from_address = "0x9526E51ee3D9bA02Ef674eB1E41FB24Dc2165380"
    to_address = "0xc3E5ad11aE2F00c740E74B81f134426A3331D950"


    async def main():
        total_transferred = await get_total_tokens_sent('triples', from_address, to_address)
        print(f"총 전송된 토큰 수: {total_transferred}")


    # 비동기 함수 실행
    asyncio.run(main())


    a = asyncio.run(get_como('0xF5570fAa026789fC128A9bBD01679c013F7b012a', 'tripleS'))
    print(a)




