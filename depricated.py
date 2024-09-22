import telegram
import praw
import random
import spotipy
import logging
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)

from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)

import os
import json
from json import loads
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

REDDIT_SECRET = info["REDDIT_SECRET"]
REDDIT_ID = info["REDDIT_ID"]

reddit = praw.Reddit(
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="testscript by u/patchworky"
    )

os.environ["SPOTIPY_CLIENT_ID"] = "afff1a5a8adb417399ac98335bd48f65"
os.environ["SPOTIPY_CLIENT_SECRET"] = "5a0f85558e764ace91f127603fa4d438"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"
playlist_id = "https://open.spotify.com/playlist/2EAaoDpyLoMO5fkhF5cGt7?si=0ea63f10c0f64ad8"
scope = 'user-follow-modify playlist-modify-public'
#token = util.prompt_for_user_token("hagan_b", scope)
#spotify = spotipy.Spotify(auth=token)

# Commands
# async def start(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a cat bot, ask me about cats")

# async def get_random_cat(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Getting a random cat...")

#     # Build array of random cats
#     src = reddit.subreddit("cats+blackcats+catpictures+supermodelcats").hot(limit=25) # poll cats subreddit for top 10 hot posts
#     candidates = []
#     accepted_types = [".png", ".jpg", ".jpeg"] # filter out videos and self posts
#     for post in src:
#         if any(x in post.url for x in accepted_types):
#             candidates.append(post.url)
#     img_url = candidates[random.randint(0, len(candidates)-1)] # select random URL from candidates
#     context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url, caption="Source: {}".format(img_url))

# async def get_cat_fact(update, context):
#     with open('catfacts.txt') as f:
#         facts = f.readlines()
#     fact = facts[random.randint(0, len(facts)-1)].rstrip()
#     context.bot.send_message(chat_id=update.effective_chat.id, text=fact)

# async def add_to_playlist(update, context):
#     message = update.message.text
#     print(f"Processing request for '{msg}'")
#     try:
#         msg = str(message).split("/add ")[1]
#         spotify.user_playlist_add_tracks("hagan_b", playlist_id=playlist_id, tracks=[msg])
#         context.bot.send_message(chat_id=update.effective_chat.id, text=f"Track added.")
#     except:
#         context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error adding track, is your message formatted correctly? Try '/add [spotify URL]'")

# async def i_love_you(update, context):
#     print("Reading message...")
#     message = update.message.text
#     if "I love you CatBot" in str(update.message):
#         context.bot.send_message(chat_id=update.message.chat_id, text="I love you too!")
#         return