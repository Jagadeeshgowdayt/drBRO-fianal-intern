import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb

# --- ⚠️ IMPORTANT: Fill in your bot's credentials ---
# You can get these from my.telegram.org
API_ID = 12345  # REPLACE WITH YOUR API ID
API_HASH = "YOUR_API_HASH_HERE"  # REPLACE WITH YOUR API HASH
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" # REPLACE WITH YOUR BOT TOKEN
# ----------------------------------------------------

# --- SCRIPT CLASS (FROM YOUR Script.py) ---
class script(object):
    TOP_MOVIES_LIST_TXT = "🎬 **Here are the Top 10 Movies.**\n\nClick the button next to a movie to get its full details:"
    
    TOP_MOVIE_BUTTON_TEXT = "Details for '{title}'"

    TOP_MOVIE_DETAIL_TXT = """<b>🎬 Title:</b> <a href="{url}">{title}</a> ({year})

<b>⭐ Rating:</b> {rating} / 10
<b>🎭 Genres:</b> {genres}
<b>🗣️ Language:</b> {language}

<b>📜 Plot:</b> {plot}"""

# A unique prefix for buttons to avoid conflicts with other plugins
BUTTON_PREFIX = "movie_detail"

# Initialize the Pyrogram Client and IMDb
app = Client("movie_details_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
ia = IMDb()

# List of all the movies you want to feature
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]

@app.on_message(filters.command("topmovies"))
async def list_movies_with_buttons(client: Client, message: Message):
    """
    Sends a list of movies, each with its own 'Show Details' button, using text from the script class.
    """
    print(f"✅ /topmovies command received in chat {message.chat.id}")
    
    # Use the text from the script class
    text = script.TOP_MOVIES_LIST_TXT
    
    # Create a list of buttons, one for each movie
    buttons = []
    for i, title in enumerate(MOVIE_LIST):
        button_text = script.TOP_MOVIE_BUTTON_TEXT.format(title=title)
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"{BUTTON_PREFIX}_{i}"
        )
        buttons.append([button])

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex(f"^{BUTTON_PREFIX}_"))
async def show_movie_details(client: Client, query: CallbackQuery):
    """
    Handles when a user clicks a 'Show Details' button and uses the script class for the caption.
    """
    await query.answer("Fetching details...")
    
    chat_id = query.message.chat.id
    try:
        movie_index = int(query.data.split("_")[2])
        movie_title = MOVIE_LIST[movie_index]

        print(f"✅ User requested details for '{movie_title}' in chat {chat_id}")

        # --- Fetch movie details from IMDb ---
        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        if not search_results:
            await client.send_message(chat_id, f"Sorry, I couldn't find details for '{movie_title}'.")
            return

        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie)

        # --- Extract and format details ---
        poster = movie.get('full-size cover url', 'https://placehold.co/600x900/1e293b/ffffff?text=Poster+Not+Found')
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        language = movie.get('languages', ['N/A'])[0]
        plot = movie.get('plot outline', 'No plot summary available.')
        genres = ', '.join(movie.get('genres', ['N/A']))
        imdb_url = f"https://www.imdb.com/title/tt{movie.movieID}"

        # Use the template from the script class to create the caption
        caption = script.TOP_MOVIE_DETAIL_TXT.format(
            url=imdb_url,
            title=title,
            year=year,
            rating=rating,
            genres=genres,
            language=language,
            plot=plot
        )

        # --- Send a new message with the movie details ---
        await client.send_photo(
            chat_id=chat_id,
            photo=poster,
            caption=caption,
            reply_to_message_id=query.message.id 
        )

    except Exception as e:
        print(f"❌ An error occurred in show_movie_details: {e}")
        await client.send_message(chat_id, "Sorry, an error occurred while fetching the details.")


if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or API_ID == 12345 or API_HASH == "YOUR_API_HASH_HERE":
        print("\n[ERROR] PLEASE OPEN THE SCRIPT AND FILL IN YOUR BOT_TOKEN, API_ID, and API_HASH.\n")
    else:
        print("Bot is starting...")
        app.run()
        print("Bot has stopped.")
