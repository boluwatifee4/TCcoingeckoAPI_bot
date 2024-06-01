import os
import requests
import json
import schedule
import time
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables from .env file
load_dotenv()

# Retrieve tokens and chat ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

# Dictionary to store user preferences
user_preferences = {}

# Function to fetch data from CoinGecko API
def fetch_trending_data():
    url = "https://api.coingecko.com/api/v3/search/trending"
    
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": API_KEY
    }
    
    response = requests.get(url, headers=headers)
    
    coins = []
    nfts = []
    
    if response.status_code == 200:
        data = response.json()
        coins = data.get('coins', [])
        nfts = data.get('nfts', [])
        
    return coins, nfts

# Function to process trending coins
def process_trending_coins(coins):
    trending_coins = []
    for coin in coins:
        coin_info = coin['item']
        coin_item_data = coin_info['data']
        coin_detail = {
            "name": coin_info['name'],
            "symbol": coin_info['symbol'],
            "coin_id": coin_info['id'],
            "market_cap_rank": coin_info['market_cap_rank'],
            "market_cap_btc": coin_item_data['market_cap_btc'],
            "market_cap": coin_item_data['market_cap'],
            "total_volume": coin_item_data['total_volume'],
            "total_volume_btc": coin_item_data['total_volume_btc'],
            "spark_link": coin_item_data['sparkline'],
            "thumb_url": coin_info['small'] 
        }
        trending_coins.append(coin_detail)
    return trending_coins

# Function to process trending NFTs
def process_trending_nfts(nfts):
    trending_nfts = []
    for nft in nfts:
        nft_data = nft['data']
        nft_detail = {
            "name": nft['name'],
            "symbol": nft['symbol'],
            "nft_contract_id": nft['nft_contract_id'],
            "floor_price": nft_data['floor_price'],
            "floor_price_24h_percentage_change": nft_data['floor_price_in_usd_24h_percentage_change'],
            "h24_volume": nft_data['h24_volume'],
            "h24_average_sale_price": nft_data['h24_average_sale_price'],
            "spark_link": nft_data['sparkline'],
            "thumb_url": nft['thumb'] 
        }
        trending_nfts.append(nft_detail)
    return trending_nfts

# Function to format the coin message
def format_coin_message(username, coin):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message = f"GM {username}!\nTOP 15 TRENDING COINS ON COINGECKO ({timestamp})\n\n"
    # for i, coin in enumerate(coins[:15], start=1):
    # coin_info = coin['item']
    # coin_item_data = coin_info['data']
    message += f"💥 Name: {coin['name']}\n"
    message += f"   Symbol: {coin['symbol']}\n"
    message += f"   Coin ID: {coin['coin_id']}\n"
    message += f"   Market Cap Rank: {coin['market_cap_rank']}\n"
    message += f"   Market Cap BTC: {coin['market_cap_btc']}\n"
    message += f"   Market Cap: {coin['market_cap']}\n"
    message += f"   Total Volume: {coin['total_volume']}\n"
    message += f"   Total Volume BTC: {coin['total_volume_btc']}\n"
    message += f"   See more: {coin['spark_link']}\n\n"
    return message

# Function to format the NFT message
def format_nft_message(username, nft):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message = f"GM {username}!\nTOP TRENDING NFTS ({timestamp})\n\n"
    # for i, nft in enumerate(nfts[:15], start=1):
    message += f"💥 Name: {nft['name']}\n"
    message += f"   Symbol: {nft['symbol']}\n"
    message += f"   NFT Contract ID: {nft['nft_contract_id']}\n"
    message += f"   Floor Price: {nft['floor_price']}\n"
    message += f"   24h Floor Price Change: {nft['floor_price_24h_percentage_change']}%\n"
    message += f"   24h Volume: {nft['h24_volume']}\n"
    message += f"   24h Average Sale Price: {nft['h24_average_sale_price']}\n"
    message += f"   See more: {nft['spark_link']}\n\n"
    return message

# Function to send Coin message via Telegram
async def send_coin_message(context: ContextTypes.DEFAULT_TYPE):
    for user_id in user_preferences:
        coins, _ = fetch_trending_data()
        trending_coins = process_trending_coins(coins)
        if trending_coins:
            for coin in trending_coins:
                coin_message = format_coin_message(user_preferences[user_id], coin)
                await context.bot.send_photo(chat_id=user_id, photo=coin['thumb_url'], caption=coin_message)
            # message = format_coin_message(user_preferences[user_id], trending_coins)
            # await context.bot.send_photo(chat_id=user_id, photo=trending_coins['thumb_url'], caption=message)
        else:
            await context.bot.send_message(chat_id=user_id, text="Failed to fetch trending coins.")

# Function to send NFT message via Telegram
async def send_nft_message(context: ContextTypes.DEFAULT_TYPE):
    for user_id in user_preferences:
        _, nfts = fetch_trending_data()
        trending_nfts = process_trending_nfts(nfts)
        if trending_nfts:
            for nft in trending_nfts:
                nft_message = format_nft_message(user_preferences[user_id], nft)
                await context.bot.send_photo(chat_id=user_id, photo=nft['thumb_url'], caption=nft_message)
            # message = format_nft_message(user_preferences[user_id], trending_nfts)
            # await context.bot.send_photo(chat_id=user_id, photo=trending_nfts['thumb_url'], caption=message)
        else:
            await context.bot.send_message(chat_id=user_id, text="Failed to fetch trending NFTs.")

# Telegram bot setup
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_preferences:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello Chief! What would you like to be called?")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {user_preferences[user_id]}! I will send you updates twice a day.")
    await send_initial_messages(context, user_id)

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_preferences[user_id] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Got it! From now on, I will call you {update.message.text}. I will send you updates twice a day.")
    await send_initial_messages(context, user_id)

async def send_initial_messages(context: ContextTypes.DEFAULT_TYPE, user_id):
    await context.bot.send_message(chat_id=user_id, text=f"Fetching trending data ..")
    coins, nfts = fetch_trending_data()
    trending_coins = process_trending_coins(coins)
    trending_nfts = process_trending_nfts(nfts)
    await context.bot.send_message(chat_id=user_id, text=f"Fetched trending data !")

    if trending_coins:
         for coin in trending_coins:
             coin_message = format_coin_message(user_preferences[user_id], coin)
             await context.bot.send_photo(chat_id=user_id, photo=coin['thumb_url'], caption=coin_message)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Failed to fetch trending coins ")

    if trending_nfts:
        for nft in trending_nfts:
                nft_message = format_nft_message(user_preferences[user_id], nft)
                await context.bot.send_photo(chat_id=user_id, photo=nft['thumb_url'], caption=nft_message)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Failed to fetch trending NFTs ")

application = ApplicationBuilder().token(BOT_TOKEN).build()

start_handler = CommandHandler('start', start)
username_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), set_username)

application.add_handler(start_handler)
application.add_handler(username_handler)

application.run_polling()

# Schedule the function to fetch and send trending NFTs and coins at 7:31pm and 7:31am
schedule.every().day.at("22:59").do(send_coin_message)
schedule.every().day.at("23:15").do(send_nft_message)

while True:
    schedule.run_pending()
    time.sleep(1)