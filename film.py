import os
import requests
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8648156756:AAE2TILU0NwnF8zn7ap06MfUPhukJBjBtYA")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "57790011db603d03ea8dc41743499835")

# Жанры с эмодзи
GENRES = {
    "😂 Комедия": 35,
    "😱 Ужасы": 27,
    "🚀 Фантастика": 878,
    "🔫 Боевик": 28
}

# Настроение с эмодзи
MOODS = {
    "😊 Весёлое": ["😂 Комедия"],
    "😢 Грустное": ["😱 Ужасы", "🔫 Боевик"],
    "😨 Напряжённое": ["🚀 Фантастика", "🔫 Боевик"]
}

def get_movie(genre_name=None, mood=None, min_rating=6.8):
    genre_id = None
    if genre_name:
        genre_id = GENRES.get(genre_name)
    elif mood:
        mood_genres = MOODS.get(mood, [])
        if mood_genres:
            genre_id = GENRES.get(mood_genres[0])
    page = random.randint(1, 30)
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&vote_average.gte={min_rating}&language=ru-RU&page={page}"
    if genre_id:
        url += f"&with_genres={genre_id}"
    response = requests.get(url)
    data = response.json()
    movies = data.get("results", [])
    if not movies:
        return None, None
    movie = random.choice(movies)
    poster = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None
    text = f"🎬 {movie['title']}\n⭐ Рейтинг: {movie['vote_average']}\n\n{movie['overview']}"
    return text, poster

# Старт бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Клавиатура всегда снизу
    keyboard = [
        [KeyboardButton(genre) for genre in GENRES],  # все жанры в одном ряду
        [KeyboardButton(mood) for mood in MOODS],    # все настроения в другом ряду
        [KeyboardButton("🎲 Случайный фильм")]        # отдельная кнопка случайного фильма
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🍿 Привет! Выбирай жанр, настроение или случайный фильм 👇",
        reply_markup=reply_markup
    )

# Обработка нажатий на кнопки
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in GENRES:
        movie, poster = get_movie(genre_name=text)
    elif text in MOODS:
        movie, poster = get_movie(mood=text)
    elif text == "🎲 Случайный фильм":
        movie, poster = get_movie()
    else:
        movie, poster = get_movie()
    if poster:
        await update.message.reply_photo(photo=poster, caption=movie)
    else:
        await update.message.reply_text(movie)

# Запуск
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен 🚀")
    app.run_polling()

main()
