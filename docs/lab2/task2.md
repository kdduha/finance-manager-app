# Ход работы

Сначала пишем отдельный парсер. Будем собирать посты на тему финансы с `https://vc.ru/money`.
Сайт подгружает в одну ленту все посты динамически => нужно имитировать прокрутку страницы, 
что делаем через `selenium`. Парсер выглядит так:

```python
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def fetch_vc_money_posts_selenium(desired_count=30, url="https://vc.ru/money"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

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
                    print(f"-- Post #{len(posts)+1} added")
                    posts.append({"title": title, "link": link})

        if len(posts) >= desired_count:
            break

    driver.quit()
    return posts[:desired_count]


if __name__ == "__main__":
    data = fetch_vc_money_posts_selenium(desired_count=400)

    with open("vc_money_posts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} posts to vc_money_posts.json")
```

Сначала мы собираем все ссылки на все посты N штук (в примере 400 ссылок), заносим все в json, 
который считываем в каждом отдельном эксперименте и пробуем парсить везде каждый пост отдельно

## Процессы

```python
import json
import time
import math
import multiprocessing as mp
import requests
from bs4 import BeautifulSoup


def fetch_post_details(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    result = {"link": url, "title": None, "text": None}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
        return result

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)
    return result


def worker_chunk(chunk):
    return [fetch_post_details(item["link"]) for item in chunk]


if __name__ == "__main__":
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    cpu_count = mp.cpu_count()
    total = len(posts)

    chunk_size = math.ceil(total / cpu_count)
    chunks = [posts[i:i + chunk_size] for i in range(0, total, chunk_size)]

    start_time = time.time()
    with mp.Pool(processes=cpu_count) as pool:
        results_per_chunk = pool.map(worker_chunk, chunks)

    elapsed = time.time() - start_time
    detailed_posts = [item for sublist in results_per_chunk for item in sublist]

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": cpu_count
        },
        "posts": detailed_posts
    }

    with open("processes.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed, 2)}s "
          f"using {cpu_count} processes")
```

## Потоки 

```python
import json
import threading
import time
import requests
from bs4 import BeautifulSoup


def fetch_post_details(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    result = {"link": url, "title": None, "text": None}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
        return result

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)

    return result


def worker(idx: int, total: int, url: str, output: list, lock: threading.Lock):
    print(f"[{idx}/{total}] Fetching: {url}")
    details = fetch_post_details(url)
    with lock:
        output.append(details)


if __name__ == "__main__":
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    detailed_posts = []
    lock = threading.Lock()
    threads = []

    total = len(posts)
    start_time = time.time()

    for idx, post in enumerate(posts, start=1):
        url = post.get("link")
        t = threading.Thread(
            target=worker,
            args=(idx, total, url, detailed_posts, lock),
            daemon=True
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    batch_count = len(threads)

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": batch_count
        },
        "posts": detailed_posts
    }

    with open("threads.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed,2)}s using {batch_count} threads")
```

## Корутины

```python
import json
import asyncio
import time
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup

MAX_CONCURRENT = 500


async def fetch_post_details(session: ClientSession, url: str) -> dict:
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
        result["error"] = f"Request failed: {e}"
        return result

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)
    return result


async def bound_fetch(semaphore, session, idx, total, url, output):
    async with semaphore:
        print(f"[{idx}/{total}] Fetching: {url}")
        details = await fetch_post_details(session, url)
        output.append(details)


async def main():
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    total = len(posts)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    detailed_posts = []
    timeout = ClientTimeout(total=60)

    start = time.monotonic()
    async with ClientSession(timeout=timeout) as session:
        tasks = []
        for idx, post in enumerate(posts, start=1):
            url = post.get("link")
            tasks.append(
                asyncio.create_task(
                    bound_fetch(semaphore, session, idx, total, url, detailed_posts)
                )
            )
        await asyncio.gather(*tasks)
    elapsed = time.monotonic() - start

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": total
        },
        "posts": detailed_posts
    }
    with open("coroutines.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed,2)}s using concurrency={MAX_CONCURRENT}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Итого 

| Метод      | Время выполнения (с) | Батчи |
|------------|-----------------------|-------|
| Корутин   | 1.4                   | 400   |
| Процессы   | 37.45                 | 8     |
| Потоки    | 1.71                  | 400   |

Корутины и потоки показали значительно более быстрое время парсинга, чем процессы, с результатами 1.4 и 1.71 секунды соответственно. 
Процессы оказались наименее эффективными, занимая 37.45 секунды при малом количестве пакетов.
В целом, убеждаемся, что I/O-bound задачи лучше решать через потоки/корутины нежели через процессы.

Например, можно использовать существующие механизмы так:
- потоке предпочтительнее для работы с данными на input/output ожидание
- корутины для сетевых запросов
- процессы для параллельности вычислений 
