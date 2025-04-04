import asyncio

import aiohttp


async def objekt_search(address: str, options: dict):
    base_url = f'https://api.cosmo.fans/objekt/v1/owned-by/{address}'

    # Create query parameters from options
    query_params = []
    for key, value in options.items():
        if value is not None:
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


async def objekt_search_all(address, filters):
    all_objekts = {}
    all_objekts['objekts'] = []
    has_next = True
    next_start_after = None

    # Remove any keys with None values from filters
    clean_filters = {k: v for k, v in filters.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        while has_next:
            url = f"https://apollo.cafe/api/objekts/by-address/{address}"
            params = clean_filters.copy()
            if next_start_after:
                params['start_after'] = next_start_after

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    all_objekts['objekts'].extend(data.get("objekts", []))
                    has_next = data.get("hasNext", False)
                    next_start_after = data.get("nextStartAfter")
                else:
                    response.raise_for_status()

    all_objekts['total'] = len(all_objekts['objekts'])
    return all_objekts



async def getInfoBytokenId(tokenId):
    url = f'https://api.cosmo.fans/objekt/v1/token/{tokenId}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # Request successful
                result = await response.json()
                return result
            else:  # Request failed
                print(
                    f"Failed request: Status {response.status}, Response: {await response.text()}")  # Debug: Print the error
                return None
# Example options and locale
#filters = {"artist": None,"season": None,"sort": "newest","class": None,"member": None,"gridable": None,"transferable": None}

# Run the function and print results
#objekts = asyncio.run(objekt_search('0x0BeC30E1eB5496A235a09729f9CcfFE2FD72310D', filters))
#print(r['objekts'][0:9]['thumbnailImage'])
#image_names = [objekt['collectionNo'] for objekt in objekts['objekts'][0:61]]
#print(image_names)


if __name__ == '__main__':
    a = asyncio.run(getInfoBytokenId(1557328))
    print(a)