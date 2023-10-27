import asyncio
import logging
import re
from logging.config import dictConfig
from typing import Any, Callable, List, Optional, Type, TypeVar, Tuple, Union

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag

from constantns import SCRAPER_SETTINGS, SCRAPER_CONSTANTS
from exceptions import EmptyDataError
from log_config import log_config
from monster_card import MonsterCard

dictConfig(log_config)
logger = logging.getLogger(__name__)

ExpectedType = TypeVar("ExpectedType")
ReturnType = TypeVar("ReturnType")


def safe_method_call(
    instance: Any,
    expected_type: Type[ExpectedType],
    method: Callable[[ExpectedType], ReturnType],
    *args,
    **kwargs,
) -> Optional[ReturnType]:
    if isinstance(instance, expected_type):
        return method(instance, *args, **kwargs)
    return None


def check_if_none(
    argument: Union[None, BeautifulSoup, str, Tag, List[Tag], List[str]],
    text: str = "",
) -> None:
    """
    Check if the given argument is None and raise an exception if it is.

    Args:
        argument (Union[None, BeautifulSoup, str, Tag, List[Tag], List[str]]):
        The argument to check.
        text (str, optional): The error message to log. Defaults to ''.

    Returns:
        None

    Raises:
        EmptyDataError: If the argument is None.
    """
    if argument is None:
        logger.error(text)
        raise EmptyDataError(text)


def is_last_page(soup: BeautifulSoup) -> bool:
    """
    Check if the given BeautifulSoup object represents the last page of a web
    scraping operation.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the web page.

    Returns:
        bool: True if it's the last page, False otherwise.
    """
    ul_tags_pagination = soup.find("ul", class_="pagination")
    logger.debug("There is ul tags in soup")
    if not ul_tags_pagination:
        logger.debug("There is only one page")
        return True
    li_tags = safe_method_call(ul_tags_pagination, Tag, Tag.find_all, "li")
    if not li_tags:
        logger.error("There is no li tags in pagination")
        raise EmptyDataError("There is no li tags in pagination")
    for tag in li_tags:
        text = tag.get_text()
        if SCRAPER_SETTINGS["NEXT_PAGE_INDICATOR"] in text:
            return False
    return True


def get_title(title_tag: Tag) -> str:
    """
    Extract the title text from the given BeautifulSoup tag.

    Args:
        title_tag (Tag): The BeautifulSoup tag containing the title.

    Returns:
        str: The extracted title as a string.

    Raises:
        EmptyDataError: If the title is None.
    """
    title = title_tag.get_text(strip=True) if title_tag else None
    check_if_none(title, "There is no title")
    return title  # type: ignore # Already checked by check_if_none()


def get_link(title_tag: Tag) -> str:
    """
    Extract the hyperlink from the given BeautifulSoup tag.

    Args:
        title_tag (Tag): The BeautifulSoup tag containing
        the hyperlink.

    Returns:
        str: The extracted hyperlink as a string.

    Raises:
        EmptyDataError: If the hyperlink is None.
    """
    suffix_link = title_tag.find("a")
    link: Optional[str] = None
    if (
        isinstance(suffix_link, Tag)
        and "href" in suffix_link.attrs
        and not isinstance(suffix_link["href"], list)
    ):
        link = suffix_link["href"]
    check_if_none(link, "There is no link")
    return link  # type: ignore [return-value] # Chekced by check_if_none()


def read_characteristic(
    tag: Tag, text: str, sample: str, pattern: str
) -> Optional[str]:
    """
    Extract specific information from the given BeautifulSoup tag
    based on a pattern.

    Args:
        tag (Tag): The BeautifulSoup tag to search in.
        text (str): The text to search.
        sample (str): The sample text to look for.
        pattern (str): The regex pattern to use for extraction.

    Returns:
        Optional[str]: The extracted information as a string or None.
    """
    characteristic: Optional[str] = None
    if tag.strong and tag.strong.string == sample:
        try:
            characteristic = re.search(pattern, text).group()  # type: ignore
        except (TypeError, AttributeError) as error:
            logger.warning(f"{sample}- {error}")
    return characteristic


def get_armor_class_and_danger(
    card: Tag,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract armor class and danger rate from a given card Tag.

    Search through the 'ul' tag with class 'params' in the BeautifulSoup object
    representing a monster card. Retrieve and log the armor class and danger
    rate for the monster.

    Args:
        card (Tag): BeautifulSoup object representing a monster card.

    Returns:
        Tuple[Optional[str], Optional[str]]: Armor class and danger rate for
        the monster, as strings or None if not found.

    Raises:
        EmptyDataError via check_if_none(): If 'ul' with class 'params' or 'li'
        tags within it are not found.
    """
    armor_class = None
    danger_rate = None
    params = card.find("ul", class_="params")
    check_if_none(params, "There is no ul tags with params class")
    li_tags = safe_method_call(params, Tag, Tag.find_all, "li")
    check_if_none(li_tags, "There is no li tags in ul tag with params class")
    for tag in li_tags:  # type: ignore [union-attr] # Checked by check_if_none
        text = tag.get_text()
        armor_class = read_characteristic(
            tag,
            text,
            SCRAPER_CONSTANTS["ARMOR_CLASS"],
            SCRAPER_CONSTANTS["ARMOR_PATTERN"],
        )
        danger_rate = read_characteristic(
            tag,
            text,
            SCRAPER_CONSTANTS["DANGER"],
            SCRAPER_CONSTANTS["DANGER_PATTERN"],
        )
    logger.debug(f"armor class = {armor_class}, danger = {danger_rate}")
    return armor_class, danger_rate


def add_monster_in_list(
    monster_data: List[MonsterCard],
    min_armor_class: int,
    max_armor_class: int,
    title: str,
    link: str,
    armor_class: Optional[str],
    danger_rate: Optional[str],
) -> None:
    """
    Add a MonsterCard object to the given list based on armor class criteria.

    Args:
        monster_data (List[MonsterCard]): The list to add the MonsterCard to.
        min_armor_class (int): The minimum armor class.
        max_armor_class (int): The maximum armor class.
        title (str): The title of the monster.
        link (str): The hyperlink to the monster's details.
        armor_class (str): The armor class of the monster as a string.
        danger_rate (str): The danger rate of the monster.

    Returns:
        None

    Raises:
        ValueError, TypeError: If the armor_class string cannot be converted
        to an integer.
    """
    try:
        armor_class_int = int(armor_class)  # type: ignore [arg-type] # in try
    except (ValueError, TypeError) as error:
        logger.error(f"Armor class can't be int - {error}")
        return
    if min_armor_class <= armor_class_int <= max_armor_class:
        monster = MonsterCard(title, link, armor_class_int, danger_rate)
        monster_data.append(monster)


def scrape_cards(
    cards: ResultSet, min_armor_class: int, max_armor_class: int
) -> List[MonsterCard]:
    """
    Scrape monster cards based on specified armor class criteria.

    Args:
        cards: ResultSet of BeautifulSoup objects representing monster cards.
        min_armor_class (int): Minimum armor class.
        max_armor_class (int): Maximum armor class.

    Returns:
        List[MonsterCard]: List of MonsterCard objects that meet the armor
        class criteria.
    """
    monster_data: List[MonsterCard] = []
    if max_armor_class < min_armor_class:
        min_armor_class, max_armor_class = max_armor_class, min_armor_class
    for card in cards:
        try:
            title_tag = card.find("h2", class_="card-title")
            check_if_none(title_tag, "title_tag is empty")
            title = get_title(title_tag)
            link = get_link(title_tag)
            armor_class, danger_rate = get_armor_class_and_danger(card)
            add_monster_in_list(
                monster_data,
                min_armor_class,
                max_armor_class,
                title,
                link,
                armor_class,
                danger_rate,
            )
        except EmptyDataError as error:
            logger.error(error, stack_info=True, stacklevel=2)
    return monster_data


async def get_soup(
    session: aiohttp.ClientSession, current_url: str
) -> Optional[BeautifulSoup]:
    """
    Fetch and parse the HTML content from a given URL using an aiohttp session.

    Perform an asynchronous HTTP GET request to fetch the HTML content of the
    specified URL. Parse the HTML content into a BeautifulSoup object for
    further manipulation.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session to use for
        the HTTP request.
        current_url (str): The URL to fetch HTML content from.

    Returns:
        Optional[BeautifulSoup]: A BeautifulSoup object containing the parsed
        HTML content, or None if an error occurs during the request.

    Raises:
        Various aiohttp errors: For different types of HTTP request errors:
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
            aiohttp.ServerTimeoutError,
            aiohttp.ClientError.
    """
    try:
        async with session.get(current_url) as r:
            text = await r.text()
    except (
        aiohttp.ClientConnectionError,
        aiohttp.ClientResponseError,
        aiohttp.ServerTimeoutError,
        aiohttp.ClientError,
    ) as error:
        logger.critical(f"Error on {current_url} - {error}")
        return None
    return BeautifulSoup(text, "lxml")


async def scrape_bestiary(
    url: str, min_armor_class: int, max_armor_class: int
) -> List[MonsterCard]:
    """
    Scrap the D&D bestiary based on armor class criteria.

    Args:
        url (str): The URL of the D&D bestiary.
        min_armor_class (int): Minimum armor class.
        max_armor_class (int): Maximum armor class.

    Returns:
        List[MonsterCard]: List of MonsterCard objects.
    """
    headers = {"User-Agent": SCRAPER_CONSTANTS["USER_AGENT"]}
    async with aiohttp.ClientSession(headers=headers) as session:
        monsters_list: List[MonsterCard] = []
        page_num = 1
        last_page = False
        while not last_page and page_num <= SCRAPER_SETTINGS["MAX_PAGES"]:
            current_url = url + f"&page={page_num}"
            try:
                soup = await get_soup(session=session, current_url=current_url)
                check_if_none(soup, f"No data found on link {current_url}")
                cards = soup.find_all("div", class_="card") if soup else None
                check_if_none(cards, f"No data found on link {current_url}")
            except EmptyDataError as error:
                logger.error(f"Scraper error - {error}")
            monsters_list.extend(
                await scrape_cards(
                    cards,  # type: ignore # Already checked by check_if_none()
                    min_armor_class,
                    max_armor_class,
                )
            )
            logger.debug(f" Read page №{page_num}")
            last_page = is_last_page(soup) if soup is not None else True
            if last_page:
                logger.debug(" Reading pages completed.\n")
            page_num += 1
            await asyncio.sleep(SCRAPER_SETTINGS["SLEEP_TIME"])
        return monsters_list
