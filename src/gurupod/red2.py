import praw

from data.consts import DTG_SUB, GURUS
from gurupod.reddit import reddit_

texty = GURUS.pop() + ' lots of other text'
print(f'{texty=}')

reddit: praw.Reddit = reddit_()
reddit.subreddit(DTG_SUB).submit(texty, selftext="a load of filler text")
