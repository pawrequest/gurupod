from pprint import pprint

import requests
from bs4 import BeautifulSoup

from static.resource import ALL_EPISODE_URLS

FAILS = ['https://decoding-the-gurus.captivate.fm/episode/special-episode-interview-with-virginia-heffernan-on-edge-the-dangers-of-scientism-culture-wars']
GURU_URL = "https://decoding-the-gurus.captivate.fm"
EPISODE_IMPORTER_URL = "http://localhost:8000/episode-from-url/"
BULK_IMPORTER_URL = "http://localhost:8000/bulk-importer/"


def get_episodes_from_api():
    response = requests.get("http://localhost:8000/all-episodes/")
    return response.json()


def get_episode_urls_from_api():
    response = requests.get("http://localhost:8000/all-episode-urls/")
    return response.json()


def import_episode(episode_url):
    for count in range(3):
        data = {'episode_url': episode_url}
        response = requests.post(EPISODE_IMPORTER_URL, data=data)
        if response.status_code == 201:
            print(f'Episode imported {episode_url}')
            return response
        if response.status_code == 400:
            print(f'Episode really already exists {episode_url}')
            return response
        print(f'Error importing {episode_url}, retrying #{count} ')
    else:
        print(f'Fatal Error importing episode {episode_url} '
              f'{response.status_code=}')
    return response


def listing_urls_from_main(main_url) -> list[str]:
    response = requests.get(main_url)
    mainsoup = BeautifulSoup(response.text, "html.parser")
    pod_name = mainsoup.select_one(".about-title").text
    page_links = mainsoup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.replace(f"{main_url}/episodes/", "")
    num_pages = int(num_pages.replace("#showEpisodes", ""))  #
    page_urls = []
    for page in range(num_pages):
        # for page in range(1):
        page_urls.append(main_url + f"/episodes/{page + 1}/#showEpisodes")
    return page_urls


def get_all_episode_urls(listing_urls):
    if isinstance(listing_urls, str):
        listing_urls = [listing_urls]
    episode_page_urls = []
    for page in listing_urls:
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")
        episode_soup = soup.select(".episode")
        for episode in episode_soup:
            link = episode.select_one(".episode-title a")['href']
            episode_page_urls.append(link)
    return episode_page_urls


def just_fails(fails):
    existing_urls = set(get_episode_urls_from_api())
    failures = []
    for url in fails:
        if url in existing_urls:
            print(f'Episode already exists {url}')
            continue
        response = import_episode(url)
        if response.status_code != 201:
            failures.append(url)
        return failures


def from_disk():
    ep_to_add = episode_to_add2()
    failures = []
    for url in ep_to_add:
        response = import_episode(url)
        if response.status_code != 201:
            failures.append(url)
        print(url, response.status_code)


def episode_to_add2():
    all_episodes = set(ALL_EPISODE_URLS)
    print(f'{len(all_episodes)=}')
    existing = set(get_episode_urls_from_api())
    print(f'{len(existing)=}')
    ep_to_add = all_episodes - existing
    print(f'{len(ep_to_add)=}')
    return ep_to_add


def one_at_a_time():
    listing_urls = listing_urls_from_main(main_url=GURU_URL)
    existing = set(get_episode_urls_from_api())

    failures = []
    for page in listing_urls:
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")
        episode_soup = soup.select(".episode")
        for episode in episode_soup:
            link = episode.select_one(".episode-title a")['href']
            if link in existing_urls:
                print(f'Episode already exists {link}')
                continue
            response = import_episode(link)
            if response.status_code != 201:
                failures.append(link)
    return failures


def import_all_episodes(main_url):
    all_episodes = set(ALL_EPISODE_URLS)
    existing = set(get_episode_urls_from_api())
    for url in all_episodes:
        if url in existing:
            print(f'Episode already exists {url}')
            continue
        response = import_episode(url)
        if response.status_code != 201:
            print(f'Error importing {url}, {response.status_code=}')
        print(url, response.status_code)
        ...
    print("Done")


# failures = one_at_a_time()
# pprint (failures)
# fails = just_fails(FAILS)
# pprint(failures)
# failures = from_disk()
failures = requests.post(BULK_IMPORTER_URL, data={})
...
