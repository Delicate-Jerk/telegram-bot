# basic script to interact with a telegram bot using aiogram, sends userid and ref if any when user joins a channel
# and starts a web app game when clicked on play game.

from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Your bot token from BotFather
API_TOKEN = ''

# Initialize the bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    # Extract the parameter from the start command
    args = message.get_args()
    
    if args:
        welcome_text = f"Hi {message.from_user.first_name}, you joined using the referral code: {args}."
        print(f"Referral code received: {args} - User: {message.from_user.username} (ID: {message.from_user.id})")
    else:
        welcome_text = f"Hi {message.from_user.first_name}, welcome to the bot! You did not use a referral code."
        print(f"No referral code - User: {message.from_user.username} (ID: {message.from_user.id})")

    # Define the title, description, and button
    title = "Welcome to Antier Platform!"
    description = "This is a fun and exciting game. Click the button below to start playing."
    button_url = "https://t.me/gameantierbot"  # Modify this URL to your game link
    button = InlineKeyboardButton(text="Play Game", url=button_url)
    keyboard = InlineKeyboardMarkup().add(button)

    # Send the message with the button
    await message.answer_photo(
        photo="https://stage-chatbot-frontend.s3.amazonaws.com/bot_icons/template.jpg",
        caption=f"{title}\n\n{description}",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp, skip_updates=True)