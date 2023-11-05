# Monster Armor Class Bot

A Telegram bot that allows you to search for information about monsters from the game Dungeons & Dragons based on their armor class.

## Description

This bot gives users access to information about monsters, including their names, armor class, and threat level. It is capable of performing the following functions:

- Search for monsters based on specified armor class values.
- Sorting found monsters by danger level, armor class and name.
- Sending the user information about the monster, including its name and a link to more information.

The data is taken from the site dnd.su/bestiary, which provides a free translation of the D&D bestiary into Russian.

## How to start a project:

__On a standalone windows server:__

_Clone the repository and go to it on the command line::_
```
git clone https://github.com/Galenfea/armor_class_bot.git
```
```
cd armor_class_bot
```

_Create and activate a virtual environment:_
```
python -m venv venv
```
```
source venv/Scripts/activate
```

_Install dependencies from the requirements.txt file:_
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

_Create a .env file and add the following environment variables there:_
```
BOT_TOKEN = 'Your_Telegram_API_token'
```

_Launch the bot, do:_
```
python main.py
```