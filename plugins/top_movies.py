# plugins/top_movies.py

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from imdb import IMDb

print("✅ GUARANTEED SOLUTION (top_movies.py) loaded.")

# --- DATA ---
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]

ia = IMDb()

# --- HANDLERS ---

@Client.on_message(filters.command("topmovies"))
async def list_top_movies_command(client: Client, message: Message):
    """
    Handles the /topmovies command by sending a numbered list.
    """
    print(f"✅ /topmovies command received in chat {message.chat.id}")
    
    # Create a formatted string with the numbered list of movies
    text = "🎬 **Here are your Top 10 Movies:**\n\n"
    for i, title in enumerate(MOVIE_LIST, 1):
        text += f"**{i}.** {title}\n"
    
    text += "\nTo get full details (including poster and rating), **just send the movie's number** (e.g., send `1`)."
    
    await message.reply_text(text, disable_web_page_preview=True)


@Client.on_message(filters.text & filters.private)
async def get_movie_details_by_number(client: Client, message: Message):
    """
    Handles when a user sends a number to get movie details.
    """
    # Check if the message text is a number between 1 and 10
    if not message.text.isdigit():
        return # Not a number, ignore
        
    number = int(message.text)
    if not (1 <= number <= len(MOVIE_LIST)):
        return # Number is out of range, ignore

    # The index in our list is the number minus 1
    movie_index = number - 1
    movie_title = MOVIE_LIST[movie_index]
    chat_id = message.chat.id
    
    print(f"✅ User wants details for movie #{number} ('{movie_title}') in chat {chat_id}")

    # Send a "thinking" message
    loading_msg = await message.reply_text(f"Searching for *{movie_title}*...", quote=True)

    try:
        # --- Asynchronously fetch movie details from IMDb ---
        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        if not search_results:
            await loading_msg.edit(f"Sorry, I couldn't find details for '{movie_title}'.")
            return

        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie)

        # --- Extract details ---
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

        # --- Send the details and delete the "loading" message ---
        await client.send_photo(
            chat_id=chat_id,
            photo=poster,
            caption=caption
        )
        await loading_msg.delete()

    except Exception as e:
        print(f"❌ ERROR fetching details: {e}")
        await loading_msg.edit("Sorry, an error occurred while getting the movie details.")
