import asyncio
import discord
from discord.ext import commands

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

lxc.run(token)
