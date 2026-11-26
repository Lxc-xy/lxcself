import asyncio
import discord
from discord.ext import commands
import os
import requests
import time
from datetime import datetime, timezone
import tls_client
import random
import string
import math


token = "Yourmom"
lxc = commands.Bot(command_prefix="!", self_bot=True, help_command=None)

# Varibles

pspam = False
active_tasks = {}
name_tasks = {}
rspam = False


@lxc.event
async def on_ready():
    print(f"Logged in as {lxc.user} (ID: {lxc.user.id})")

# functions

def format_duration(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} {sec} second{'s' if sec != 1 else ''}"
    hours, min = divmod(minutes, 60)
    return f"{hours} hour{'s' if hours != 1 else ''} {min} minute{'s' if min != 1 else ''}"


@lxc.command()
async def help(ctx, cmd_name: str = None):
    await ctx.message.delete()

    if not cmd_name:
        await ctx.send("Please provide a command name. Usage: `.help <command>`", delete_after=10)
        return

    cmd = lxc.get_command(cmd_name)
    if not cmd:
        for command in lxc.commands:
            if cmd_name in command.aliases:
                cmd = command
                break

    if not cmd:
        await ctx.send(f"No command named or aliased as '{cmd_name}' found.", delete_after=10)
        return

    msg = f"```js\nCommand Help: {cmd.qualified_name}\n\n"
    msg += f"Usage: {cmd.qualified_name} {cmd.signature}\n"
    if cmd.aliases:
        msg += f"Aliases: {', '.join(cmd.aliases)}\n"
    msg += "```"

    await ctx.send(msg, delete_after=60)
    
        
menu_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠄⢤⣠⢷⣝⢦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠒⣲⣦⣺⣳⣤⡿⠛⠃⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠉⠢⣣⣁⠀⣀⠙⢧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡎⠑⢤⡼⡩⡪⠷⠀⠀⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣶⡞⢯⣠⡻⠼⡇⠀⠀⠀⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡷⢌⠻⣶⡟⡄⠈⠁⠀⠀⠐⢣⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡴⣷⣿⡗⠀⣡⠊⠻⠋⠒⢄⠀⠀⢀⠔⠙⢦⡀⠀
⠀⠀⠀⠀⠀⠀⡠⠊⠁⢺⣿⢇⠜⠁⠀⠀⠀⠀⣠⠗⠊⠀⠀⣠⡺⠆⠀
⠀⠀⠀⠀⣠⣾⡗⠀⠀⢸⡿⠋⠀⠀⠀⠀⠀⠀⠻⣆⠛⣠⣞⢕⢽⣆⠀
⠀⠀⠀⣴⣿⣿⡇⠀⢀⠞⠁⠀⠀⠀⠀⠀⠀⠀⢐⡯⡪⡫⡢⣑⣕⢕⠀
⠀⠀⣼⣿⣿⣿⠇⡰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢮⡺⣾⣮⡪⡳⠀
⢀⣼⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠺⣷⣝⢮⠀
⠾⠿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠪⣻⡇
"""

@lxc.command()
async def menu(ctx, page: int = 1):
    await ctx.message.delete()

    cmds = sorted([c for c in lxc.commands if not c.hidden], key=lambda c: c.qualified_name.lower())
    per_page = 40
    total = len(cmds)
    pages = math.ceil(total / per_page)

    if page < 1 or page > pages:
        await ctx.send(f"Page {page} doesn't exist. Total pages: {pages}.", delete_after=10)
        return

    start = (page - 1) * per_page
    end = start + per_page
    page_cmds = cmds[start:end]

    left = page_cmds[:20]
    right = page_cmds[20:]

    header = f"```js\n{menu_art}\n``````\n<> = required  [] = optional\n[Lxc Sb]\n``````js"
    cmd_section = "\n"

    for i in range(20):
        l = f"[{str(start + i + 1).zfill(2)}] {left[i].qualified_name}" if i < len(left) else ""
        r = f"[{str(start + i + 21).zfill(2)}] {right[i].qualified_name}" if i < len(right) else ""
        cmd_section += f"{l.ljust(24)}│ {r}\n"

    cmd_section += "``````js"

    footer_text = "Creator - lxc | 77lxc"
    footer = f"\n{footer_text.center(40)}\n```"

    await ctx.send(f"{header}\n{cmd_section}\n{footer}", delete_after=60)
    


@lxc.command()
async def ping(ctx):
    def convert_units(value):
        units = ["ps", "ns", "µs", "ms", "s"]
        scales = [1e-12, 1e-9, 1e-6, 1e-3, 1]  
        for i in range(len(scales) - 1, -1, -1):
            if value >= scales[i] or i == 0:
                return f"{value / scales[i]:.2f}{units[i]}"

    start_determinism = time.perf_counter()
    _ = ctx.prefix
    end_determinism = time.perf_counter()
    prefix_determinism_time = end_determinism - start_determinism  

    host = lxc.latency
    api = (datetime.now(timezone.utc) - ctx.message.created_at.replace(tzinfo=timezone.utc)).total_seconds()
    now = datetime.now(timezone.utc)
    uptime_duration = now - start_time

    d = uptime_duration.days
    h, r = divmod(uptime_duration.seconds, 3600)
    m, s = divmod(r, 60)

    upart = []
    if d > 0:
        upart.append(f"{d}d")
    if h > 0:
        upart.append(f"{h}h")
    if m > 0:
        upart.append(f"{m}m")
    if s > 0 or not upart:
        upart.append(f"{s}s")

    uptime = " ".join(upart)

    response = (
        "```js\n"
        f"Prefix Determinism Time: <{convert_units(prefix_determinism_time)}>\n"
        f"Host Latency: <{convert_units(host)}>\n"
        f"API Latency: <{convert_units(api)}>\n"
        f"Uptime: <{uptime}>\n"
        "```"
    )
    
    await ctx.send(response, delete_after=20)
    await ctx.message.delete()


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

@lxc.command()
async def poll(ctx, channel_id: int, *, name: str):
    await ctx.message.delete()
    global pspam
    pspam = True

    while pspam:
        try:
            with open("ab.txt", "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            return

        if not lines:
            return

        poll_question = random.choice(lines).replace("{name}", name)
        nonce = str(random.randint(10**17, 10**18))
        poll_name = f"HEX HOES THE FUCK OUT OF {name}"

        poll_data = {
            "mobile_network_type": "unknown",
            "content": "",
            "nonce": nonce,
            "tts": False,
            "flags": 0,
            "poll": {
                "question": {"text": poll_name},
                "answers": (
                    [{"poll_media": {"text": poll_name}}]
                    + [{"poll_media": {"text": poll_question}} for _ in range(8)]
                    + [{"poll_media": {"text": poll_name}}]
                ),
                "allow_multiselect": True,
                "duration": 5,
                "layout_type": 1
            }
        }

        async with session.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers={
                "Authorization": token,
                "Content-Type": "application/json"
            },
            json=poll_data
        ):
            pass

        await asyncio.sleep(3)
        

@lxc.command()
async def stoppoll(ctx):
    global pspam
    pspam = False
    await ctx.message.delete()


@lxc.command()
async def rename(ctx, *, new_name: str):
    await ctx.message.delete()
    if isinstance(ctx.channel, (discord.TextChannel, discord.GroupChannel)):
        await ctx.channel.edit(name=new_name)
 

@lxc.command()
async def regionspam(ctx, channel_id: int):
    await ctx.message.delete()

    channel = lxc.get_channel(channel_id)
    if not isinstance(channel, discord.VoiceChannel):
        await ctx.send("Invalid voice channel ID.")
        return

    rspam = False
    await ctx.send(f"Started region spam on: {channel.name}")

    while not rspam:
        try:
            r = random.choice(["us-west", "us-east", "us-central", "us-south", "rotterdam", "hongkong", "japan", "brazil", "singapore", "sydney", "russia", "india"])
            await channel.edit(rtc_region=r)
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            break


@lxc.command()
async def stopspamregion(ctx):
    await ctx.message.delete()

    rspam = True
    await ctx.send("Stopped all region spams", delete_after=3)


@lxc.command()
async def ss(ctx, url: str):
    await ctx.message.delete()

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    params = urlencode({
        "access_key": "b861ba18afda4ba2aeb1d80bab2a4161",
        "url": url,
        "wait_until": "page_loaded"
    })
    image_path = "lxc.png"

    try:
        urlretrieve(f"https://api.apiflash.com/v1/urltoimage?{params}", image_path)
        await ctx.send(file=discord.File(image_path))
        os.remove(image_path)
    except Exception as e:
        await ctx.send(f"Error generating screenshot: {e}")
        

class DiscordJoinerPY:
    def __init__(self):
        self.client = tls_client.Session(
            client_identifier="chrome120",
            random_tls_extension_order=True
        )
        self.tokens = []
        self.load_tokens()

    def headers(self, token: str):
        headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="120", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-context-properties': 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6IjExMDQzNzg1NDMwNzg2Mzc1OTEiLCJsb2NhdGlvbl9jaGFubmVsX2lkIjoiMTEwNzI4NDk3MTkwMDYzMzIzMCIsImxvY2F0aW9uX2NoYW5uZWxfdHlwZSI6MH0=',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-GB',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6Iml0LUlUIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE5MzkwNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
        }
        return headers


    def get_cookies(self):
        cookies = {}
        try:
            response = self.client.get('https://discord.com')
            for cookie in response.cookies:
                if cookie.name.startswith('__') and cookie.name.endswith('uid'):
                    cookies[cookie.name] = cookie.value
            return cookies
        except Exception as e:
            print(f'Failed to obtain cookies ({e})')
            return cookies

    def accept_invite(self, token: str, invite: str):
        payload = {
            'session_id': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        }
        try:
            response = self.client.post(
                url=f'https://discord.com/api/v10/invites/{invite}',
                headers=self.headers(token=token),
                json=payload,
                cookies=self.get_cookies()
            )
            if response.status_code == 200:
                return "Successfully"
            elif response.status_code == 401:
                return "Invalid Token"
            elif response.status_code == 403:
                return "Flagged Token"
            elif response.status_code == 400:
                return "Hcaptcha"
            elif response.status_code == 404:
                return "Unknown invite"
            else:
                return f"Error {response.status_code}"
        except Exception as e:
            return str(e)

    def load_tokens(self):
        try:
            with open("tokens.txt", "r") as file:
                self.tokens = [line.strip() for line in file.readlines()]
        except:
            self.tokens = []


@lxc.command(aliases=['tjoin'])
async def mjoin(ctx, invite: str):
    joiner = DiscordJoinerPY()
    if not joiner.tokens:
        await ctx.send("No tokens found in tokens.txt", delete_after=5)
        return

    msg = await ctx.send("[Token Joiner in progress]\n\nToken: N/A\nStatus: Waiting...")

    for token in joiner.tokens:
        token_display = token[:15] 
        status = joiner.accept_invite(token, invite)
        await msg.edit(content=f"[Token Joiner in progress]\n\nToken: {token_display}\nStatus: {status}")
        await asyncio.sleep(2)

    await msg.edit(content="[Token Joiner Finished]\n\nAll tokens processed.")
    

lxc.run(token)
