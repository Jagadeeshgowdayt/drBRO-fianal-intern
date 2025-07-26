import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb

# --- ⚠️ IMPORTANT ⚠️ ---
# --- PASTE YOUR BOT TOKEN HERE ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
# --- AND YOUR API ID AND HASH ---
API_ID = 12345  # REPLACE WITH YOUR API ID
API_HASH = "YOUR_API_HASH_HERE"
# -----------------------------------

# Check if the credentials are set
if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or API_ID == 12345 or API_HASH == "YOUR_API_HASH_HERE":
    print("\n[ERROR] PLEASE OPEN THE 'test_movies.py' FILE AND FILL IN YOUR BOT_TOKEN, API_ID, and API_HASH.\n")
    exit()

# Initialize the Pyrogram Client
app = Client("movie_test_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- DATA ---
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]
ia = IMDb()

# --- HANDLERS ---
@app.on_message(filters.command("topmovies"))
async def start_top_movies_command(client, message):
    chat_id = message.chat.id
    print(f"✅ /topmovies command received in chat {chat_id}")
    await display_movie(client, chat_id, movie_index=0, message_to_edit=None)


@app.on_callback_query()
async def handle_all_callbacks(client, query: CallbackQuery):
    """
    This single handler processes all button presses for this test.
    """
    chat_id = query.message.chat.id
    data = query.data
    print(f"✅ Button pressed in chat {chat_id} with data: {data}")
    await query.answer()

    try:
        parts = data.split("_")
        action = parts[1]
        current_index = int(parts[2])

        if action == "close":
            await query.message.delete()
            return

        new_index = current_index
        if action == "next":
            new_index += 1
        elif action == "prev":
            new_index -= 1

        await display_movie(client, chat_id, movie_index=new_index, message_to_edit=query.message)
    except Exception as e:
        print(f"❌ ERROR in callback handler: {e}")

# --- CORE LOGIC ---
async def display_movie(client, chat_id, movie_index, message_to_edit=None):
    try:
        movie_title = MOVIE_LIST[movie_index]
        print(f"🔄 Displaying '{movie_title}' (index {movie_index})...")

        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie)

        poster = movie.get('full-size cover url', 'https://i.imgur.com/B1YTE4p.jpg')
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        language = movie.get('languages', ['N/A'])[0]
        caption = f"**{title}** ({year})\n\n**⭐ Rating:** {rating}/10\n**🗣️ Language:** {language}"

        # Note the very specific callback_data format
        buttons = []
        row = []
        if movie_index > 0:
            row.append(InlineKeyboardButton('⬅️ Previous', callback_data=f"movie_prev_{movie_index}"))
        if movie_index < len(MOVIE_LIST) - 1:
            row.append(InlineKeyboardButton('Next ➡️', callback_data=f"movie_next_{movie_index}"))
        buttons.append(row)
        buttons.append([InlineKeyboardButton("❌ Close", callback_data=f"movie_close_{movie_index}")])
        reply_markup = InlineKeyboardMarkup(buttons)

        if message_to_edit:
            await message_to_edit.edit_media(media=poster, caption=caption, reply_markup=reply_markup)
        else:
            await client.send_photo(chat_id=chat_id, photo=poster, caption=caption, reply_markup=reply_markup)
        print(f"✅ Successfully displayed '{title}'.")
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"❌ ERROR in display_movie: {e}")

# --- RUN THE BOT ---
print("Bot is starting...")
app.run()
print("Bot has stopped.")
