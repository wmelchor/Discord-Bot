import json
import string
import discord

from discord.ext import commands
from discord.ext.commands import CommandNotFound
from yahoo_fin import stock_info as si
from yahoo_fin import news
from yahoo_fin.stock_info import get_quote_table, get_day_gainers, get_day_losers, get_day_most_active, get_income_statement, get_live_price
from yahoo_fin.options import get_calls, get_puts

#from ticker_info import *                           # Import files in directory.
from ticker_info import get_daily_info, get_RSI
from market_info import afterHours                  
from market_info import dateTime
from keep_alive import keep_alive

# Grab the prefix for the guild at bot launch.
def get_prefix(client, message):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)

        # Try to return the current prefix set for the guild, if we encounter any errors, we default the prefix to '$'
        try:
            return prefixes[str(message.guild.id)]
        except Exception as e:
            print("get_prefix exception for guild ID {}: {}".format(message.guild.id, e))
            return '$'

# Get the current prefix of the guild (already in json).
def get_current_prefix(ctx):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
        return prefixes.get(str(ctx.message.guild.id))

# Same function as above but takes a guild ID instead.
def get_current_prefix_two(guild_id):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
        return prefixes.get(str(guild_id))


# Use commands with the below prefix. That is commands will always use: '$' to activate
# 'client' is the bot's name.
# Prefix associated with each server as done above, default is '$'
client = commands.Bot(command_prefix = get_prefix)

# Remove the default help command
client.remove_command('help')

# ------------------------------------------ All client events are below -----------------------------------------------------#

# If a user types an invalid command (global handler, indiviudal command error handlers are below):
# 'ctx' means context the bot is ran under, needs to be in every command.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("That command doesn't exist! Type {}help or {}h for a list of available commands!".format(get_current_prefix(ctx), get_current_prefix(ctx)))
        return
    raise error

""" When the bot starts up, we want to make sure the guild key is already present in the json file.
    If not (in the literal only case where I invited the bot the server before writing this code), we add the guild id to the json file with the default prefix.
"""
@client.event
async def on_ready():
    print('Bot is ready!')                                  # Local message (in cmd/IDE) that the bot is running.
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)                             # Grab dictionary of guild IDs and prefixes.

        # Ensure there are no missing guilds in the json file, if there are, we add them with the default prefix '$'.
        for guild in client.guilds:

            # if the guild ID is not found as a key in the json, add it with default prefix.
            if(str(guild.id) not in prefixes.keys()):
                print(f"Missing guild found: {guild.id}")
                prefixes[guild.id] = '$'

            with open('guild_prefixes.json', 'w') as writer:
                json.dump(prefixes, writer, indent = 4)

    # Allows for a custom status, where name is "Listening to: {name}".
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Tendies"))

# Triggered when the bot is invited to a server, places the current guild ID in the json file & associated prefix.
@client.event
async def on_guild_join(guild):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)

        prefixes[str(guild.id)] = '$'                   # Set the default prefix to '$' when the bot is first invited to a server.

        with open('guild_prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)

# Triggered when the bot is kicked/removed/banned from a server. Removes the guild ID in the json file & associated prefix.
@client.event
async def on_guild_remove(guild):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))                         # Remove the associated guild ID from the json dict.

    with open('guild_prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)

# When you @ at bot, display the current prefix and a help message.
@client.event
async def on_message(message):
    if(str(client.user.id) in message.content):
        embedVar = discord.Embed(title = f"My prefix is: {get_current_prefix_two(message.guild.id)}\n-------------\nType {get_current_prefix_two(message.guild.id)}help to view a list of my commands!", description = "", color = 0xf508e9)
        await message.channel.send(embed = embedVar)
    await client.process_commands(message)                                              # Need this ensure that other commands still work after you @ the bot.

# ------------------------------------------ All of the bot commands are below -----------------------------------------------------#

# Help command to display all commands.
@client.command()
async def help(ctx):
    embedVar = discord.Embed(title = "List of Commands:", description = "Help page", color = 0xf508e9)
    embedVar.add_field(name = "quote/q", value = "Display various ticker information such as bid and ask price, last traded price, and volume.", inline = False)
    embedVar.add_field(name = "day_gainers/daygainers/dg/dayg", value = "Scrapes the top 74 stocks with the largest gains for the day.", inline = False)
    embedVar.add_field(name = "day_losers/dl/dayloser/dayl", value = "Scrapes the top 100 (at most) worst performing stocks (on the given trading day) from Yahoo Finance.", inline = False)
    embedVar.add_field(name = "day_most_active/dma/act/active/daymostactive", value = "Scrapes the top 100 most active stocks (on the given trading day) from Yahoo Finance.", inline = False)
    embedVar.add_field(name = "income_statement/inc/income/is/statement/state", value = "Scrapes the income statement for the input ticker, which includes information on Price/Sales and moving averages.", inline = False)
    embedVar.add_field(name = "price/p", value = "Gets live price for a given ticker.", inline = False)
    embedVar.add_field(name = "opening_price/op/o/open/open_price", value = "Gets opening price for a given ticker.", inline = False)
    embedVar.add_field(name = "high_price/high/h/hp/highprice/max", value = "Get high price for the day for a given ticker.", inline = False)
    embedVar.add_field(name = "low_price/low/l/lp/lowprice/min", value = "Get low price for the day for a given ticker.", inline = False)
    embedVar.add_field(name = "closing_price/close/c/cl/closeprice/closingprice", value = "Get closing price for the day for a given ticker.", inline = False)
    embedVar.add_field(name = "volume/vol/v", value = "Get the volume for the day for a given ticker.", inline = False)
    embedVar.add_field(name = "relative_strength_index/rsi", value = "Get the RSI for a given ticker.", inline = False)
    embedVar.add_field(name = "change_prefix/prefix/changeprefix", value = "Change the prefix for calling DieMand.", inline = False)
    embedVar.add_field(name = "showprefix", value = "Displays DieMand's current prefix.", inline = False)
    embedVar.add_field(name = "time", value = "Display market operating hours according to a given timezone.", inline = False)

    embedVar.add_field(name = "calls", value = "Displays call options for a given ticker.\nYou may optionally define an expiration date for call options after the ticker in the format of DD/MM/YYYY.", inline = False)
    embedVar.add_field(name = "puts", value = "Displays put options for a given ticker.\nYou may optionally define an expiration date for call options after the ticker in the format of DD/MM/YYYY.", inline = False)

    embedVar.add_field(name = "info", value = "Retrieves the Yahoo Finance news RSS feeds for a ticker.", inline = False)
    await ctx.send(embed = embedVar)

# Allow user to set the prefix for their server.
@client.command(aliases = ['prefix', 'changeprefix'])
async def change_prefix(ctx, prefix):
    with open('guild_prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)] = prefix

    with open('guild_prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent = 4)
    
    await ctx.send(f"My prefix is now: {prefix}")

# Error checking for the prefix command.
@change_prefix.error
async def change_prefix_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}[change_prefix, prefix, changeprefix] [new prefix]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Returns ticker "quote".
# NOTE: aliases are the other strings in which you can use to call this command in Discord.
@client.command(aliases = ['q'])
async def quote(ctx, ticker):
    format = "| # |        | Attribute |                           | Value |\n"
    separator = "| "
    text = si.get_quote_table(ticker, dict_result=False)
    lines = str(text)
    lines = lines.splitlines()
    finalText = ""
    i = 1
    while i < len(lines):
        words = lines[i].split()
        j = 0
        while j < len(words):
            if ord(str(words[0])[0:1]) > 47 and ord(str(words[0])[0:1]) < 58:
                number = int(words[0]) + 1
                words[0] = str(number)
            if j < 1:
                if (int(words[0])) + 1 > 10:
                    finalText = finalText + separator + str(words[j]) + " " + separator + "      |"
                else:
                    finalText = finalText + separator + str(words[j]) + " " + separator + "       |"
            elif j == len(words) - 1 and i != 1 and i != 2 and i != 3 and i!=5 and i != 6 and i != 7 and i != 8 and i != 9 and i != 10 and i != 11  and i != 12 and i != 17 and i != 13 and i != 14 and i != 15:
                finalText = finalText + " " + separator + "                        " + str(words[j]) + " "
            elif i == 1:
                if j == 4:
                    finalText = finalText + " " + separator + "                      " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 2:
                if j == 4:
                    finalText = finalText + " " + separator + "                      " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 3 or i == 6:
                if j == 2:
                    finalText = finalText + " " + separator + "                                " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 5:
                if j == 4:
                    finalText = finalText + " " + separator + "                  " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 7:
                if j == 3:
                    finalText = finalText + " " + separator + "                        " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 8:
                if j == 3:
                    finalText = finalText + " " + separator + "                          " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 9:
                if j == 3:
                    finalText = finalText + " " + separator + "                      " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 10:
                if j == 3:
                    finalText = finalText + " " + separator + "                   " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 11:
                if j == 5:
                    finalText = finalText + " " + separator + "           " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 12:
                if j == 3:
                    finalText = finalText + " " + separator + "                         " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 14:
                if j == 4:
                    finalText = finalText + " " + separator + "                     " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif i == 15:
                if j == 3:
                    finalText = finalText + " " + separator + "                     " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            elif j == len(words) - 1 and i == 13:
                finalText = finalText + " " + separator + "                               " + str(words[j]) + " "
            elif i == 17:
                if j == 2:
                    finalText = finalText + " " + separator + "                             " + str(words[j]) + " "
                else:
                    finalText = finalText + " " + str(words[j])
            else:
                finalText = finalText + " " + str(words[j])
            j = j + 1
        finalText = finalText + "\n"
        i = i + 1
    finalText = "```"  + format + finalText  + "```"
    await ctx.send(finalText)

# Error checking for the quote command.
@quote.error
async def quote_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}[quote, q] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Scrapes the top 100 (at most - we have 74 from discord, probably due to character limits) stocks with the largest gains for the day.
# NOTE: typing a ticker name after using this command does not break it, so any string after $dg etc... is not parsed.
@client.command(aliases = ['dg', 'daygainers', 'dayg'])
async def day_gainers(ctx):
    format1 = "+----------------------------------------------------------------------------+\n | # | Symbol |             Name             | MarCap  | PE Ratio |\n"
    format2 = "+----------------------------------------------------------------------------+\n | # | Symbol | PE Ratio |\n"
    endline = "+----------------------------------------------------------------------------+"
    linebreak = "\n"
    separator = " | "
    text = si.get_day_gainers()
    lines = str(text)
    lines = lines.splitlines()
    finalText = ""
    i = 1
    while i < len(lines) - 2:
        words = lines[i].split()
        j = 0
        while j < len(words):
            while j > 2 and j < (len(words) - 2):
                if str(words[j]) == "...":
                    break
                finalText = finalText + " " + str(words[j])
                j = j + 1
            if str(words[j]) == "...":
                j = j + 1
                continue
            if ord(str(words[0])[0:1]) > 47 and ord(str(words[0])[0:1]) < 58:
                number = int(words[0]) + 1
                words[0] = str(number)
            finalText = finalText + separator + str(words[j])
            j = j + 1
        finalText = finalText + linebreak
        i = i + 1
    words = lines[3].split()
    if len(words) < 5:
        finalText = "```" + linebreak + format2 + finalText + endline + "```"
    else:
        finalText = "```" + linebreak + format1 + finalText + endline + "```"
    await ctx.send(finalText)

# Scrapes the top 100 (at most) worst performing stocks (on the given trading day) from Yahoo Finance.
# NOTE: typing a ticker name after using this command does not break it, so any string after $dl etc... is not parsed.
@client.command(aliases = ['dl', 'daylosers', 'dayl'])
async def day_losers(ctx):
    format1 = "+----------------------------------------------------------------------------+\n | # | Symbol |        Name        | MarCap  | PE Ratio |\n"
    format2 = "+----------------------------------------------------------------------------+\n | # | Symbol | PE Ratio |\n"
    endLine = "+----------------------------------------------------------------------------+"
    linebreak = "\n"
    separator = " | "
    text = si.get_day_losers()
    lines = str(text)
    lines = lines.splitlines()
    finalText = ""
    i = 1
    while i < len(lines) - 2:
        words = lines[i].split()
        j = 0
        while j < len(words):
            while j > 2 and j < (len(words) - 2):
                if str(words[j]) == "...":
                    break
                finalText = finalText + " " + str(words[j])
                j = j + 1
            if str(words[j]) == "...":
                j = j + 1
                continue
            if ord(str(words[0])[0:1]) > 47 and ord(str(words[0])[0:1]) < 58:
                number = int(words[0]) + 1
                words[0] = str(number)
            finalText = finalText + separator + str(words[j])
            j = j + 1
        finalText = finalText + linebreak
        i = i + 1
    words = lines[3].split()
    if len(words) < 5:
        finalText = "```" + linebreak + format2 + finalText + endLine + "```"
    else:
        finalText = "```" + linebreak + format1 + finalText + endLine + "```"
    await ctx.send(finalText)

# Scrapes the top 100 most active stocks (on the given trading day) from Yahoo Finance.
@client.command(aliases = ['dma', 'act', 'active', 'daymostactive'])
async def day_most_active(ctx):
    format1 = "+----------------------------------------------------------------------------+\n | # | Symbol |             Name             | MarCap  | PE Ratio |\n"
    format2 = "+----------------------------------------------------------------------------+\n | # | Symbol | PE Ratio |\n"
    endLine = "+----------------------------------------------------------------------------+"
    linebreak = "\n"
    separator = " | "
    text = si.get_day_most_active()
    lines = str(text)
    lines = lines.splitlines()
    finalText = ""
    i = 1
    while i < len(lines) - 2:
        words = lines[i].split()
        j = 0
        while j < len(words):
            while j > 2 and j < (len(words) - 2):
                if str(words[j]) == "...":
                    break
                finalText = finalText + " " + str(words[j])
                j = j + 1
            if str(words[j]) == "...":
                j = j + 1
                continue
            if ord(str(words[0])[0:1]) > 47 and ord(str(words[0])[0:1]) < 58:
                number = int(words[0]) + 1
                words[0] = str(number)
            finalText = finalText + separator + str(words[j])
            j = j + 1
        finalText = finalText + linebreak
        i = i + 1
    words = lines[3].split()
    if len(words) < 5:
        finalText = "```" + linebreak + format2 + finalText + endLine + "```"
    else:
        finalText = "```" + linebreak + format1 + finalText + endLine + "```"
    await ctx.send(finalText)

# Scrapes the income statement for the input ticker, which includes information on Price / Sales, P/E, and moving averages.
# NOTE: A better alternative might be to use get_financials, which combines three different functions.
@client.command(aliases = ['inc', 'income', 'is', 'statement', 'state'])
async def income_statement(ctx, ticker):
    linebreak = "\n"
    separator = " | "
    text = si.get_income_statement(ticker)
    lines = str(text)
    lines = lines.splitlines()
    firstLine = lines[0].split()
    format = "+----------------------------------------------------------------------------+\n |        Item       " + " | " + \
             firstLine[1] + " | " + firstLine[3] + "\n"
    endLine = "+----------------------------------------------------------------------------+"
    finalText = ""
    i = 2
    while i < len(lines) - 2:
        words = lines[i].split()
        j = 0
        while j < len(words):
            while j > 2 and j < (len(words) - 2):
                if str(words[j]) == "...":
                    break
                finalText = finalText + " " + str(words[j])
                j = j + 1
            if str(words[j]) == "...":
                j = j + 1
                continue
            # if i == 2 and j > 0:
            # finalText = finalText + separator + "       " + str(words[j]) + "     " + separator
            else:
                finalText = finalText + separator + str(words[j])
            j = j + 1
        finalText = finalText + linebreak
        i = i + 1
    finalText = "```" + linebreak + format + finalText + endLine + "```"
    await ctx.send(finalText)

# Error checking for the income_statement command.
@income_statement.error
async def income_statement_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['income_statement', 'inc', 'income', 'is', 'statement', 'state'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Gets live price for a given ticker.
@client.command(aliases = ['p'])
async def price(ctx, ticker):
    live_price = si.get_live_price(ticker)
    embedVar = discord.Embed(title = ticker.upper(), description = '${:0.3f}'.format(live_price), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the price command.
@price.error
async def price_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['price', 'p'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Gets opening price for a given ticker.
@client.command(aliases = ['op', 'o', 'open', 'open_price'])
async def opening_price(ctx, ticker):
    
    # Retrieve information using function in ticker_info.py.
    open_price = get_daily_info(ticker, 'open')
    embedVar = discord.Embed(title = '{} opening price:'.format(ticker.upper()), description = '${:0.3f}'.format(open_price), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the opening_price command.
@opening_price.error
async def opening_price_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['opening_price', 'op', 'o', 'open', 'open_price'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get high price for the day for a given ticker.
@client.command(aliases = ['high', 'h', 'hp', 'highprice', 'max'])
async def high_price(ctx, ticker):

    # Retrieve information using function in ticker_info.py.
    high_price = get_daily_info(ticker, 'high')
    embedVar = discord.Embed(title = '{} high price:'.format(ticker.upper()), description = '${:0.3f}'.format(high_price), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the high_price command.
@high_price.error
async def high_price_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['high_price', 'high', 'h', 'hp', 'highprice', 'max'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get low price for the day for a given ticker.
@client.command(aliases = ['low', 'l', 'lp', 'lowprice', 'min'])
async def low_price(ctx, ticker):

    # Retrieve information using function in ticker_info.py.
    low_price = get_daily_info(ticker, 'low')
    embedVar = discord.Embed(title = '{} low price:'.format(ticker.upper()), description = '${:0.3f}'.format(low_price), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the high_price command.
@low_price.error
async def low_price_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['low_price', 'low', 'l', 'lp', 'lowprice', 'min'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get closing price for the day for a given ticker.
@client.command(aliases = ['close', 'c', 'cl', 'closeprice', 'closingprice'])
async def closing_price(ctx, ticker):

    # Retrieve information using function in ticker_info.py.
    closing_price = get_daily_info(ticker, 'close')
    embedVar = discord.Embed(title = '{} closing price:'.format(ticker.upper()), description = '${:0.3f}'.format(closing_price), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the closing_price command.
@closing_price.error
async def closing_price_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['closing_price', 'close', 'c', 'cl', 'closeprice', 'closingprice'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get the volume for the day for a given ticker.
@client.command(aliases = ['vol', 'v'])
async def volume(ctx, ticker):

    # Retrieve information using function in ticker_info.py.
    volume = get_daily_info(ticker, 'volume')
    embedVar = discord.Embed(title = '{} volume:'.format(ticker.upper()), description = '{}'.format(int(volume)), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the volume command.
@volume.error
async def volume_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['volume', 'vol', 'v'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get the RSI for a given ticker.
@client.command(aliases = ['rsi'])
async def relative_strength_index(ctx, ticker):

    # Retrieve information using function in ticker_info.py.
    # Source: https://www.investopedia.com/terms/r/rsi.asp
    rsi = get_RSI(ticker)
    if(rsi <= 30.0000):
        embedVar = discord.Embed(title = '{} RSI:'.format(ticker.upper()), description = '{}% - This security may be oversold.'.format(rsi), color = 0xffa500)
    elif(rsi >= 70.0000):
        embedVar = discord.Embed(title = '{} RSI:'.format(ticker.upper()), description = '{}% - This security may be overbought.'.format(rsi), color = 0xffa500)
    embedVar = discord.Embed(title = '{} RSI:'.format(ticker.upper()), description = '{}%'.format(rsi), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the RSI command.
@relative_strength_index.error
async def relative_strength_index_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['relative_strength_index', 'rsi'] [ticker_name]", color = 0xffa500)
        await ctx.send(embed = embedVar)
    
# Time-related content pertaining to the market.
@client.command()
async def time(ctx,tz):
    embedVar = discord.Embed(title = dateTime(tz), description = afterHours(), color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the time command.
@time.error
async def time_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['time'] [timezone]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Get news for a given ticker.
@client.command()
async def info(ctx, ticker):
    embedVar = discord.Embed(title = f'{ticker.upper()} Yahoo Finance news: ', description = f'{news.get_yf_rss(ticker)}', color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the time command.
@info.error
async def info_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['info'] [ticker]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# ------------------------------------------ Commands for options below -----------------------------------------------------#

# Call options for a ticker.
@client.command()
async def calls(ctx, ticker, date = None):
    embedVar = discord.Embed(title = f"{ticker.upper()}'s Call options: ", description = f"{get_calls(ticker, date)}", color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the calls command.
@calls.error
async def calls_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['calls'] [ticker] [OPTIONAL DD/MM/YYYY]", color = 0xffa500)
        await ctx.send(embed = embedVar)

# Put options for a ticker.
@client.command()
async def puts(ctx, ticker, date = None):
    embedVar = discord.Embed(title = f"{ticker.upper()}'s Put options: ", description = f"{get_puts(ticker, date)}", color = 0xffa500)
    await ctx.send(embed = embedVar)

# Error checking for the calls command.
@puts.error
async def puts_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, commands.errors.CommandInvokeError):
        embedVar = discord.Embed(title = "Invalid command use!", description = f"Proper command use: {get_current_prefix(ctx)}['puts'] [ticker] [OPTIONAL DD/MM/YYYY]", color = 0xffa500)
        await ctx.send(embed = embedVar)
 
# Keeping the bot alive by pinging the server every 5 minutes
keep_alive()

# TODO: MAKE SURE YOU PUT YOUR TOKEN HERE.
client.run('YOUR BOT TOKEN HERE')
