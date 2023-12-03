import csv
import json
import os
from datetime import datetime
import praw
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dateutil.parser import parse

MAIN_URL = "https://decoding-the-gurus.captivate.fm"
REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_PASS = os.environ['REDDIT_PASS']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SEC = os.environ['CLIENT_SEC']
USER_AGENT = "Guru_Pod Wiki updater by prosodyspeaks"
REDIRECT = "http://localhost:8080"
REF_TOK = os.environ['REF_TOK']


@dataclass
class Pod:
    main_url: str

    def __post_init__(self):
        try:
            with open("../data/episodes.json", 'r') as input_json:
                pod_dict = json.load(input_json)
                print(f"Json Loaded with {len(pod_dict)} entries")
        except:
            print("Fresh Json dict")
            pod_dict = {}
        self.json_dict = pod_dict
        self.episodes = []
        for episode, details in pod_dict.items():
            object_dict = {episode:details}
            episode_o = Episode(episode_json=object_dict)
            self.episodes.append(episode_o)

        response = requests.get(self.main_url)
        self.mainsoup = BeautifulSoup(response.text, "html.parser")
        self.pod_name = self.mainsoup.select_one(".about-title").text
        listing_pages = self.get_listing_pages()
        episode_pages = self.get_episode_pages(listing_pages)
        self.new_episodes = [Episode(page) for page in episode_pages]

    def get_listing_pages(self):
        page_links = self.mainsoup.select(".page-link")
        lastpage = page_links[-1]['href']
        num_pages = lastpage.replace(f"{self.main_url}/episodes/", "")
        num_pages = int(num_pages.replace("#showEpisodes", ""))  #
        pages = []
        for page in range(num_pages):
            # for page in range(1):
            pages.append(self.main_url + f"/episodes/{page + 1}/#showEpisodes")
        return pages

    def get_episode_pages(self, listing_pages):
        episode_pages = []
        end_search = False
        for page in listing_pages:
            response = requests.get(page)
            soup = BeautifulSoup(response.text, "html.parser")
            episode_soup = soup.select(".episode")
            for episode in episode_soup:
                link = episode.select_one(".episode-title a")['href']
                title = episode.select_one(".episode-title").text
                if title in self.json_dict:
                    print(f"Episode already in JSON: {title} \nEnding Search")
                    end_search = True
                    break
                else:
                    print(f"New Episode found: {title}")
                    episode_pages.append(link)
            if end_search:
                break

        return episode_pages

    def update_json(self):
        update_package = {}
        for episode in self.new_episodes:
            update_package[episode.show_name] = {'show_url': episode.episode_url,
                                                 'show_date': episode.show_date.date().isoformat(),
                                                 'show_notes': episode.show_notes,
                                                 'show_links': episode.show_links}
        if update_package:
            print(f"Update Package:{update_package}")
            update_package.update(self.json_dict)
            self.json_dict = update_package
            with open("../data/episodes.json", "w") as outfile:
                json.dump(update_package, outfile)


        else:
            print("No Update")

    def create_markup(self, format):
        '''
           takes a dict of episodes and format - html or reddit - and returns markup/markdown
           :param episode_dict:
           :param format: "reddit" or "html"
           :return:
           '''
        markup_text = ""

        for episode_name, details in self.json_dict.items():
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
        self.markup = markup_text
        return markup_text

    def write_markup(self, format):
        '''
        :param format: 'html' or 'reddit'(as .txt)
        :return: writes to file
        '''
        if format.lower() == "reddit":
            with open('data/episodes.txt', "w", encoding="utf-8") as output_txt:
                markdown_text = self.create_markup(format)
                output_txt.write(markdown_text)
                print("Wrote out .txt file for reddit markdown")
        else:
            with open('data/episodes.html', "w", encoding="utf-8") as output_html:
                markup_text = self.create_markup(format)
                output_html.write(markup_text)
                print("html")

    def update_wiki(self, subr, wiki_page):
        reddit = praw.Reddit(client_id=CLIENT_ID,
                             client_secret=CLIENT_SEC,
                             user_agent=USER_AGENT,
                             redirect_uri=REDIRECT,
                             refresh_token=REF_TOK
                             )

        subreddit = reddit.subreddit(subr)
        wiki = subreddit.wiki[wiki_page]
        if input(f"Overwrite The Reddit Wiki page '{wiki_page}'?").lower()[0] == "y":
            wiki.edit(content=self.markup)
            print("edited the wiki")





@dataclass
class Episode:
    episode_url: str = None
    episode_json: dict = None

    def __post_init__(self):
        if self.episode_url:
            self.episode_from_url()
        elif self.episode_json:
            self.episode_from_json()

    def episode_from_json(self):
        for show_name, details in self.episode_json.items():
            self.show_name = show_name
            self.show_links = details['show_links']
            self.show_notes = details['show_notes']
            self.show_date = details['show_date']
            self.show_url = details['show_url']
            print(f"Episode object Created from Json: {self.show_name}")


    def episode_from_url(self):
        response = requests.get(self.episode_url)
        self.episode_soup = BeautifulSoup(response.text, "html.parser")
        self.show_name: str = self.episode_soup.select_one(".episode-title").text
        self.show_links: dict = self.get_show_links()
        self.show_notes: list = self.get_show_notes()
        self.show_date = parse(self.episode_soup.select_one(".publish-date").text)
        print(f"Episode object Created from Url: {self.show_name}")

    def get_show_notes(self):
        paragraphs = self.episode_soup.select(".show-notes p")
        full_show_notes = [p.text for p in paragraphs]
        show_notes = []

        for note in full_show_notes:
            if note == "Links":
                break
            else:
                show_notes.append(note)

        return show_notes

    def get_show_links(self):
        show_links_html = self.episode_soup.select(".show-notes a")
        show_links_dict = {}
        for aref in show_links_html:
            show_links_dict[aref.text] = aref['href']
        return show_links_dict


GuruPod = Pod(MAIN_URL)
if GuruPod.new_episodes:
    GuruPod.update_json()
    GuruPod.write_markup('reddit')
    GuruPod.update_wiki(subr='DecodingTheGurus', wiki_page='episodes')
else:
    print("No New Episodes")

...
