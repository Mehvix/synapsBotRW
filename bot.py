#!/usr/bin/env python
# -*- coding: utf-8 -*-
# testing all branches are good.

"""
TODOs:
    https://github.com/Mehvix/synapsBotRW/projects/1

Code:
    https://github.com/Mehvix/synapsBotRW
"""

import socket
import websockets
import json
import asyncio
import os
import random
import sys
from datetime import datetime
from mcstatus import MinecraftServer
import aiohttp

import discord
from discord.ext import commands

import karma
import curtime
import settings

# Cogs being used
extensions = ['accept', 'admin', 'basic', 'forwarding', 'karma', 'typeracer', 'notifications', 'games',
              'verified', 'reddit', 'qr', 'lobby_text', 'hearthstone_decode']

settings.set_server("main")  # make sure this is test or main

seconds = 0
ban_message = 0
users = 0

global before_invites, after_invites
before_invites = []
after_invites = []


def flair(num_of_users):  # todo: add more flairs
    flairs = ['Created by Mehvix#7966',
              'Running Version {}'.format(settings.get_version()),
              'Used by {} users'.format(num_of_users),
              'Try .github for code',
              'Try .trello for upcoming stuff'
              ]
    return random.choice(flairs)


# Defines Client
client = commands.Bot(description="If you have any issues please contact @Mehvix#7966",
                      command_prefix='.',
                      owner_id="196355904503939073",
                      case_insensitive=True)


# discord.ext.commands.HelpFormatter(show_hidden=False)


def get_json(file_path):
    with open(file_path, 'r') as fp:
        return json.load(fp)


async def timer():
    await client.wait_until_ready()
    global seconds
    while True:
        # "Who invited" code
        for guild in client.guilds:
            for invite in await guild.invites():
                x = [invite.url, invite.uses, invite.inviter.id]
                before_invites.append(x)

        # Presence
        try:
            await client.change_presence(
                activity=discord.Streaming(name=flair(users), url='https://twitch.tv/mehvix',
                                           twitch_name="Mehvix"))
        except (websockets.exceptions.ConnectionClosed):  # aiohttp.client_exceptions.ClientConnectorError
            pass  # Random error (I think?)

        try:
            fp = random.choice(os.listdir("avatars"))
            with open('avatars/{}'.format(fp), 'rb') as f:
                try:
                    await client.user.edit(avatar=f.read())
                except discord.HTTPException:
                    pass  # Sometimes discord gets angry when the profile pic is changed a lot
        except FileNotFoundError:
            pass  # you dont have any avatars!

        # Comic Code
        # if str(str(str(datetime.now()).split(" ")[1]).split(".")[0])[:5] == "09:00":
        #     date = datetime.today().strftime('%Y/%m/%d')
        #     search = "https://www.gocomics.com/calvinandhobbes/{}".format(date)
        #     print(search)
        #     channel = client.get_channel(settings.notification_channel)
        #     await channel.send(search)
        #     await channel.send("https://xkcd.com/")

        chnl = client.get_channel(settings.mc_data_channel)
        server = MinecraftServer.lookup("mc.mehvix.com:25544")

        try:
            status = server.status()
            await chnl.edit(name="{} / 20 Online".format(status.players.online))

        except (AttributeError, ConnectionRefusedError, socket.timeout):
            await chnl.edit(name="Server Offline")

        await asyncio.sleep(59)  # sometimes this skips if it's on 60?


@commands.Cog.listener()
async def on_member_join(member):
    channel = client.get_channel(id=settings.notification_channel)
    for guild in client.guilds:
        for invite in await guild.invites():
            x = [invite.url, invite.uses, invite.inviter.id]
            after_invites.append(x)

        await asyncio.sleep(1)

        def diff(first, second):
            second = list(second)
            return [item for item in first if item not in second]

        invite_used = diff(after_invites, before_invites)
        invite_user = client.get_user(invite_used[0][2])

        if member.guild.name != "Bot Test":
            karma.user_add_karma(invite_user.id, 75, invite_user.name)
            await channel.send("<@{}> used an invited created by <@{}> which gave the invite creator `75` karma".
                               format(member.id, invite_user.id))

    level_role = discord.utils.get(channel.guild.roles, id=settings.level_role)
    roles_role = discord.utils.get(channel.guild.roles, id=settings.roles_role)
    groups_role = discord.utils.get(channel.guild.roles, id=settings.groups_role)
    games_role = discord.utils.get(channel.guild.roles, id=settings.games_role)
    restriction_role = discord.utils.get(channel.guild.roles, id=settings.restriction_role)
    level1_role = discord.utils.get(channel.guild.roles, name="Level 1")

    if level_role not in member.roles:
        await member.add_roles(level_role, roles_role, groups_role, games_role, restriction_role, level1_role)

@client.event
async def on_connect():
    print("Connected!")


@client.event
async def on_ready():
    global users
    users = len(set(client.get_all_members()))
    channels = len([c for c in client.get_all_channels()])
    server_list = list(client.guilds)
    dirpath = os.getcwd()

    print("=========================================================================")
    print("                                      ____        __  ____ _       __")
    print("   _______  ______  ____ _____  _____/ __ )____  / /_/ __ \ |     / /")
    print("  / ___/ / / / __ \/ __ `/ __ \/ ___/ __  / __ \/ __/ /_/ / | /| / /")
    print(" (__  ) /_/ / / / / /_/ / /_/ (__  ) /_/ / /_/ / /_/ _, _/| |/ |/ /")
    print("/____/\__, /_/ /_/\__,_/ .___/____/_____/\____/\__/_/ |_| |__/|__/")
    print("     /____/           /_/")
    print("• Bot Version:               {}".format(os.path.basename(dirpath)))
    print("• Discord Version:           {}".format(discord.__version__))
    print("• Python Version:            {}".format(sys.version.split()[0]))
    print("• Client Version:            {}".format(settings.get_version()))
    print("• Start Time:                {}".format(curtime.get_time()))
    print("• Client Name:               {}".format(client.user))
    print("• Client ID:                 {}".format(client.user.id))
    print("• Channels:                  {}".format(channels))
    print("• Users:                     {}".format(users))
    print("• Connected to " + str(len(client.guilds)) + " server(s):")
    for x in range(len(server_list)):
        print("     > " + server_list[x - 1].name)
    print("=========================================================================")

    if len(client.guilds) > 1:
        print("ISSUE: It's not recommended to have more than one server being hosted at the same time.")

    await client.change_presence(
        activity=discord.Streaming(name=flair(users), url='https://twitch.tv/mehvix',
                                   twitch_name="Mehvix"))  # TODO add more presences


@client.event
async def on_resumed():
    print("{}: Resumed".format(curtime.get_time()))


@client.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")

    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("Sorry. This command is disabled and cannot be used.")

    elif isinstance(error, commands.CheckFailure):
        await ctx.send("Sorry. You don't have permission to use this command.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing a parameter. Do `.help [command name]` for more info")

    elif isinstance(error, commands.NotOwner):
        await ctx.send("Only the bot's owner can use this command")

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I need special permissions to use that command.")

    elif isinstance(error, commands.BadArgument):
        await ctx.send(error)

    elif isinstance(error, commands.TooManyArguments):
        await ctx.send("You have too many arguments")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            "That command is on a cooldown for `{}` more seconds. It can be used every `{}` seconds".format(
                commands.CommandOnCooldown.cooldown, str(commands.CommandOnCooldown.retry_after)[:5]))

    """
    elif isinstance(error, commands.BadArgument):
        command = ctx.message.content.split()[1]
        await ctx.send("Missing an argument: " + command)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("I don't recognize that command")
    """


if __name__ == "__main__":
    for extension in extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    client.loop.create_task(timer())
    client.run(settings.token)
