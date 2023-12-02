import asyncio
import requests
from bs4 import BeautifulSoup
from django.urls import reverse


GURU_URL = "https://decoding-the-gurus.captivate.fm"
EPISODE_IMPORTER_URL = "http://localhost:8000/episode-from-url/"  # Replace with your actual URL

async def import_all_episodes(main_url):
    episode_urls = episode_urls_from_main(main_url)
    tasks = [asyncio.create_task(import_episode(url)) for url in episode_urls]
    await asyncio.gather(*tasks)

async def episode_urls_from_main(main_url):
    response = await asyncio.to_thread(requests.get, main_url)
    mainsoup = BeautifulSoup(response.text, "html.parser")
    pod_name = mainsoup.select_one(".about-title").text
    listing_urls = await asyncio.to_thread(get_listing_urls, mainsoup=mainsoup, main_url=main_url)[:2]  # LIMITED TO 2
    episode_urls = await asyncio.to_thread(get_episode_urls, listing_urls=listing_urls)
    return episode_urls

async def import_episode(url):
    data = {'episode_url': url}
    added_episode_response = await asyncio.to_thread(requests.post, EPISODE_IMPORTER_URL, data=data)
    return added_episode_response

def get_listing_urls(mainsoup, main_url) -> list[str]:
    page_links = mainsoup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.replace(f"{main_url}/episodes/", "")
    num_pages = int(num_pages.replace("#showEpisodes", ""))  #
    page_urls = []
    for page in range(num_pages):
        # for page in range(1):
        page_urls.append(main_url + f"/episodes/{page + 1}/#showEpisodes")
    return page_urls

def get_episode_urls(listing_urls):
    episode_page_urls = []
    for page in listing_urls:
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")
        episode_soup = soup.select(".episode")
        for episode in episode_soup:
            link = episode.select_one(".episode-title a")['href']

            episode_page_urls.append(link)
    return episode_page_urls

asyncio.run(import_all_episodes(GURU_URL))