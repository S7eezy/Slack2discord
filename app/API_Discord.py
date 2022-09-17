__author__ = "S7eezy"
__version__ = "1.0"
__project__ = "Slack2discord"

import discord
import asyncio
import time
from datetime import datetime
import wget
import os
import sys
import requests
from tqdm import tqdm


class DiscordClient:

    def __init__(self, token, data, channels) -> None:
        self.slackData = data
        self.slackChannels = channels

        self.client = discord.Client(intents=discord.Intents.default())
        self.channels = None

        @self.client.event
        async def on_ready() -> None:
            """
            Waits for Discord client initialization then start main loop.

            :return: None
            """
            for channel in self.slackChannels:
                await self.addChannel(channel)
                self.getChannels()
                for data in tqdm(self.slackData[channel], desc=f"Processing {channel}"):
                    await self.addMessage(channel=self.channels[channel], data=data)

        self.client.run(token)

    def getChannels(self) -> None:
        """
        Store a list of channels for every linked Discord server.

        :return: None
        """
        channels = dict()
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                channels[channel.name] = channel.id
        self.channels = channels

    async def addChannel(self, channel) -> None:
        """
        Create a new channel for every linked Discord server.

        :param channel: channel name
        :return: None
        """
        for guild in self.client.guilds:
            await guild.create_text_channel(channel)

    async def addMessage(self, channel, data) -> None:
        """
        Create and send a Slack message to Discord.

        :param channel: channel name
        :param data: data dict
        :return: None
        """
        if len(data["text"]) > 1023:
            isFirst = True
            parts = self.splitMessage(message=data["text"])
            for part in parts:
                embedVar = self.createEmbed(title=datetime.fromtimestamp(float(data["time"])), value=part, author=data["user"], icon=data["icon"], isFirst=isFirst)
                await self.client.get_channel(channel).send(embed=embedVar)
                isFirst = False

        if len(data["text"]) < 1024 and data["text"] != "":
            embedVar = self.createEmbed(title=datetime.fromtimestamp(float(data["time"])), value=data["text"], author=data["user"], icon=data["icon"])
            await self.client.get_channel(channel).send(embed=embedVar)

        if data["file"] is not None:
            for file in data["file"]:
                await self.getFile(file=file, time=datetime.fromtimestamp(float(data["time"])), channel=channel)

        await self.client.get_channel(channel).send(file=discord.File("temp/divider.png"))

    async def deleteAll(self) -> None:
        """
        Use with caution ! Deletes every channel on all linked Discord servers.

        :return: None and even Void
        """
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                await self.client.get_channel(channel.id).delete()

    @staticmethod
    def createEmbed(color=0x3876c7, title=None, subtitle="\u200b", value=None, inline=False, author=None, icon=None, isFirst=True) -> discord.Embed:
        """
        Create a Discord embed message.

        :param color: border color
        :param title: main title
        :param subtitle: sub title
        :param value: main content
        :param inline: use inline or not
        :param author: author field's name
        :param icon: author field's icon
        :param isFirst: is it the first embed or is it the n-th component of a split embed
        :return: discord.Embed
        """
        if isFirst:
            embedVar = discord.Embed(title=title, color=color)
            embedVar.set_author(name=author, icon_url=icon)
        else:
            embedVar = discord.Embed(color=color)
        embedVar.add_field(name=subtitle, value=value, inline=inline)
        return embedVar

    @staticmethod
    def createErrorEmbed(color=0xe62222, title=None, file_url=None, file_name=None, file_size=None, author="Warning", icon="https://icones.pro/wp-content/uploads/2021/05/symbole-d-avertissement-jaune.png") -> discord.Embed:
        """
        Create a Discord error embed message. Used for size limitation during uploads.

        :param color: border color
        :param title: main title
        :param file_url: file direct download url
        :param file_name: file name and extension
        :param file_size: file size in bytes
        :param author: author field's name
        :param icon: author field's icon
        :return: discord.Embed
        """
        embedVar = discord.Embed(title=title, color=color)
        embedVar.set_author(name=author, icon_url=icon)
        embedVar.add_field(name=f"{file_name} ({int(file_size*100)/100} Mb)", value=f"File size exceeds Discord's 8 Mb limitation ({int(file_size*100)/100} Mb). You can download it manually here: {file_url}", inline=False)
        return embedVar

    @staticmethod
    def splitMessage(message=None, length=1024) -> [str]:
        """
        Split a message when length exceeds 1024 characters.

        :param message: data string
        :param length: desired length for each split
        :return: [str]
        """
        split = []
        while True:
            if "." in message:
                res = [i for i in range(len(message)) if message.startswith(".", i)]
                found = False
                for p in reversed(res):
                    if p < length:
                        found = True
                        split.append(message[:p])
                        message = message[p + 1:]
                        break
                if not found:
                    split.append(message[:length-1])
                    message = message[length:]
                    break
            else:
                split.append(message[:length-1])
                message = message[length:]
                break
        return split

    async def getFile(self, file, time, channel) -> None:
        """
        Download a file and upload it to Discord.

        :param file: file direct download url
        :param time: message datetime information
        :param channel: message channel
        :return: None
        """
        filename = str(file).split("download/")[1].split("?t")[0]
        response = requests.head(file, allow_redirects=True)
        size = int(response.headers.get('content-length', -1)) / float(1 << 20)
        if size < 8:
            wget.download(file, out=f"temp/{filename}")
            await self.client.get_channel(channel).send(file=discord.File(f"temp/{filename}"))
            os.remove(os.path.join("temp", filename))
        else:
            embedVar = self.createErrorEmbed(title=time, file_url=file, file_name=filename, file_size=size, author="File size over 8Mb")
            await self.client.get_channel(channel).send(embed=embedVar)
