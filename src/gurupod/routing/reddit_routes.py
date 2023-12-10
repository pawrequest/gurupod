from fastapi import APIRouter


red_router = APIRouter()

# @red_router.post('/post_sub')
# async def post_episode_subreddit(key: str, episode: EpisodeDB,
#                                  subreddit: Subreddit = Depends(subreddit_dflt)):
#     if key != REDDIT_SEND_KEY:
#         return 'wrong key'
#     subreddit = await subreddit
#     return await submit_episode_subreddit(episode, subreddit)


# @red_router.post('/update_wiki')
# async def update_wiki_dflt(key, session: Session = Depends(get_session),
#                            wiki_page: WikiPage = Depends(wiki_page_dflt)):
#     if key != REDDIT_SEND_KEY:
#         return 'wrong key'
#     episodes = session.exec(select(EpisodeDB)).all()
#     markup = episodes_wiki(episodes)
#     res = await edit_reddit_wiki(markup, wiki_page)
#     return res
#
#
