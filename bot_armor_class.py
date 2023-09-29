import re
import time

import requests
from bs4 import BeautifulSoup


def find_last_page_num(soup):
    last_page = 1
    li_tags = soup.find('ul', class_='pagination').find_all('li')
    for tag in li_tags:
        text = tag.get_text()
        if '>' in text:
            break
        a_tag = tag.find('a')
        if a_tag:
            last_page = a_tag['title'].split()[1]
    return last_page


def scraping_cards(cards, min_armor_class, max_armor_class, monster_data):
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
                if "Опасность" in text:
                    try:
                        danger_rate = re.search(r'\d+/\d+|\d+', text).group()
                    except AttributeError:
                        danger_rate = None

            if min_armor_class <= int(armor_class) <= max_armor_class:
                monster_data.append(
                    {'Название': title,
                     'URL': link,
                     'Класс Доспеха': armor_class,
                     'Опасность': danger_rate
                     }
                )
    return monster_data


def scrap_bestiary(url: str, min_armor_class: int, max_armor_class: int):
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/58.0.3029.110 Safari/537.36')
    }
    r = requests.get(url, headers=headers)
    initial_soup = BeautifulSoup(r.text, 'lxml')
    monster_data = []
    last_page = int(find_last_page_num(initial_soup))

    for page_num in range(1, last_page + 1):
        current_url = url + f'&page={page_num}'
        r = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.find_all('div', class_='card')
        monster_data.extend(scraping_cards(
            cards,
            min_armor_class,
            max_armor_class,
            monster_data
            )
        )
        print('Прочитана страница N', page_num)
        time.sleep(2)
    return monster_data
