import discord
from discord.ext import commands
from . import config,chathistory
import re

# Define bot command prefix
intents = discord.Intents.default()
intents.message_content = True  # Enable message-related events

bot = commands.Bot(command_prefix="%", intents=intents)
channels = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm a bot. You can talk to me by mentioning me in a message.")

@bot.command()
async def clear(ctx):
    channels[ctx.channel.id] = chathistory.ChatHistory()
    await ctx.send("Chat history cleared.")

@bot.command()
async def history(ctx):
    if ctx.channel.id in channels:
        await ctx.send("\n".join([f"{a}: {b}" for a,b in channels[ctx.channel.id].messages]))
    else:
        await ctx.send("No chat history found for this channel.")

@bot.event
async def on_message(message:discord.Message):
    await commands.Bot.on_message(bot, message)  # Process commands
    assert bot.user
    if message.author == bot.user:
        return
    
    if message.channel.id not in channels:
        channels[message.channel.id] = chathistory.ChatHistory()
    chat_history = channels[message.channel.id]

    replied=False
    if message.reference and isinstance(message.reference.resolved,discord.Message) and message.reference.resolved.author.id == bot.user.id:
        replied=True
    username=message.author.name
    if isinstance(message.author, discord.Member) and message.author.nick:
        username = message.author.nick

    if f"<@{bot.user.id}>" in message.content or replied:
        # Bot was mentioned or replied to, respond to the message
        if config.ENABLE_TYPING:
            async with message.channel.typing():
                await respond(message,chat_history,username)
        else:
            await respond(message,chat_history,username)
    else:
        # User message, store in chat history
        chat_history.user_message(username,message.content)

async def respond(message:discord.Message,chat_history:chathistory.ChatHistory,username:str):
    ctxlen = 2048
    content=message.content
    src=re.search("[Cc]:([0-9]*)",content)
    if src:
        ctxlen = min(int(src.group(1)),4096)
        content = content.replace(src.group(0),"")
        
    ct = content.replace(f"<@{bot.user.id}>",config.BOT_NAME)

    chat_history.user_message(username, ct)
    replymessage = await chat_history.assistant_message(ctx=ctxlen)

    rln = replymessage.split("\n")
    msg = ""
    for line in rln:
        if len(msg)+len(line)>=2000: # Break on paragraphs if message is too long
            await message.reply(msg,mention_author=config.MENTION_AUTHOR)
            msg = ""
        if len(line)>2000:
            msg="Error: Paragraph is too long"
        else:
            msg+=line+"\n"
    await message.reply(msg,mention_author=config.MENTION_AUTHOR)

# Run the bot
bot.run(config.TOKEN)