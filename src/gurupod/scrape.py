from datetime import datetime

from bs4 import BeautifulSoup
from dateutil import parser


def ep_soup_date(ep_soup) -> datetime:
    date_str = ep_soup.select_one(".publish-date").text
    datey = parser.parse(date_str)
    return datey


def ep_soup_notes(soup: BeautifulSoup) -> list:
    """ some listing have literal("Links") as heading for next section some dont """

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes or None


def ep_soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict or None
