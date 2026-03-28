import discord
import asyncio
from discord import app_commands
from decouple import config
from agent import agent_chat
from tools.ssh_tools import _ssh

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

async def update_status():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            cpu = _ssh("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
            ram = _ssh("free | awk '/Mem:/ {printf \"%.0f\", $3/$2 * 100}'")
            disk = _ssh("df / | awk 'NR==2 {print $5}'")
            status = f"CPU {cpu}% · RAM {ram}% · Disk {disk}"
        except Exception:
            status = "stats unavailable"

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=status
            )
        )
        await asyncio.sleep(30)

@tree.command(name="ops", description="Run an nlops infrastructure command")
@app_commands.describe(query="What do you want to do?")
async def ops(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  
    response = await agent_chat(query)
    await interaction.followup.send(response)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"logged in as {bot.user}")
    asyncio.create_task(update_status())

bot.run(config("DISCORD_TOKEN"))
