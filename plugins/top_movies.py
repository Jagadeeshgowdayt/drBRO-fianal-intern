# plugins/top_movies.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb
import asyncio

print("✅ DEBUG: FINAL_SOLUTION (top_movies.py) loaded.")

# --- DATA ---
# This dictionary stores the user's current movie index
# It's correct to use user_id as the key here to track individual sessions
user_movie_state = {}

# Your custom list of top movies
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]

ia = IMDb()

# --- HANDLERS ---

@Client.on_message(filters.command("topmovies"))
async def start_top_movies_command(client, message):
    """Entry point for the /topmovies command."""
    user_id = message.from_user.id
    chat_id = message.chat.id  # <-- **THE FIX: Get the chat_id**
    print(f"✅ DEBUG: /topmovies from user {user_id} in chat {chat_id}")

    # Set the user's starting position
    user_movie_state[user_id] = 0

    # Pass the correct chat_id to the display function
    await display_movie(client, user_id, chat_id, message_to_edit=None)

@Client.on_callback_query(filters.regex("^(next_movie|prev_movie|close_movies)$"))
async def navigate_movies_callback(client, query: CallbackQuery):
    """Handles all button presses for this feature."""
    user_id = query.from_user.id
    chat_id = query.message.chat.id  # <-- **THE FIX: Get chat_id from the query**
    action = query.data

    print(f"✅ DEBUG: Button '{action}' by user {user_id} in chat {chat_id}")
    await query.answer()

    if action == "close_movies":
        if user_id in user_movie_state:
            del user_movie_state[user_id]
        await query.message.delete()
        return

    if user_id not in user_movie_state:
        user_movie_state[user_id] = 0
    else:
        if action == "next_movie":
            user_movie_state[user_id] += 1
        elif action == "prev_movie":
            user_movie_state[user_id] -= 1

    # Pass the correct chat_id when updating the message
    await display_movie(client, user_id, chat_id, message_to_edit=query.message)

# --- CORE LOGIC ---

async def display_movie(client, user_id, chat_id, message_to_edit=None):
    """The main function to fetch and display a movie."""
    current_index = user_movie_state.get(user_id, 0)
    movie_title = MOVIE_LIST[current_index]

    print(f"✅ DEBUG: Displaying '{movie_title}' for user {user_id} in chat {chat_id}")

    try:
        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        if not search_results:
            await client.send_message(chat_id, f"Could not find details for '{movie_title}'.")
            return

        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie)

        poster = movie.get('full-size cover url', 'https://i.imgur.com/B1YTE4p.jpg')
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        language = movie.get('languages', ['N/A'])[0]
        plot = movie.get('plot outline', 'No plot summary available.')

        caption = (f"**🎬 Title:** {title} ({year})\n\n"
                   f"**⭐ Rating:** {rating} / 10\n"
                   f"**🗣️ Language:** {language}\n\n"
                   f"**📜 Plot:** {plot}")

        buttons = []
        row = []
        if current_index > 0:
            row.append(InlineKeyboardButton('⬅️ Previous', callback_data="prev_movie"))
        if current_index < len(MOVIE_LIST) - 1:
            row.append(InlineKeyboardButton('Next ➡️', callback_data="next_movie"))
        buttons.append(row)
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_movies")])
        reply_markup = InlineKeyboardMarkup(buttons)

        if message_to_edit:
            await message_to_edit.edit_media(media=poster, caption=caption, reply_markup=reply_markup)
        else:
            # **THE FIX: Use the correct chat_id to send the initial message**
            await client.send_photo(chat_id=chat_id, photo=poster, caption=caption, reply_markup=reply_markup)

    except MessageNotModified:
        pass
    except Exception as e:
        # Provide a more specific error log
        print(f"❌ ERROR in display_movie for chat {chat_id}: {e}")
