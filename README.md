# 🔹 Slack2discord

*Transfer a whole Slack workspace to Discord.*

*This python script allows you to transfer channels, messages and files to Discord from Slack's json export files.*

- - -

# Installation
## Slack2discord
- Clone repository
- `pip install -r requirements.txt`
- Edit **config.ini** as needed

## Bot
- Create a discord bot using the [Discord developer portal](https://discord.com/developers/applications)
- Copy bot's token and invite your bot to your Discord server

## Slack
- [Export Slack data](https://slack.com/help/articles/201658943-Export-your-workspace-data)
- Copy export content in `../Slack2discord/resources`. 
- It should look like `../Slack2discord/resources/channel1/day1.json`, `../Slack2discord/resources/channel1/day2.json`, `../Slack2discord/resources/channel2/day1.json`

# Usage
`cd ../Slack2discord/ && python slack2discord.py`
