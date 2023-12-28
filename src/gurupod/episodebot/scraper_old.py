#
# async def scrape_titles_urls(aiosession: ClientSession, main_url) -> AsyncGenerator[tuple[str, str], None]:
#     listing_pages = await _listing_pages(main_url, aiosession)
#     new = []
#     for i, _ in enumerate(listing_pages):
#         if DEBUG:
#             logger.debug(f"Scraping page {i + 1} of {len(listing_pages)}")
#         async for title, url in _episode_titles_and_urls_from_listing(_, aiosession):
#             yield title, url
#
#
# async def title_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-title").text.strip()
#
#
# async def url_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-title a")["href"]
#
#
# def date_from_soup_section(soup_section):
#     return soup_section.select_one(".publish-date").text.strip()
#
#
# async def ep_number_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-info").text.strip()


# async def _episode_titles_and_urls_from_listing(
#     listing_page: str, aio_session: ClientSession
# ) -> AsyncGenerator[tuple[str, str], None]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     for soup_section in episodes_res:
#         title = title_from_soup_section(soup_section)
#         url = url_from_soup_section(soup_section)
#         yield title, url


# async def _episode_titles_and_urls_from_listingold(
#     listing_page: str, aio_session: ClientSession
# ) -> tuple[tuple[str, str], ...]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     output = []
#     for soup_section in episodes_res:
#         title = soup_section.select_one(".episode-title").text
#         url = soup_section.select_one(".episode-title a")["href"]
#         output.append((title, url))
#     return tuple(output)


# async def _episode_urls_from_listing(listing_page: str, aio_session: ClientSession) -> list[str]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     urls = [str(ep_soup.select_one(".episode-title a")["href"]) for ep_soup in episodes_res]
#     return urls


# async def _listing_pages(main_url: str, session: ClientSession) -> list[str]:
#     main_html = await _response(main_url, session)
#     main_soup = BeautifulSoup(main_html, "html.parser")
#     num_pages = _num_pages(main_soup)
#     listing_pages = _listing_page_strs(main_url, num_pages)
#     return sorted(listing_pages, key=lambda x: int(x.split("/")[-2]))


# def _num_pages(soup: BeautifulSoup) -> int:
#     page_links = soup.select(".page-link")
#     lastpage = page_links[-1]["href"]
#     num_pages = lastpage.split("/")[-1].split("#")[0]
#     return int(num_pages)
