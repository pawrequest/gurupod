import json
import os
from datetime import datetime
import praw
# from django.utils import dateformat
from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup

from classes import Episode

MAIN_URL = "https://decoding-the-gurus.captivate.fm"
REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_PASS = os.environ['REDDIT_PASS']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SEC = os.environ['CLIENT_SEC']
USER_AGENT = "Guru_Pod Wiki updater by prosodyspeaks"
REDIRECT = "http://localhost:8080"
REF_TOK = os.environ['REF_TOK']


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


def get_show_notes_and_links(show_url: str) -> (list, dict):
    """
    gets full_show_notes and show_links from episode_url
    :param show_url:
    :return:
    """
    response = requests.get(show_url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.select(".show-notes p")
    full_show_notes = [p.text for p in paragraphs]
    show_notes = []

    for note in full_show_notes:
        if note == "Links":
            break
        else:
            show_notes.append(note)

    show_links_html = soup.select(".show-notes a")
    show_links_dict = {}
    for aref in show_links_html:
        show_links_dict[aref.text] = aref['href']
    return show_notes, show_links_dict


def episode_objects_from_page(page_url: str) -> tuple:
    """
    loads episode dict from json, or creates empty
    gets data for mutliple episodes from a given page
    retrieves title, date, url directly, show_notes and show_links via function call
    returns a list of Episode objects, and booleans for new episodes found / reached end of search
    :param page_url:
    :return:
    """
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    new_ep_found = False
    reached_end = False
    episode_os = []
    try:
        with open("../data/episodes.json", 'r') as input_json:
            show_dict = json.load(input_json)
    except:
        show_dict = {}

    episode_soup = soup.select(".episode")
    for episode in episode_soup:
        show_name = episode.select_one(".episode-title a").text
        show_date_str = episode.select_one(".publish-date").text
        show_date = parse(show_date_str)
        show_url = episode.select_one(".episode-title a")['href']
        show_notes, show_links = get_show_notes_and_links(show_url)

        if show_name in show_dict:
            print(f"Already in json: {show_name} \n ending search")
            reached_end = True
            break

        else:
            print(f"New episode found: {show_name}")
            new_ep_found = True

            episode_o = Episode(show_name=show_name, show_url=show_url, show_links=show_links, show_date=show_date,
                                show_notes=show_notes)
            episode_os.append(episode_o)

    # return (new_dict, new_ep_found, reached_end)
    return (episode_os, new_ep_found, reached_end)


def create_markup(episode_dict: dict, format: str = 'reddit') -> str:
    '''
    takes a dict of episodes and format - html or reddit - and returns markup/markdown
    :param episode_dict:
    :param format: "reddit" or "html"
    :return:
    '''
    markup_text = ""

    for episode_name, details in episode_dict.items():
        date_pub = details.get('show_date')
        show_url = details.get('show_url')
        show_notes = details.get('show_notes')
        show_links = details.get('show_links')

        if format == 'html':
            markup_text += f"<h1>{episode_name}</h1>\n"
            markup_text += f"<p>Date Published: {date_pub}</p>\n"
            markup_text += f"<a href='{show_url}'>Play on Captivate.fm</a>"

            if show_notes:
                markup_text += "<h3>Show Notes:</h3>\n"
                for note in show_notes:
                    markup_text += f"<p>{note}</p>\n"

            if show_links:
                markup_text += "<h3>Show Links:</h3>\n"
                for text, link in show_links.items():
                    markup_text += f"<a href='{link}'>{text}</a><br>"

            markup_text += "<br> <br>"

        elif format == 'reddit':
            markup_text += f"## [{episode_name}]({show_url})\n \n"
            markup_text += f"***Date Published:*** {date_pub}\n \n"
            # markup_text += f"[Play on Captivate.fm]({show_url})"

            if show_notes:
                markup_text += "***Show Notes:***\n \n"
                for note in show_notes:
                    markup_text += f"{note}\n \n"

            if show_links:
                markup_text += "***Show Links:***\n \n"
                for text, link in show_links.items():
                    markup_text += f"[{text}]({link}) \n \n"

            markup_text += "\n \n --- \n"
    return markup_text


def dict_to_markup_file(episodes_dict: dict, format: str):
    '''
    :param format: 'html' or 'reddit'(as .txt)
    :return: writes to file
    '''
    if format.lower() == "reddit":
        with open('data/episodes.txt', "w", encoding="utf-8") as output_txt:
            markdown_text = create_markup(episodes_dict, format)
            output_txt.write(markdown_text)
            print(".txt for reddit")
    else:
        with open('data/episodes.html', "w", encoding="utf-8") as output_html:
            markup_text = create_markup(episodes_dict, format)
            output_html.write(markup_text)
            print("html")


def json_to_markup(format: str):
    '''
    :param format: 'html' or 'reddit'(as .txt)
    :return: writes to file
    '''
    with open("../data/episodes.json", 'r') as input_json:
        episodes_dict = json.load(input_json)
        if format.lower() == "reddit":
            with open('data/episodes.txt', "w", encoding="utf-8") as output_txt:
                markdown_text = create_markup(episodes_dict, format)
                output_txt.write(markdown_text)
                print(".txt for reddit")
        else:
            with open('data/episodes.html', "w", encoding="utf-8") as output_html:
                markup_text = create_markup(episodes_dict, format)
                output_html.write(markup_text)
                print("html")


def get_new_episodes(main_url):
    try:
        with open("../data/episodes.json", "r") as infile:
            dict_in_json = json.load(infile)
            for page in range(get_num_pages(main_url)):
                page_url = main_url + f"/episodes/{page + 1}/#showEpisodes"
                (episode_dict, new_ep_found, reached_end) = episode_objects_from_page(page_url)
                if not new_ep_found:
                    print("no new episodes")
                    break
                else:
                    print("merging new episodes")
                    episode_dict.update(dict_in_json)

                if reached_end:
                    # no point trying more pages
                    print("Search complete")
                    break
                else:
                    # carry on more pages
                    continue
            if new_ep_found:
                with open("../data/episodes.json", "w") as outfile:
                    json.dump(episode_dict, outfile)
                return episode_dict
            else:
                return "no new"


    except:
        print(
            "Error, probably episodes.json doesn't exist or is empty so i'm making a new one from all data on captivate.fm")
        fresh_episode_dict = {}
        with open("../data/episodes.json", "w") as outfile:

            for page in range(get_num_pages(main_url)):
                page_url = main_url + f"/episodes/{page + 1}/#showEpisodes"
                (episode_dict, new_ep_found, reached_end) = episode_objects_from_page(page_url)
                fresh_episode_dict.update(episode_dict)
            json.dump(fresh_episode_dict, outfile)
            return fresh_episode_dict


def update_wiki():
    subr = 'DecodingTheGurus'
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SEC,
                         user_agent=USER_AGENT,
                         redirect_uri=REDIRECT,
                         refresh_token=REF_TOK
                         )

    subreddit = reddit.subreddit(subr)

    episode_dict = get_new_episodes(MAIN_URL)
    if episode_dict == "no new":
        print("nothing new to add")
        exit()
    else:
        markdown = create_markup(episode_dict, format='reddit')
        wikiname = "episodes"
        wiki = subreddit.wiki[wikiname]
        if input(f"overwrite {wikiname}?").lower()[0] == "y":
            wiki.edit(content=markdown)
            print("edited the wiki")


def dict_to_excel(episode_dict):
    for name, details in episode_dict.items():
        print(name)
        for k, v in details.items():
            print(k, v, "\n")
        print(parse(details['show_date']))
        break


# json_to_markup("reddit")

# get_new_episodes(MAIN_URL)

with open("../data/episodes.json", "r") as infile:
    dict_in_json = json.load(infile)
    dict_to_excel(dict_in_json)
