import asyncio
import time
from playwright.async_api import async_playwright
import yt_dlp
import sqlite3

async def insert_all_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale='en-GB')
        url = 'https://www.youtube.com/@RichardJMurphy/videos'
        await page.goto(url)
        await page.get_by_role("button", name="Accept all").click()
        await page.wait_for_load_state()
        print(await page.title())

        link_count = 0
        while True:
            time.sleep(2)
            await page.evaluate("window.scrollBy(0, 30000)")
            linked = await page.locator("#video-title-link").count()
            print(linked)
            if linked <= link_count:
                break
            else:
                link_count = linked

        links = await page.locator("#video-title-link").all()

        data = []
        ydl_opts = {
            'extract_flat': True,  # Extract metadata without downloading
            'quiet': True,         # Suppress output
            'no_warnings': True,   # Suppress warnings
            'extract_info': True,  # Extract video info
            'cookiefile': '/workspaces/endi/cookies.txt',
            "sleep_interval": 30,         # Minimum wait time between downloads
            "max_sleep_interval": 60,     # Maximum wait time (randomized to look human)
            "ratelimit": 500000,  # Limit download speed to 500 KB/s
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        for i, link in enumerate(links):
            # title = await link.text_content()
            href = await link.get_attribute('href')
            info = ydl.extract_info(f"https://youtu.be/{href}", download=False)
            title = info.get('title')
            upload_date = info.get('upload_date')
            video_id = info.get('id')
            dic = {'title': title, 'video_id': video_id, 'upload_date': upload_date}
            print(dic)
            data.append(dic)
            time.sleep(1)
            if i > 10:
                break
        await browser.close()
    
    print(data)
    # for i, link in enumerate(links):
    #     if i < 2:
    #         print(await link.text_content())
    #         href = await link.get_attribute("href")
    #         print(href)
    #         with yt_dlp.YoutubeDL({'cookiefile': '/workspaces/endi/cookies.txt'}) as ydl:
    #             ydl.download([f"https://youtu.be/{href}"])
    #     else:
    #         break

    con = sqlite3.connect('videodb.db')
    cur = con.cursor()

    cur.executemany(
        """
        insert into videos (video_id, title) values(:href, :title)
        """,
        data
    )

    con.commit()
    con.close()

    return data

async def main():
    data = await get_new_links()
    insert_new_links(data)

async def get_new_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale='en-GB')
        url = 'https://www.youtube.com/@RichardJMurphy/videos'
        await page.goto(url)
        await page.get_by_role("button", name="Accept all").click()
        await page.wait_for_load_state()
        time.sleep(2)
        links = await page.locator("#video-title-link").all()

        data = []
        for link in links:
            title = await link.text_content()
            href = await link.get_attribute('href')
            data.append({'title': title, 'href': href})
        await browser.close()
    print(data)
    return data

def insert_new_links(data):
    con = sqlite3.connect('videodb.db')
    cur = con.cursor()

    cur.executemany(
            """
            insert into videos (video_id, title) values(:href, :title)
            on conflict (video_id) do nothing
            """,
            data
        )

    con.commit()
    con.close()


# asyncio.run(main())