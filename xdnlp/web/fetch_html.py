from pyppeteer import launch
import asyncio
import aiofiles
import os
from xdnlp.web import url2domain, decode_image
from xdnlp.utils import default_logger
import aiohttp

headers_file = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
}


class Browser(object):

    def __init__(self, sem_value=10):
        self.args = ['--no-sandbox', '--ignore-certificate-errors', '--disable-gpu',
                     '--window-size=1920x1080']
        self.sem_value = sem_value
        self.browser = asyncio.get_event_loop().run_until_complete(self.get_browser())

    async def get_browser(self):
        return await launch({'args': self.args, 'ignoreHTTPSErrors': True})

    async def fetch_content(self, url, screenshot_path=None):
        domain = url2domain(url)
        page = await self.browser.newPage()
        await page.goto(url)
        content = await page.content()
        elements = await page.querySelectorAll('img')
        images = [await page.evaluate('(element) => element.src', ele) for ele in elements]
        title = await page.querySelector('title')
        title = await page.evaluate('(element) => element.textContent', title)
        if screenshot_path is not None:
            await page.screenshot(
                {'path': os.path.join(screenshot_path, domain, "screenshot.png"), 'fullPage': True})
        return content, title, images, domain

    async def fetch_save(self, url, output_dir="./", image=True, screenshot=True):
        try:
            async with asyncio.Semaphore(self.sem_value):
                page = await self.browser.newPage()
                await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
                await page.goto(url)
                domain = url2domain(url)
                content = await page.content()
                if not os.path.exists(os.path.join(output_dir, domain)):
                    os.makedirs(os.path.join(output_dir, domain))
                async with aiofiles.open(os.path.join(output_dir, domain, f"{url.split('/')[-1]}.html"), 'w',
                                         encoding='utf-8') as f:
                    await f.write(content)
                if image:
                    elements = await page.querySelectorAll('img')
                    images = [await page.evaluate('(element) => element.src', ele) for ele in elements]
                    async with asyncio.Semaphore(self.sem_value):
                        for idx, img in enumerate(images):
                            try:
                                if img.startswith("data:image"):
                                    async with aiofiles.open(os.path.join(output_dir, domain, f"{idx}.jpg"), 'wb') as f:
                                        await f.write(decode_image(img))
                                else:
                                    async with aiohttp.ClientSession(trust_env=True) as session:
                                        async with session.get(img, headers=headers_file,
                                                               timeout=aiohttp.ClientTimeout(total=4),
                                                               ssl=False) as resp:
                                            if resp.status == 200:
                                                image = await resp.read()
                                                async with aiofiles.open(os.path.join(output_dir, domain, f"{idx}.jpg"),
                                                                         'wb') as f:
                                                    await f.write(image)
                            except Exception as e:
                                default_logger.error(f"{domain}, IMG:{e},{img}")
                if screenshot:
                    await page.screenshot(
                        {'path': os.path.join(output_dir, domain, "screenshot.png"), 'fullPage': True})
                default_logger.info(url)
                del page
        except Exception as e:
            default_logger.error(f"{url}, BASE:{e}")

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(asyncio.wait(self.browser.close()))


if __name__ == '__main__':

    bs = Browser(sem_value=5)
    outdir = "/home/geb/PycharmProjects/task-serve/serving/data"
    data = []
    with open("/home/geb/datas/家庭下高危域名0728.txt", 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if os.path.exists(os.path.join(outdir, line, "0.jpg")):
                continue
            if not line.startswith("http"):
                line = "http://" + line
                data.append(line)
    total = len(data)
    print(total)
    tasks = [bs.fetch_save(url, output_dir=outdir, screenshot=False) for url in data]

    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

    # urls = []
    # while len(data) > 0:
    #     if len(urls) < 10:
    #         urls.append(data.pop())
    #     else:
    #
    #         tasks = [bs.fetch(url, output_dir=outdir, screenshot=False) for url in urls]
    #         print("剩余待爬:", len(data))
    #         asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    #         urls = []
    """
    76555.org:IMG:，https://76555.org/static/aqvns/img/pz.png
76555.org:IMG:，https://76555.org/static/aqvns/img/right.png
76555.org:IMG:，https://76555.org/static/aqvns/img/home/v0601_img/lottery-link.png
76555.org:IMG:，https://76555.org/static/aqvns/img/home/v0601_img/outline-square.png
76555.org:IMG:，https://76555.org/static/aqvns/img/home/v0601_img/girl5.png
    # """
    # async def tt(img):
    #     async with aiohttp.ClientSession(trust_env=True) as session:
    #         async with session.get(img, headers=headers_file,
    #                                timeout=aiohttp.ClientTimeout(total=3), ssl=False) as resp:
    #             if resp.status == 200:
    #                 image = await resp.read()
    #                 print(image)
    #
    # asyncio.get_event_loop().run_until_complete(tt("https://76555.org/static/aqvns/img/pz.png"))
