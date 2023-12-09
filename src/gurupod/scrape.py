from datetime import datetime
from typing import Literal

from bs4 import BeautifulSoup

MAYBE_ATTR = Literal['name', 'notes', 'links', 'date']
# def deet_from_soup(deet: Literal['name', 'notes', 'links', 'date'], soup: BeautifulSoup):


def set_soup(values):
    print(f'{type(values)=}')
    if missing := [_ for _ in MAYBE_ATTR.split() if getattr(values, _) is None]:

        # todo constrain get_deets to only MAYBE_ATTRS
        """
        strats: 1) iterate over maybe_attrs, if missing, get from soup
                    cant iterate over literal?
                2) construct type from tuple
                    cant unpack into literal?
            """

        response = requests.get(values.url)
        soup = BeautifulSoup(response.text, "html.parser")

        # async with aiohttp.ClientSession() as session:
        #     async with session.get(values.url) as response:
        #         text = await response.text()
        # soup = BeautifulSoup(text, "html.parser")

        for key in missing:
            val = deet_from_soup(key, soup)
            if key == 'date':
                val = datetime.strptime(val, '%Y-%m-%d')
            setattr(values, key, val)
            # [setattr(values, key, deet_from_soup(key, soup)) for key in missing]
    return values
def deet_from_soup(deet: MAYBE_ATTR, soup: BeautifulSoup):
    if deet == 'name':
        return soup_title(soup)
    if deet == 'notes':
        return soup_notes(soup)
    if deet == 'links':
        return soup_links(soup)
    if deet == 'date':
        return soup_date(soup)
    else:
        raise ValueError(f'invalid deet: {deet}')


def soup_date(soup) -> datetime:
    return soup.select_one(".publish-date").text


def soup_notes(soup: BeautifulSoup) -> list:
    """ some listing have literal("Links") as heading for next section some dont """

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes or None


def soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict


def soup_title(soup: BeautifulSoup) -> str:
    return soup.select_one(".episode-title").text
