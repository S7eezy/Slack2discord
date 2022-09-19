__author__ = "S7eezy"
__version__ = "1.0"
__project__ = "Slack2discord"

from app.API_Discord import DiscordClient as discord
import json
from datetime import datetime
import time
import configparser
import os
import operator


class Engine:
    def __init__(self) -> None:
        # Define Slack backup path
        self.path = 'resources'
        if self.getConfig('path') != "":
            self.path = self.getConfig('path')

        # Define Channels to create and import
        self.channels = None
        if self.getConfig('channels') != "":
            channels = self.getConfig('channels')
            self.channels = self.getConfig('channels')
        self.getChannels()

        # Define Servers affected by slack import
        self.servers = None
        if self.getConfig('servers') != "":
            channels = self.getConfig('servers')
            self.servers = self.getConfig('servers')

        # Discord client gateway connection
        self.token = self.getConfig('token')
        self.users = self.getUsers()
        self.data = self.getData()
        self.discord = discord(token=self.token, data=self.data, channels=self.channels)

    @staticmethod
    def getConfig(var) -> str:
        """
        Get a config.ini value.

        :param var: variable to retrieve
        :return: str
        """
        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        var = cfg.get('slack2discord', var)
        return var

    def getChannels(self) -> None:
        """
        Get a list of every channel name in Slack's export files.

        :return: None
        """
        if not self.channels:
            dirs = next(os.walk('resources'))[1]
            self.channels = dirs

    def getData(self) -> dict:
        """
        Create a full dictionary with Slack's export files data.

        :return: Dict[str]
        """
        slackData = dict()
        for channel in self.channels:
            slackData[channel] = []
            for file in os.listdir(os.path.join(os.getcwd(), self.path, channel)):
                if file.endswith(".json"):
                    with open(os.path.join(os.getcwd(), self.path, channel, file), encoding="utf-8") as f:
                        for message in json.load(f):
                            if "subtype" not in message and "bot_id" not in message:
                                time = float(message["ts"])
                                text = message["text"].replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
                                user = self.users[message["user"]]["name"]
                                icon = self.users[message["user"]]["icon"]
                                if "text" in message and "user_profile" in message and "ts" in message:
                                    slackData[channel].append(dict(time=time, user=user, text=text, icon=icon, file=None))
                                else:
                                    if "files" in message:
                                        files = []
                                        for file in message['files']:
                                            if "url_private_download" in file:
                                                files.append(file["url_private_download"])
                                        slackData[channel].append(dict(time=time, user=user, text=text, icon=icon, file=files))
            slackData[channel].sort(key=operator.itemgetter('time'))
        return slackData

    def getUsers(self) -> dict:
        """
        Get username informations and store them in a dictionary.

        :return: Dict[str]
        """
        users = dict()
        for channel in self.channels:
            for file in os.listdir(os.path.join(os.getcwd(), self.path, channel)):
                if file.endswith(".json"):
                    with open(os.path.join(os.getcwd(), self.path, channel, file), encoding="utf-8") as f:
                        for message in json.load(f):
                            if "subtype" not in message:
                                if "user_profile" in message:
                                    if not message["user"] in users:
                                        users[message["user"]] = dict()
                                        users[message["user"]]["name"] = message["user_profile"]["real_name"]
                                        users[message["user"]]["icon"] = message["user_profile"]["image_72"]
        return users
