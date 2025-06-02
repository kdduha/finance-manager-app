import os
import time
import asyncio
from typing import List
from aiohttp import ClientSession, ClientTimeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from parser.schemas import Post, DetailedPost

MAX_CONCURRENT: int = 100


def fetch_vc_money_posts_selenium(desired_count=10, url="https://vc.ru/money") -> List[Post]:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if os.getenv("ENV") == "DOCKER":
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.get(url)

    SCROLL_PAUSE = 2
    posts_seen = set()
    posts = []

    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(posts) < desired_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for post in soup.find_all("div", class_="content content--short"):
            title_tag = post.find("div", class_="content-title")
            link_tag = post.find("a", class_="content__link")
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = "https://vc.ru" + link_tag["href"]
                if link not in posts_seen:
                    posts_seen.add(link)
                    posts.append(Post(title=title, link=link))

        if len(posts) >= desired_count:
            break

    driver.quit()
    return posts[:desired_count]


async def fetch_post_details(session: ClientSession, url: str) -> DetailedPost:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    result = {"link": url, "title": None, "text": None}
    try:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            html = await resp.text()
    except Exception as e:
        return DetailedPost(link=url, error=f"Request failed: {e}")

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)

    return DetailedPost(**result)


async def gather_details(posts: List[Post]) -> List[DetailedPost]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    detailed_posts = []
    timeout = ClientTimeout(total=60)

    async with ClientSession(timeout=timeout) as session:
        tasks = []
        for idx, post in enumerate(posts, start=1):
            tasks.append(bound_fetch(semaphore, session, idx, len(posts), post.link, detailed_posts))
        await asyncio.gather(*tasks)

    return detailed_posts


async def bound_fetch(semaphore, session, idx, total, url, output):
    async with semaphore:
        print(f"[{idx}/{total}] Fetching: {url}")
        details = await fetch_post_details(session, url)
        output.append(details)
