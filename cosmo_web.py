import aiohttp
import asyncio
import json


async def send_post_request():
    # 요청에 필요한 URL
    url = "https://try.playwright.tech/service/control/run"

    # 실행할 JavaScript 코드를 포함한 데이터
    data = {
        "code": """// @ts-check
const playwright = require('playwright');

(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // open login page
  await page.goto('https://shop.cosmo.fans/en/login/landing');

  // click to trigger recaptcha
  await page.getByRole('button', { name: "Continue with Cosmo app" }).click();

  // Wait for the specific network response from the ticket endpoint
  const response = await page.waitForResponse(response => 
    response.url().includes('https://shop.cosmo.fans/bff/v1/users/auth/login/native/qr/ticket')
  );

  // Log the response body
  const responseBody = await response.text();
  console.log('Response from ticket endpoint:', responseBody);

  // Now take a screenshot
  //await page.screenshot({ path: 'screenshot.png' });

  await browser.close();
})();
""",
        "language": "javascript",
        "token": """0.BO6aS2Ld4maJh0b5TlzFuQypfhnbEaPTJ0xe2od9Hcc8kgEzHtLJ9aoGscOubpTIMJ932NNLBrgyHc3Aw1qVZrpXi0friFZedBpRzsqbmyfFepR9OEaNd9mmQEiZ9BWcm3rCyQ_0Cjq_H4ssX_8E47qjYslYU7ZA6bFnUEbdlNz6BN3vD4POpCdJUYVFGJdzuSVRowhw3-StjccpbX_3_VDJ2jduKN5d5EHrldCXrXl82YL0PKcdJ7Y-M3iRRRtHrI3tmblgXS7hS_Ic5AKPe9W590xnjtdkxXadTBRadu5gw6YSq1BEA9ZhbJC58bKYdwy0AWSynUOSOmOBdu0iNO6EogpyGna-1OmXFrPXqVlhAR61yhk0BWvlMIDJEc8gHYDJkDdH9MiT53MZioCNapoS-1xaH37-4bO4BqxE9KHtJy_XpsmAEP-NCeypqImRjR3XRgxCBY_sUZmJTBPwYInQ65M5JM2fXBHpgT72IKa2nshamOkrdOOqaehEUhg0en03OMD3kA3co1krpdjr3F56rbxsFbJZMlo3oz9GWhfckNgvQDluqFDeCI_EdIjFhnrZbPcEbYf52m2PlzaU3mQeVQ3HCGxBBbEZX7PrmApPnfU-boa1es3zhOAl6VVz_iXaNW7WfWxozb81QytuyftHaszKA8GzWEU9oWdqQRPOMc-el6Qmfi--k5nHEH9O_bytt2orZSoQyWt7hkZ2525dKJdIyd52-uUNpZ27aejxF4OiWRZu9kO9c3erPmz1MYS78LxUA3vni27sj0NWQd5ISDTa3-LLh9Jlr87T4IsSc9Wid01OtBt_enj1Ix2gcgA8ggfr62P08HoFJpMSSw.unb8iGJ5OU0NJlqAkPvV3g.83c6ba81e2e536416b5b7dabdd13c571a01c21cbd7f08b651082dd388f1cc7f4"""
    }

    # 비동기 POST 요청 보내기
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_json = await response.json()
            print(response_json)
            # 'output'에서 필요한 부분만 추출
            output = response_json.get('output', '')
            # 출력이 'Response from ticket endpoint: {JSON}' 형태이므로, 콜론 뒤의 JSON 부분만 추출
            if 'Response from ticket endpoint:' in output:
                json_str = output.split('Response from ticket endpoint:')[1].strip()
                # JSON 문자열을 파싱하여 딕셔너리로 변환
                ticket_data = json.loads(json_str)
                return ticket_data
            else:
                return None


# 비동기 함수 실행하기
if __name__ == "__main__":
    result = asyncio.run(send_post_request())
    print(result)
