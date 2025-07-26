# plugins/top_movies.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb
import asyncio

print("✅ DEBUG: top_movies.py plugin (with hardcoded list) loaded successfully!")

# Initialize the IMDbPY library
ia = IMDb()

# Your custom list of top movies
HARDCODED_MOVIE_TITLES = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "The Godfather Part II",
    "12 Angry Men",
    "Schindler's List",
    "The Lord of the Rings: The Return of the King",
    "Pulp Fiction",
    "The Good, the Bad and the Ugly",
    "Forrest Gump"
]

# Cache to store the fetched movie objects
top_movies_cache = []

async def get_top_movies_from_list():
    """
    Fetches IMDb movie objects for the hardcoded list and caches them.
    """
    global top_movies_cache
    if not top_movies_cache:
        print("✅ DEBUG: Fetching details for hardcoded movie list from IMDb...")
        loop = asyncio.get_running_loop()
        # Create a list to hold the movie objects
        movie_objects = []
        for title in HARDCODED_MOVIE_TITLES:
            # Search for the movie
            # We run the synchronous search in an executor to avoid blocking
            search_results = await loop.run_in_executor(None, ia.search_movie, title)
            if search_results:
                # Add the first search result to our list
                movie_objects.append(search_results[0])
        top_movies_cache = movie_objects
        print("✅ DEBUG: Movie cache created.")
    return top_movies_cache

@Client.on_message(filters.command("topmovies"))
async def show_top_movies(client, message):
    print("✅ DEBUG: /topmovies command received.")
    # Show a "loading" message because fetching all details can take a moment
    loading_message = await message.reply_text("🎬 _Fetching your custom top 10 list..._")
    await show_movie_info(client, message, movie_index=0)
    # Delete the "loading" message once the first movie is shown
    await loading_message.delete()


async def show_movie_info(client, message_or_query, movie_index):
    """Fetches and displays a movie's info from the cached list."""
    movies = await get_top_movies_from_list()
    if not movies or movie_index >= len(movies):
        await message_or_query.reply_text("Couldn't retrieve the movie from the list.")
        return

    # Get the specific movie from our cached list
    movie = movies[movie_index]

    # --- Fetch full details for the movie ---
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, ia.update, movie)

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
    if movie_index < len(movies) - 1:
        row.append(InlineKeyboardButton('Next ➡️', callback_data=f"topmovie_{movie_index + 1}"))
    buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_top_movies")])
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        if isinstance(message_or_query, CallbackQuery):
            await message_or_query.message.edit_media(media=poster, caption=caption, reply_markup=reply_markup)
        else:
            await client.send_photo(chat_id=message_or_query.chat.id, photo=poster, caption=caption, reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"❌ DEBUG: Error in show_movie_info: {e}")

@Client.on_callback_query(filters.regex("^topmovie_"))
async def top_movie_callback(client, query: CallbackQuery):
    print(f"✅ DEBUG: Button pressed! Callback data: {query.data}")
    await query.answer()
    try:
        movie_index = int(query.data.split("_")[1])
        await show_movie_info(client, query, movie_index)
    except Exception as e:
        print(f"❌ DEBUG: Error in top_movie_callback: {e}")

@Client.on_callback_query(filters.regex("^close_top_movies$"))
async def close_top_movies_callback(client, query: CallbackQuery):
    print("✅ DEBUG: Close button pressed!")
    await query.answer()
    await query.message.delete()
