import asyncio
from playwright.async_api import async_playwright

async def send_post_request():
    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 페이지 이동
        await page.goto('https://shop.cosmo.fans/en/login/landing')

        # response 이벤트 대기 설정(티켓 엔드포인트)
        # "response" 이벤트가 발생할 때마다 람다(r)로 필터링하며
        # 조건을 만족(r.url에 'qr/ticket' 포함)하면 해당 response를 잡아냄
        wait_for_ticket = page.wait_for_event(
            "response",
            lambda r: 'https://shop.cosmo.fans/bff/v1/users/auth/login/native/qr/ticket' in r.url
        )

        # 버튼 클릭 (reCAPTCHA 트리거)
        await page.get_by_role("button", name="Continue with Cosmo app").click()

        # 티켓 endpoint 응답을 기다렸다가 받음
        response = await wait_for_ticket
        response_body = await response.text()
        print("Response from ticket endpoint:", response_body)

        # 스크린샷(필요시 사용)
        # await page.screenshot(path="screenshot.png")

        await browser.close()
        import json
        data = json.loads(response_body)
        return data

if __name__ == "__main__":
    asyncio.run(send_post_request())
