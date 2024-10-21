import discord
from discord.ext import commands, tasks
import os
import asyncio
from itertools import cycle
import random
import requests
from bs4 import BeautifulSoup

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

bot_statuses = cycle([""])

#Will state in the terminal Kabook is online
@bot.event
async def on_ready():
    print("Kabooki Bot Online!")

#Response command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! I am Kabooki Bot! I was Developed by Aaron Singh to provide you with all your necessities from giving you encouragement and quizzing you for your class.")

#Says hello to user
@bot.command(aliases =["gm", "morning"])
async def goodmorning(ctx):
    await ctx.send(f"Good morning, {ctx.author.mention}! Have a good day!")

#Says good luck to user
@bot.command(aliases = ["gl", "luck1"])
async def goodluck1(ctx):
    await ctx.send(f"Good luck on your test, {ctx.author.mention}! CS1 is hard but I know you got this! Just think about the possibilities if you push through.")

# CS1 Questions for Midterm 
# Will add questions only on requests
quiz_data = {
    "(Question)": "(Answer)",
    "(Question)": "(Answer)",
    "(Question)": "(Answer)"
}

@bot.command()
async def quiz(ctx):
    questions = list(quiz_data.keys())
    random.shuffle(questions)
    index = 0

    await ctx.send(f"Question: {questions[index]}")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while index < len(questions):
        try:
            answer = await bot.wait_for('message', check=check, timeout=600)
            if answer.content.lower() == quiz_data[questions[index]].lower():
                await ctx.send("Correct!")
            else:
                await ctx.send(f"Incorrect. The correct answer was: {quiz_data[questions[index]]}")
            index += 1
            if index < len(questions):
                await ctx.send(f"Next question: {questions[index]}")
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer!")
            index += 1
            if index < len(questions):
                await ctx.send(f"Next question: {questions[index]}")

    await ctx.send(f"You have Completed the CS1 Midterm Review! Congrats {ctx.author.mention}!")
 
# Website Scraper Command
def get_price_from_website(url, css_selector):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        price_tag = soup.select_one(css_selector)
        if price_tag:
            return price_tag.get_text(strip=True)
        else:
            return "Price not found."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@bot.command()
async def best_price(ctx, *, item: str):
    # Graphics cards?
    urls = {
        "Newegg": "newegg product url",
        "Best Buy": "best buy product url",
        "Amazon": "amzon product url "
    }

    # Need to inspect element to find the selectors for product price !!! DONT FORGET
    selectors = {
        "Newegg": ".price-class-1",
        "Best Buy": ".price-class-2",
        "Amazon": ".price-class-3"
    }

    best_price = float('inf')
    best_site = None

    # This will loop through my provided URLs and start deciding out of my websites where I can get the best price
    for site, url in urls.items():
        css_selector = selectors.get(site)
        price_text = get_price_from_website(url, css_selector)
        try:
            price_value = float(price_text.replace('$', '').replace(',', ''))
            if price_value < best_price:
                best_price = price_value
                best_site = site
        except ValueError:
            await ctx.send(f"Could not convert price from {site}: {price_text}")

    if best_site:
        await ctx.send(f"The best price for {item} is ${best_price} on {best_site}.")
    else:
        await ctx.send(f"Could not find prices for {item}.")

with open("token.txt") as f:
    token = f.read()

bot.run(token)