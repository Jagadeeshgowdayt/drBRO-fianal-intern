# plugins/top_movies.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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
    # Run the synchronous ia.get_movie in an executor
    loop = asyncio.get_running_loop()
    movie = await loop.run_in_executor(None, ia.get_movie, movie_id)

    # --- Extract Movie Details ---
    poster = movie.get('full-size cover url', 'https://i.imgur.com/B1YTE4p.jpg') # Default poster
    title = movie.get('title', 'N/A')
    year = movie.get('year', 'N/A')
    rating = movie.get('rating', 'N/A')
    # Get the first language, if available
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
    # Logic to create '⬅️ Previous' and 'Next ➡️' buttons
    row = []
    if movie_index > 0:
        row.append(InlineKeyboardButton('⬅️ Previous', callback_data=f"topmovie_{movie_index - 1}"))
    if movie_index < 9: # We have 10 movies (0-9)
        row.append(InlineKeyboardButton('Next ➡️', callback_data=f"topmovie_{movie_index + 1}"))
    buttons.append(row)

    # Add a close button
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_top_movies")])

    reply_markup = InlineKeyboardMarkup(buttons)

    # --- Send or Edit the Message ---
    if isinstance(message_or_query, CallbackQuery):
        # If it's a button click, edit the existing message
        await message_or_query.message.edit_media(
            media=poster,
            caption=caption,
            reply_markup=reply_markup
        )
    else:
        # If it's a command, send a new message
        await client.send_photo(
            chat_id=message_or_query.chat.id,
            photo=poster,
            caption=caption,
            reply_markup=reply_markup
        )


@Client.on_callback_query(filters.regex("^topmovie_"))
async def top_movie_callback(client, query: CallbackQuery):
    """Handles 'Next' and 'Previous' button clicks."""
    try:
        movie_index = int(query.data.split("_")[1])
        await show_movie_info(client, query, movie_index)
    except Exception as e:
        print(f"Error in top_movie_callback: {e}")
        await query.answer("Something went wrong!", show_alert=True)


@Client.on_callback_query(filters.regex("^close_top_movies$"))
async def close_top_movies_callback(client, query: CallbackQuery):
    """Handles the close button click."""
    await query.message.delete()
