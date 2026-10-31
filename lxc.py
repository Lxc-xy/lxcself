import asyncio
import discord
from discord.ext import commands
import os
import requests
import time

token = "Yourmom"
lxc = commands.Bot(command_prefix="!", self_bot=True, help_command=None)

active_tasks = {}
name_tasks = {}

@lxc.event
async def on_ready():
    print(f"Logged in as {lxc.user} (ID: {lxc.user.id})")

@lxc.command()
async def ping(ctx):
    await ctx.message.delete()
    latency = round(lxc.ws.latency * 1000)
    await ctx.send(f"Latency: `{latency}ms`", delete_after=15)


@lxc.command()
async def ap2(ctx, *, message: str):
    await ctx.message.delete()
    channel_id = ctx.channel.id

    if channel_id in active_tasks and not active_tasks[channel_id].done():
        return

    async def message_loop():
        count = 1
        try:
            while True:
                await ctx.send(f"{message} -# {count}")
                count += 1
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(message_loop())
    active_tasks[channel_id] = task

@lxc.command()
async def ap2e(ctx):
    await ctx.message.delete()
    channel_id = ctx.channel.id

    if channel_id in active_tasks and not active_tasks[channel_id].done():
        active_tasks[channel_id].cancel()
        del active_tasks[channel_id]

@lxc.command()
async def gn(ctx, delay: float, *, name: str):
    await ctx.message.delete()
    channel_id = ctx.channel.id

    if not isinstance(ctx.channel, discord.GroupChannel):
        return

    if channel_id in name_tasks and not name_tasks[channel_id].done():
        return

    async def name_loop():
        count = 1
        try:
            while True:
                await ctx.channel.edit(name=f"{name} | {count}")
                count += 1
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(name_loop())
    name_tasks[channel_id] = task

@lxc.command()
async def gne(ctx):
    await ctx.message.delete()
    channel_id = ctx.channel.id

    if channel_id in name_tasks and not name_tasks[channel_id].done():
        name_tasks[channel_id].cancel()
        del name_tasks[channel_id]

@lxc.command(aliases=['lgcs'])
async def leavegcs(ctx):
    await ctx.message.delete()
    await ctx.send("Are you sure you want to leave all group DMs? Type 'yes' to confirm or 'no' to cancel", delete_after=60)

    def c(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']

    try:
        r = await lxc.wait_for('message', timeout=30.0, check=c)
    except asyncio.TimeoutError:
        return

    if r.content.lower() == 'no':
        return

    n = 0

    for g in lxc.private_channels:
        if isinstance(g, discord.GroupChannel):
            try:
                await g.leave()
                n += 1
                await asyncio.sleep(1)
            except discord.HTTPException:
                pass

    await ctx.send(f'left {n} gcs')

@lxc.command()
async def banner(ctx, user: discord.User):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    url = f"https://discord.com/api/v10/users/{user.id}/profile"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            banner_hash = data.get("user", {}).get("banner")
            
            if banner_hash:
                banner_format = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_hash}.{banner_format}?size=2048"
                await ctx.send(f"```{user.display_name}'s banner:```\n[Lxc Sb]({banner_url})")
            else:
                await ctx.send(f"{user.mention} does not have a banner set.")
        else:
            await ctx.send(f"Failed to retrieve banner: {response.status_code} - {response.text}")
    
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@lxc.command()
async def avatar(ctx, user: discord.User = None):
    try:
        if user is None:
            user = lxc.user

        if user.display_avatar:
            avatar_url = user.display_avatar.url
            await ctx.send(f'```{user.display_name}'s avatar:```\n[Lxc Sb]({avatar_url})')
        else:
            await ctx.send(f'{user.name} does not have an avatar.', delete_after=5)

        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f'An error occurred: {e}', delete_after=10)
        

@lxc.command()
async def ipinfo(ctx, ip: str):
    try:
        response = requests.get(f'http://ipwho.is/{ip}')
        data = response.json()

        if data.get('success'):
            info = (
                f"**Latitude**: {data.get('latitude', 'N/A')}\n"
                f"**Longitude**: {data.get('longitude', 'N/A')}\n"
                f"**Country**: {data.get('country', 'N/A')}\n"
                f"**City**: {data.get('city', 'N/A')}\n"
                f"**Postal Code**: {data.get('postal', 'N/A')}\n"
            )
        else:
            errmsg = data.get('message', 'Failed to retrieve IP information.')
            info = f'Error: {errmsg}'
    except Exception as e:
        info = f'An error occurred: {e}'
    
    await ctx.message.delete()
    await ctx.send(info, delete_after=30)
   

@lxc.command()
async def spam(ctx, times: int, *, message):
    await ctx.message.delete()
    
    for _ in range(times):
        try:
            await ctx.send(message)
        except discord.HTTPException as e:
            print(f'Error: {e}')
            await asyncio.sleep(5)

@lxc.command()
async def log(ctx, channel_id: int = None):
    await ctx.message.delete()
    channel = lxc.get_channel(channel_id) if channel_id else ctx.channel
    if not channel:
        return

    messages = []
    total_messages = 0
    async for _ in channel.history(limit=None, oldest_first=True):
        total_messages += 1

    if total_messages == 0:
        await ctx.send("No messages to log", delete_after=10)
        return

    progress_msg = await ctx.send(f"Logging <#{channel.id}> in progress...\n[0% Completed]\nEst. Time: calculating...")

    messages = []
    fetched = 0
    start_time = time.time()
    last_update = time.time()

    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        messages.append(f"[{timestamp}] {message.author.name}: {message.content}")
        fetched += 1

        now = time.time()
        if now - last_update >= 5:
            percent = (fetched / total_messages) * 100
            elapsed = now - start_time
            est_total = (elapsed / fetched) * total_messages if fetched else 0
            est_remaining = est_total - elapsed
            est_str = format_duration(est_remaining)
            await progress_msg.edit(content=(
                f"Logging <#{channel.id}> in progress...\n"
                f"[{percent:.1f}% Completed]\n"
                f"Est. Time: {est_str}"
            ))
            last_update = now

    await progress_msg.edit(content="Writing messages to file...")

    with open("log.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(messages))

    await ctx.send(file=discord.File("log.txt"))
    os.remove("log.txt")
    await progress_msg.edit(content=f"Finished logging <#{channel.id}> ({fetched} messages).")


lxc.run(token)
