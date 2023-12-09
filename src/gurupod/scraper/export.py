from data.consts import EPISODES_JSON, MAIN_URL


def fetch_episodes(main_url=MAIN_URL, injson=EPISODES_JSON):
    new_eps = asyncio.run(new_episodes_(main_url, existing_d=existing_dict))
    all_eps = existing_eps + new_eps
    _sort_n_number_eps(all_eps)
    if new_eps:
        export_episodes_json(all_eps)
    return all_eps



async def new_episodes_(main_url: str, existing_d: dict or None = None) -> List[Episode]:
    episodes = []
    async with aiohttp.ClientSession() as session:
        pages = await listing_pages_(main_url, session)
        for page in pages:
            eps = await episodes_from_page(page, session, existing_d)
            if not eps:
                break
            episodes.extend(eps)
    return episodes
