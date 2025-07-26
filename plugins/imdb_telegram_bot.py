from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# IMDb Top 10 data
movies = [
    {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "poster": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIwLTliZjMtY2NhYzU3ZTZjODBhXkEyXkFqcGdeQXVyNDYyMDk5MTU@._V1_.jpg",
        "rating": 9.3,
        "snippet": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
    },
    {
        "title": "The Godfather",
        "year": 1972,
        "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmYtYTAwYy00ZjQ5LWFmNTEtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 9.2,
        "snippet": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."
    },
    {
        "title": "The Dark Knight",
        "year": 2008,
        "poster": "https://m.media-amazon.com/images/M/MV5BN2EyZjM3NzItYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 9.0,
        "snippet": "When the menace known as the Joker emerges from his mysterious past, he wreaks havoc and chaos on the people of Gotham."
    },
    {
        "title": "The Godfather Part II",
        "year": 1974,
        "poster": "https://m.media-amazon.com/images/M/MV5BMWMwMGYzNmYtYTAwMC00ZjQ5LWIwN2YtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 9.0,
        "snippet": "The early life and career of Vito Corleone in 1920s New York is portrayed while his son expands and tightens his grip on the family crime syndicate."
    },
    {
        "title": "12 Angry Men",
        "year": 1957,
        "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmYtYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 9.0,
        "snippet": "A jury holdout attempts to prevent a miscarriage of justice by forcing his colleagues to reconsider the evidence."
    },
    {
        "title": "Schindler's List",
        "year": 1993,
        "poster": "https://m.media-amazon.com/images/M/MV5BZmE2ZjQyNmYtYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 8.9,
        "snippet": "In German-occupied Poland during WWII, Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis."
    },
    {
        "title": "The Lord of the Rings: The Return of the King",
        "year": 2003,
        "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDAtYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 8.9,
        "snippet": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring."
    },
    {
        "title": "Pulp Fiction",
        "year": 1994,
        "poster": "https://m.media-amazon.com/images/M/MV5BMTk4OGQzMjAtYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 8.9,
        "snippet": "The lives of two mob hitmen, a boxer, a gangster's wife, and a pair of diner bandits intertwine in four tales of violence and redemption."
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "year": 2001,
        "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDAtYTAwMC00ZjQ5LTk0ZGMtODM1ZmRlYzNmZWFjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "rating": 8.8,
        "snippet": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth."
    }
]

def start(update: Update, context: CallbackContext):
    return send_movie(update, context, 0)

def send_movie(update: Update, context: CallbackContext, idx=0):
    movie = movies[idx]
    caption = f"{movie['title']} ({movie['year']})\nIMDb Rating: {movie['rating']}\n\n{movie['snippet']}"
    keyboard = [[InlineKeyboardButton("Next ▶️", callback_data=f"next_{(idx+1)%len(movies)}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        update.callback_query.edit_message_media(
            InputMediaPhoto(media=movie['poster'], caption=caption),
            reply_markup=reply_markup
        )
    else:
        update.message.reply_photo(photo=movie['poster'], caption=caption, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    idx = int(query.data.split("_")[1])
    send_movie(update, context, idx)

def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
