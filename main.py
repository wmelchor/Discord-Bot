import discord
import os
import iexfinance
import requests_html
from market_info import afterHours
from market_info import dateTime
from keep_alive import keep_alive
from discord.ext import commands
from datetime import datetime
from yahoo_fin import stock_info as si #need to import yahoo_fin and discord modules
from yahoo_fin.stock_info import *
import requests

#bot will look for '$' to activate
#also, 'client' is the bot's name
client = commands.Bot(command_prefix = '$')


#turns on bot in chat
@client.event
async def on_ready():
    print('bot is ready') 



# all of the bot commands are below
@client.command()  #a bot command, 'ticker' is user input
async def quote(ctx, ticker):
    await ctx.send(si.get_quote_table(ticker, dict_result = False))

@client.command()
async def time(ctx,tz):
    await ctx.send(dateTime(tz))
    await ctx.send(afterHours())

@client.command()
async def day_gainers(ctx):
    await ctx.send(si.get_day_gainers())


@client.command()
async def day_losers(ctx):
    await ctx.send(si.get_day_losers())


@client.command() 
async def day_most_active(ctx): #'ctx' means context the bot is run under, needs to be in every command
    await ctx.send(si.get_day_most_active())


@client.command()
async def income_statement(ctx,ticker): #'ticker' is variable that user puts in after '$'
    await ctx.send(si.get_income_statement(ticker))

#gets live price for ticker
@client.command()
async def price(ctx, ticker):
    await ctx.send(si.get_live_price(ticker))

# Hooking with Amy's code 
@client.command() 
# *user to take in as a list
async def register_user(ctx, *user_data):
  # routes/users.js line 40->47 for route /reg
  url = "https://discord-bot-cs321-grp13.herokuapp.com/reg"
  user = {
    'name': user_data[0],
    'id': user_data[1]
    }
  response = requests.post(url, data = user)
  await ctx.send(response)

#token identifier is for the bot, txt me for what it is bc its supposed to be secret
#keeping the bot alive by pinging the server every 5 minutes
keep_alive()
token = os.environ.get("TOKEN")
client.run(token)

#thats it. it's really that easy.

