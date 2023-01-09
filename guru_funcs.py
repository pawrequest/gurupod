# get number of pages from 'last' tagged href css selector page-link
import json
import requests
from bs4 import BeautifulSoup

EPISODE_DICT = {}


def get_num_pages(main_url: str) -> int:
    """
    gets number of pages from the 'last' button on captivate.fm
    :param main_url:
    :return num_pages:
    """
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.replace("https://decoding-the-gurus.captivate.fm/episodes/", "")
    num_pages = int(num_pages.replace("#showEpisodes", ""))  #

    return num_pages


def get_details(show_url: str) -> (list, list):
    """
    gets show_notes and show_links from episode_url
    :param show_url:
    :return:
    """
    response = requests.get(show_url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.select(".show-notes p")
    show_notes = ([p.text for p in paragraphs if p.text != "Links"])
    show_links_html = soup.select(".show-notes li")
    show_links = [li.a['href'] for li in show_links_html]
    return show_notes, show_links


def get_episodes(page_url: str) -> dict:
    """
    gets data for mutliple episodes from a given page
    retrieves title, date, url
    calls get_details to scrape show_notes and show_links from the page at show_url
    returns a dictionary of episodes - titles as keys
    :param page_url:
    :return:
    """
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    episode_soup = soup.select(".episode")
    show_dict = {}
    for episode in episode_soup:
        show_title = episode.select_one(".episode-title a").text
        show_date = episode.select_one(".publish-date").text
        show_url = episode.select_one(".episode-title a")['href']
        show_notes, show_links = get_details(show_url)

        show_dict[show_title] = {"URL": show_url,
                                 "Date": show_date,
                                 "Show Notes": show_notes,
                                 "Show Links": show_links
                                 }

    return show_dict


def create_markup_text(episode_dict):
    markup_text = ""
    for episode_name, details in episode_dict.items():
        date_pub = details.get('Date')
        show_url = details.get('URL')
        show_notes = details.get('Show Notes')
        show_links = details.get('Show Links')

        markup_text += f"<h1>{episode_name}</h1>\n"
        markup_text += f"<p>Date Published: {date_pub}</p>\n"
        markup_text += f"<a href='{show_url}'>Play on Captivate.fm</a>"

        if show_notes:
            markup_text += "<h3>Show Notes:</h3>\n"
            for note in show_notes:
                markup_text += f"<p>{note}</p>\n"

        if show_links:
            markup_text += "<h3>Show Links:</h3>\n"
            for link in show_links:
                markup_text += f"<a href='{link}'>{link}</a><br>"

        markup_text += "<br> <br>"
    return markup_text


def runscript(main_url):
    for page in range(get_num_pages(main_url)):
        # for page in range(2):
        page_url = main_url + f"/episodes/{page + 1}/#showEpisodes"
        episode_dict = get_episodes(page_url)
        EPISODE_DICT.update(episode_dict)

    markup_text = create_markup_text(EPISODE_DICT)

    with open('episodes.html', "w", encoding="utf-8") as file:
        file.write(markup_text)

    with open("episodes.json", "w") as outfile:
        json.dump(EPISODE_DICT, outfile)
