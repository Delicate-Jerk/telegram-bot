from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import string
import time
import threading
import random
from flask import Flask, request, jsonify
import secrets

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")
REFERAL_POST_API = os.getenv("REFERAL_POST_API")
TEMPLATE = os.getenv("TEMPLATE")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

app = Flask(__name__)

generated_strings = {}

async def send_referral_to_api(username, referral_code, userId):
    url = REFERAL_POST_API
    payload = {
        "userId": str(userId),
        "referralCode": referral_code
    }
    headers = {'Content-Type': 'application/json'}
    # Creating a session with disabled SSL verification
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    print("\033[92mReferral data sent successfully\033[0m")
                else:
                    response_text = await response.text()
                    print(f"\033[91mFailed to send referral data: {response_text}\033[0m")
        except Exception as e:
            print(f"\033[91mError when sending referral data: {str(e)}\033[0m")

def remove_expired_string(string):
    time.sleep(10)
    if string in generated_strings:
        del generated_strings[string]

@app.route('/generate', methods=['GET'])
def generate_string():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    timestamp = time.time()
    generated_strings[random_string] = timestamp
    
    # Start a thread to remove the string after 10 seconds
    threading.Thread(target=remove_expired_string, args=(random_string,)).start()
    
    return jsonify({
        'status': 'success',
        'message': 'Token generated successfully.',
        'data': {
            'generated_token': random_string,
            'validity_duration': '10 seconds'
        }
    })

@app.route('/send_message', methods=['POST'])
async def send_message_to_user():
    data = request.json
    user_id = data.get('user_id')
    user_message = data.get('message')
    user_string = data.get('token')
    current_time = time.time()

    if not user_id or not user_message or not user_string:
        return jsonify({"error": "user_id, message, and string are required"}), 400

    if user_string in generated_strings:
        if current_time - generated_strings[user_string] <= 10:
            try:
                await bot.send_message(user_id, user_message)
                return jsonify({"success": True}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"status": "error", "message": "String is not valid. Time expired."}), 400
    else:
        return jsonify({"status": "error", "message": "String is not valid."}), 400

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.is_bot:
        await message.reply("Sorry, bots are not allowed to access the game.")
        return

    user_id = message.from_user.id
    username = message.from_user.username
    args = message.get_args()
    button_url = f"{BASE_URL}?user_id={user_id}&referral_code={args}"

    if args:
        welcome_text = f"Hi {message.from_user.first_name}, you joined using the referral code: {args}."
        print(f"Referral code received: \033[92m{args}\033[0m - Username: \033[92m{username}\033[0m - UserId: \033[92m{user_id}\033[0m")
        # Send referral info to API asynchronously
        asyncio.create_task(send_referral_to_api(message.from_user.username, args, message.from_user.id))
    else:
        welcome_text = f"Hi {message.from_user.first_name}, welcome to the bot! You did not use a referral code."
        print(f"No referral code - User: {message.from_user.username} (ID: {user_id})")

    title = "Welcome to 5ire Gaming World!"
    description = "This is a fun and exciting game. Click the button below to start playing."
    button = InlineKeyboardButton(text="Play Game", url=button_url)
    button_greet = InlineKeyboardButton(text="Help", callback_data="say_hello")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(button)
    keyboard.add(button_greet)

    await message.answer_photo(
        photo=TEMPLATE,
        caption=f"{title}\n\n{description}",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'say_hello')
async def process_callback_button1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, """
    Game (Home Screen):
    * Music: ON/OFF the bubble sound
    * Refer and Earn: Get your referral link once your wallet is connected with the game
    * My reward: Connect your wallet and view list of all your game earnings
    * Leaderboard: See the list of users climbing the board by scoring high and earn rewards
    * Rewards: See list of rewards that can be earned through game
    * Play
    * Connect with Wallet: Enter the name (optional) and wallet address 
    * Connect with Metamask:
        * Click on this option, redirects user to the metamask application
        * Connect your wallet to the game and user is redirected back to the game and start popping the bubbles 
    In-game 
    * Game wallet: If Wallet is connected then the 5ire icon is shown. Click on 5ire icon to view
    * User wallet address with copy button
    * Transaction history with ‘i’ icon is shown on clicking it a detail page with transaction hash will open
    * Disconnect: Disconnect your wallet from the game
    * My Score: See the scores earned by popping the bubbles
    * 5ire Tokens: See 5ire token earnings through the game
        * On every 1000 score, get 1 5ire token 
        * Every referral joined, will provide with an earning of 5ire tokens
    * My Referral : See the number of users who joined the game through your referral.
    * Referral bonus: See the bonus earned from referring friends. ‘Claim’ it to get credited to your wallet connected 
    * Pause: Click on Pause icon, user get two options - Resume and Home
    * Resume: On Click of Resume button, game will be resumed again
    * Home: On click of Home User Redirects on Home page
    IDLE TIME: If user is not Playing the game for 1 hour then 5% of the scores is deducted
    Session: No need to connect your wallet again and again (for 2 hours). Just simply click the Play button and continue playing. 
    Game Rewards (Lootbox):
    * Users on the top 100 list of leaderboard will get a chance to win exclusive rewards from the lootbox earned during gameplay such as:
    * iPhone
    * Mac
    * Score multipliers
    * 5ire Merch packs 
    * Exclusive access to 5ire programs and much more
                                                    """)

def start_flask_app():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    from multiprocessing import Process

    flask_process = Process(target=start_flask_app)
    flask_process.start()

    executor.start_polling(dp, skip_updates=True)

    flask_process.join()
