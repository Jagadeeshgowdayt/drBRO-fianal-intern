#This Plugin is developed by @Dr_BRO and @DX_MODS

import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import imdb_telegraph  # Corrected import style
from utils import get_poster, temp
from info import (
    AUTH_CHANNEL,
    IMDB,
    IMDB_TEMPLATE,
    SINGLE_BUTTON,
    PROTECT_CONTENT,
    SPELL_CHECK_REPLY,
    CUSTOM_FILE_CAPTION
)


@Client.on_message(filters.command("imdb"))
async def imdb_search(client, message):
    if IMDB == "False":
        return
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("Give me a movie name.\n\nExample: /imdb Lucifer")
    if message.reply_to_message and message.reply_to_message.text:
        search = message.reply_to_message.text
    else:
        search = message.text.split(None, 1)[1]
    
    # Use the corrected import style to call the search method
    imdb_info = imdb_telegraph.poster.search(search)
    
    if imdb_info is None:
        return await message.reply_text("No results found.")
    
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"Check {search} on IMDB",
                    url=imdb_info,
                )
            ]
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text="IMDB", url=imdb_info),
                InlineKeyboardButton(text="Google", url=f"https://www.google.com/search?q={search.replace(' ', '+')}")
            ],
            [
                InlineKeyboardButton(text="Netflix", url=f"https://www.netflix.com/search?q={search.replace(' ', '+')}"),
                InlineKeyboardButton(text="Prime Video", url=f"https://www.primevideo.com/search/ref=atv_nb_sr?phrase={search.replace(' ', '+')}&ie=UTF8")
            ]
        ]
    
    await message.reply_photo(
        photo="https://telegra.ph/file/57912d8a553139ce9a883.jpg",
        caption=f"IMDB Search Results for {search}",
        reply_markup=InlineKeyboardMarkup(btn)
    )

async def get_poster(imdb_id, file):
    # Use the corrected import style to call the imdb_lookup method
    imdb_info = imdb_telegraph.poster.imdb_lookup(imdb_id)
    if imdb_info is None:
        return None, None
    return imdb_info.get('poster'), imdb_info.get('title')

