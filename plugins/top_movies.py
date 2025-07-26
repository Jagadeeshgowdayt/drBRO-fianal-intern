import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb

# Import the main 'script' class from your project's Script.py file
from Script import script 

# A unique prefix for buttons to avoid conflicts with other plugins
BUTTON_PREFIX = "topmovies_detail"

# Initialize IMDb
ia = IMDb()

# List of all the movies you want to feature
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]

@Client.on_message(filters.command("topmovies"))
async def list_movies_with_buttons(client: Client, message: Message):
    """
    Sends a list of movies, each with its own 'Show Details' button.
    """
    print(f"✅ /topmovies command received in chat {message.chat.id}")
    
    text = "🎬 **Here are the Top 10 Movies.**\n\nClick the button next to a movie to get its full details:"
    
    buttons = []
    for i, title in enumerate(MOVIE_LIST):
        button_text = f"Details for '{title}'"
        # Corrected callback_data format
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"{BUTTON_PREFIX}_{i}"
        )
        buttons.append([button])

    reply_markup = InlineKeyboardMarkup(buttons)
    # Always reply to the chat where the command was sent
    await client.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex(f"^{BUTTON_PREFIX}_"))
async def show_movie_details(client: Client, query: CallbackQuery):
    """
    Handles when a user clicks a 'Show Details' button.
    """
    await query.answer("Fetching details...", show_alert=False)
    
    # Always use the chat_id from the query's message
    chat_id = query.message.chat.id
    try:
        # --- CORRECTED: Parsing the movie index ---
        # "topmovies_detail_0" split by "_" -> ["topmovies", "detail", "0"]
        # The index is at position 2.
        movie_index = int(query.data.split("_")[2])
        movie_title = MOVIE_LIST[movie_index]

        print(f"✅ User {query.from_user.id} requested details for '{movie_title}' in chat {chat_id}")

        # --- Fetch movie details from IMDb ---
        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        if not search_results:
            await client.send_message(chat_id, f"Sorry, I couldn't find details for '{movie_title}'.")
            return

        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie)

        # --- Use the IMDB_TEMPLATE_TXT from your Script.py for the caption ---
        title = movie.get('title', 'N/A')
        genres = ', '.join(movie.get('genres', ['N/A']))
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        imdb_url = f"https://www.imdb.com/title/tt{movie.movieID}"

        # --- CORRECTED: Passing the correct object to .format() ---
        # The 'message' key in your template expects an object with a 'from_user.mention' attribute.
        # The 'query' object has this, so we pass it directly.
        caption = script.IMDB_TEMPLATE_TXT.format(
            url=imdb_url,
            title=title,
            genres=genres,
            year=year,
            rating=rating,
            remaining_seconds=0, 
            message=query 
        )

        # --- Send a new message with the movie details ---
        await client.send_photo(
            chat_id=chat_id,
            photo=movie.get('full-size cover url', 'https://placehold.co/600x900/1e293b/ffffff?text=Poster+Not+Found'),
            caption=caption,
            reply_to_message_id=query.message.id 
        )

    except Exception as e:
        print(f"❌ An error occurred in show_movie_details: {e}")
        await client.send_message(chat_id, "Sorry, an error occurred while fetching the details.")
