import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext

token = os.getenv("BOT_TOKEN")

# Define the start command handler
def start(update: Update, context: CallbackContext) -> None:
    # Define the title, description, and button
    title = "Welcome to Antier Platform!"
    description = "This is a fun and exciting game. Click the button below to start playing."
    button = InlineKeyboardButton(text="Play Game", url="")
    
    # Define the image URL or path
    image_url = "https://stage-chatbot-frontend.s3.amazonaws.com/bot_icons/template.jpg"  # Replace with your image URL

    # Create a keyboard with the button
    keyboard = InlineKeyboardMarkup([[button]])

    # Send the image with the title and description
    update.message.reply_photo(photo=image_url, caption=f"{title}\n\n{description}", reply_markup=keyboard)

print("\033[92mServer Started\033[0m")


def main():
    updater = Updater(token)
    
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

