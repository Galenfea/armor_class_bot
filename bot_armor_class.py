import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

from monster_card import MonsterCard

SLEEP_TIME = 2
MAX_PAGES = 3000
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/91.0.4472.124 Safari/537.36'
              )


async def is_last_page(soup: BeautifulSoup) -> bool:
    try:
        li_tags = soup.find('ul', class_='pagination').find_all('li')
        for tag in li_tags:
            text = tag.get_text()
            if '>' in text:
                return False
    except AttributeError:
        return True
    return True


async def scraping_cards(cards, min_armor_class, max_armor_class) -> list:
    base_url = "https://dnd.su"
    monster_data = []
    if max_armor_class < min_armor_class:
        min_armor_class, max_armor_class = max_armor_class, min_armor_class
    for card in cards:
        # Находим и извлекаем название монстра и ссылку
        title_tag = card.find('h2', class_='card-title')
        # В этой части мы добавим проверку на то, что title не None,
        # прежде чем пытаться извлечь текст и href
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = base_url + title_tag.find('a')['href']
        else:
            title = "Нет заголовка"
            link = "Нет ссылки"

        # Находим и извлекаем класс доспеха
        params = card.find('ul', class_='params')

        if params:
            li_tags = params.find_all('li')
            for tag in li_tags:
                text = tag.get_text()
                if "Класс Доспеха" in text:
                    try:
                        armor_class = re.search(r'\d+', text).group()
                    except AttributeError:
                        armor_class = '-1'
                match = re.search(r'<strong>Опасность</strong>', str(tag))
                if match:
                    try:
                        danger_rate = re.search(r'\d+/\d+|\d+|—', text).group()
                    except AttributeError:
                        danger_rate = None

            if min_armor_class <= int(armor_class) <= max_armor_class:
                monster = MonsterCard(title, link, armor_class, danger_rate)
                monster_data.append(monster)
    return monster_data


async def scrap_bestiary(url: str, min_armor_class: int, max_armor_class: int):
    headers = {'User-Agent': USER_AGENT}
    async with aiohttp.ClientSession(headers=headers) as session:
        monsters_list = []
        page_num = 1
        last_page = False
        while not last_page and page_num <= MAX_PAGES:
            current_url = url + f'&page={page_num}'
            try:
                async with session.get(current_url) as r:
                    text = await r.text()
            except aiohttp.ClientError as e:
                print(f"Ошибка при запросе {current_url}: {e}")
                return []
            except aiohttp.ClientResponseError as e:
                print(f"Ошибка ответа сервера {current_url}: {e}")
                return []
            soup = BeautifulSoup(text, 'lxml')
            cards = soup.find_all('div', class_='card')
            monsters_list.extend(await scraping_cards(
                cards,
                min_armor_class,
                max_armor_class,
                )
            )
            print(' Прочитана страница N', page_num)
            last_page = await is_last_page(soup)
            page_num += 1
            await asyncio.sleep(SLEEP_TIME)
        monsters_list.sort(key=MonsterCard.sort_by_danger)
        return monsters_list
