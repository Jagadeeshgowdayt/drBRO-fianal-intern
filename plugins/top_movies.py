# plugins/top_movies.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import MessageNotModified
from imdb import IMDb
import asyncio

print("✅ DEBUG: NEW_SOLUTION (top_movies.py) loaded.")

# --- DATA ---
# Using a dictionary to store the user's current movie index
# Format: {user_id: movie_index}
user_movie_state = {}

# Your custom list of top movies
MOVIE_LIST = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight",
    "The Godfather Part II", "12 Angry Men", "Schindler's List",
    "The Lord of the Rings: The Return of the King", "Pulp Fiction",
    "The Good, the Bad and the Ugly", "Forrest Gump"
]

# IMDbPY instance
ia = IMDb()

# --- HANDLERS ---

@Client.on_message(filters.command("topmovies"))
async def start_top_movies_command(client, message):
    """Entry point when a user sends /topmovies."""
    print(f"✅ DEBUG: /topmovies received from user {message.from_user.id}")
    # Set the user's starting position to the first movie (index 0)
    user_id = message.from_user.id
    user_movie_state[user_id] = 0

    # Show the first movie
    await display_movie(client, user_id, message_to_edit=None)


@Client.on_callback_query(filters.regex("^(next_movie|prev_movie|close_movies)$"))
async def navigate_movies_callback(client, query: CallbackQuery):
    """Handles all button presses for this feature."""
    user_id = query.from_user.id
    action = query.data

    print(f"✅ DEBUG: Button '{action}' pressed by user {user_id}")

    # Immediately acknowledge the button press
    await query.answer()

    if action == "close_movies":
        # Remove user's state and delete the message
        if user_id in user_movie_state:
            del user_movie_state[user_id]
        await query.message.delete()
        print(f"✅ DEBUG: Closed menu for user {user_id}")
        return

    # Check if we have a state for this user
    if user_id not in user_movie_state:
        # If not, maybe the bot restarted. Start them from the beginning.
        user_movie_state[user_id] = 0
    else:
        # Update the user's movie index based on the action
        if action == "next_movie":
            user_movie_state[user_id] += 1
        elif action == "prev_movie":
            user_movie_state[user_id] -= 1

    # Display the updated movie, editing the existing message
    await display_movie(client, user_id, message_to_edit=query.message)


# --- CORE LOGIC ---

async def display_movie(client, user_id, message_to_edit=None):
    """The main function to fetch and display a movie."""
    current_index = user_movie_state.get(user_id, 0)
    movie_title = MOVIE_LIST[current_index]

    print(f"✅ DEBUG: Displaying movie '{movie_title}' (index {current_index}) for user {user_id}")

    try:
        # --- Fetch movie details from IMDb ---
        loop = asyncio.get_running_loop()
        # Search for the movie and get its full details
        search_results = await loop.run_in_executor(None, ia.search_movie, movie_title)
        if not search_results:
            await client.send_message(user_id, f"Could not find details for '{movie_title}'.")
            return

        movie = search_results[0]
        await loop.run_in_executor(None, ia.update, movie) # Fetch full details

        # --- Extract details ---
        poster = movie.get('full-size cover url', 'https://i.imgur.com/B1YTE4p.jpg')
        title = movie.get('title', 'N/A')
        year = movie.get('year', 'N/A')
        rating = movie.get('rating', 'N/A')
        language = movie.get('languages', ['N/A'])[0]
        plot = movie.get('plot outline', 'No plot summary available.')

        # --- Prepare message content ---
        caption = (
            f"**🎬 Title:** {title} ({year})\n\n"
            f"**⭐ Rating:** {rating} / 10\n"
            f"**🗣️ Language:** {language}\n\n"
            f"**📜 Plot:** {plot}"
        )

        # --- Prepare navigation buttons ---
        buttons = []
        row = []
        # Show "Previous" button if not the first movie
        if current_index > 0:
            row.append(InlineKeyboardButton('⬅️ Previous', callback_data="prev_movie"))
        # Show "Next" button if not the last movie
        if current_index < len(MOVIE_LIST) - 1:
            row.append(InlineKeyboardButton('Next ➡️', callback_data="next_movie"))
        buttons.append(row)
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_movies")])
        reply_markup = InlineKeyboardMarkup(buttons)

        # --- Send or Edit the message ---
        if message_to_edit:
            await message_to_edit.edit_media(
                media=poster,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            # This happens only the first time (/topmovies command)
            await client.send_photo(
                chat_id=user_id,
                photo=poster,
                caption=caption,
                reply_markup=reply_markup
            )
        print(f"✅ DEBUG: Successfully displayed movie for user {user_id}")

    except MessageNotModified:
        # User clicked the same button twice fast. This is normal.
        print(f"⚠️ DEBUG: MessageNotModified for user {user_id}. Ignoring.")
    except Exception as e:
        print(f"❌ ERROR: An error occurred in display_movie for user {user_id}: {e}")
