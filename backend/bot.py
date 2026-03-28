import discord
from discord import app_commands
from decouple import config
from agent import chat

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="ops", description="Run an nlops infrastructure command")
@app_commands.describe(query="What do you want to do?")
async def ops(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  
    response = await chat(query)
    await interaction.followup.send(response)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"logged in as {bot.user}")

bot.run(config("DISCORD_TOKEN"))
