from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import imdb_telegraph  # Corrected import style

# --- Caching for Performance ---
# This will hold the list of top movies to avoid fetching them repeatedly.
top_movies_cache = []
# This will track which movie each user is currently viewing.
user_movie_explorer = {}  # Format: {user_id: current_movie_index}

async def get_top_movies():
    """
    Fetches and caches the top 250 movies from IMDb.
    """
    global top_movies_cache
    if not top_movies_cache:
        try:
            # Use the corrected import style to call the top() method
            top_movies_cache = imdb_telegraph.poster.top()
        except Exception as e:
            print(f"Error fetching top movies: {e}")
            top_movies_cache = []
    return top_movies_cache

@Client.on_callback_query(filters.regex(r"^explore_"))
async def explore_movies_cb(client, query):
    """
    Handles callbacks for the movie explorer feature.
    """
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[1]

    movies = await get_top_movies()
    if not movies:
        await query.answer("Sorry, couldn't fetch movie data at the moment. Please try again later.", show_alert=True)
        return

    if action == "start":
        user_movie_explorer[user_id] = 0  # Start from the first movie
        await query.answer("Loading Top Rated Movies...")
    elif action == "next":
        current_index = user_movie_explorer.get(user_id, 0)
        user_movie_explorer[user_id] = (current_index + 1) % len(movies) # Loop back to start
    elif action == "select":
        current_index = user_movie_explorer.get(user_id, 0)
        movie_title = movies[current_index].get('title', 'Unknown Movie')
        
        # Send the movie name to the bot on behalf of the user
        await client.send_message(chat_id=user_id, text=movie_title)
        
        await query.answer(f"✅ Sent '{movie_title}' for searching!", show_alert=True)
        await query.message.delete()
        return

    # --- Display the current movie ---
    current_index = user_movie_explorer.get(user_id, 0)
    movie = movies[current_index]
    
    poster_url = movie.get('image', '')
    title = movie.get('title', '')
    rating = movie.get('rating', 'N/A')
    year = movie.get('year', 'N/A')
    
    caption = f"🎬 **{title}** ({year})\n\n⭐️ IMDb Rating: **{rating}** / 10"

    # --- Create Buttons ---
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Select This Movie", callback_data=f"explore_select"),
                InlineKeyboardButton("Next ➡️", callback_data=f"explore_next")
            ],
            [
                InlineKeyboardButton("✖️ Close", callback_data="close_data")
            ]
        ]
    )
    
    try:
        if query.message.photo and action != "start":
             # If the message already has a photo, edit it
            await query.message.edit_media(
                media={"type": "photo", "media": poster_url, "caption": caption},
                reply_markup=keyboard
            )
        else:
            # Otherwise, send a new photo message
            await query.message.reply_photo(
                photo=poster_url,
                caption=caption,
                reply_markup=keyboard
            )
            if action == "start":
                await query.message.delete() # delete the original message with the button
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

