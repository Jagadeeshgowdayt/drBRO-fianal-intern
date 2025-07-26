# plugins/top_movies.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb
import asyncio

# Initialize the IMDbPY library
ia = IMDb()

# A dictionary to cache the top movies list to avoid frequent API calls
top_movies_cache = []

async def get_top_movies():
    """Fetches and caches the top 10 movies from IMDb."""
    global top_movies_cache
    if not top_movies_cache:
        print("Fetching top 250 movies from IMDb...")
        # IMDbPY's get_top250_movies is synchronous, so we run it in an executor
        loop = asyncio.get_running_loop()
        # Fetching top 250 is slow, let's just get the top 10 directly if possible
        # For this library, get_top250_movies is the standard way.
        movies = await loop.run_in_executor(None, ia.get_top250_movies)
        top_movies_cache = movies[:10] # We only need the top 10
    return top_movies_cache

@Client.on_message(filters.command("topmovies"))
async def show_top_movies(client, message):
    """Handles the /topmovies command."""
    await show_movie_info(client, message, movie_index=0)

async def show_movie_info(client, message_or_query, movie_index):
    """Fetches and displays a movie's info."""
    movies = await get_top_movies()
    if not movies or movie_index >= len(movies):
        await message_or_query.reply_text("Couldn't retrieve top movies list.")
        return

    # Get the specific movie from the list
    movie_id = movies[movie_index].getID()
    loop = asyncio.get_running_loop()
    movie = await loop.run_in_executor(None, ia.get_movie, movie_id)

    # --- Extract Movie Details ---
    poster = movie.get('full-size cover url', 'https://i.imgur.com/B1YTE4p.jpg')
    title = movie.get('title', 'N/A')
    year = movie.get('year', 'N/A')
    rating = movie.get('rating', 'N/A')
    languages = movie.get('languages', ['N/A'])
    language = languages[0] if languages else 'N/A'
    plot = movie.get('plot outline', 'No plot summary available.')

    # --- Create the Message ---
    caption = (
        f"**🎬 Title:** {title} ({year})\n\n"
        f"**⭐ Rating:** {rating} / 10\n"
        f"**🗣️ Language:** {language}\n\n"
        f"**📜 Plot:** {plot}"
    )

    # --- Create Navigation Buttons ---
    buttons = []
    row = []
    if movie_index > 0:
        row.append(InlineKeyboardButton('⬅️ Previous', callback_data=f"topmovie_{movie_index - 1}"))
    if movie_index < 9:
        row.append(InlineKeyboardButton('Next ➡️', callback_data=f"topmovie_{movie_index + 1}"))
    buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_top_movies")])
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        if isinstance(message_or_query, CallbackQuery):
            await message_or_query.message.edit_media(
                media=poster,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await client.send_photo(
                chat_id=message_or_query.chat.id,
                photo=poster,
                caption=caption,
                reply_markup=reply_markup
            )
    except MessageNotModified:
        # This error happens if the user clicks the same button twice quickly.
        # We can safely ignore it.
        pass
    except Exception as e:
        print(f"Error in show_movie_info: {e}")


@Client.on_callback_query(filters.regex("^topmovie_"))
async def top_movie_callback(client, query: CallbackQuery):
    """Handles 'Next' and 'Previous' button clicks."""
    # ✅ CHANGE 1: Acknowledge the button press immediately.
    await query.answer()
    try:
        movie_index = int(query.data.split("_")[1])
        await show_movie_info(client, query, movie_index)
    except Exception as e:
        print(f"Error in top_movie_callback: {e}")


@Client.on_callback_query(filters.regex("^close_top_movies$"))
async def close_top_movies_callback(client, query: CallbackQuery):
    """Handles the close button click."""
    # ✅ CHANGE 2: Also acknowledge here for consistency.
    await query.answer()
    await query.message.delete()
