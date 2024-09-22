FROM python:3.10-slim

ADD telegram_cat_bot.py . 
ADD vars.json . 
RUN pip install python-telegram-bot spotipy

CMD python3 telegram_cat_bot.py