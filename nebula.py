import io
import random
import uuid
import asyncio
import os
import re
from array import array
from io import BytesIO

from datetime import datetime, timedelta

import aiohttp
import discord
import qrcode

from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import typing
import pickle

from matplotlib.pyplot import title

import activity_img

import apollo
import collection_img
#import cosmo
import teest
import profile_img5se3
import translate

from config import triples_member_names, class_, season, artist, collection_array


import math

def start_after(page):
    start_number = (page - 1) * 9
    return start_number

triples_member = [
        app_commands.Choice(name="SeoYeon", value="SeoYeon"),
        app_commands.Choice(name="HyeRin", value="HyeRin"),
        app_commands.Choice(name="JiWoo", value="JiWoo"),
        app_commands.Choice(name="ChaeYeon", value="ChaeYeon"),
        app_commands.Choice(name="YooYeon", value="YooYeon"),
        app_commands.Choice(name="SooMin", value="SooMin"),
        app_commands.Choice(name="Nakyoung", value="Nakyoung"),
        app_commands.Choice(name="YuBin", value="YuBin"),
        app_commands.Choice(name="Kaede", value="Kaede"),
        app_commands.Choice(name="DaHyun", value="DaHyun"),
        app_commands.Choice(name="Kotone", value="Kotone"),
        app_commands.Choice(name="YeonJi", value="YeonJi"),
        app_commands.Choice(name="Nien", value="Nien"),
        app_commands.Choice(name="SoHyun", value="SoHyun"),
        app_commands.Choice(name="Xinyu", value="Xinyu"),
        app_commands.Choice(name="Mayu", value="Mayu"),
        app_commands.Choice(name="Lynn", value="Lynn"),
        app_commands.Choice(name="JooBin", value="JooBin"),
        app_commands.Choice(name="HaYeon", value="HaYeon"),
        app_commands.Choice(name="ShiOn", value="ShiOn"),
        app_commands.Choice(name="ChaeWon", value="ChaeWon"),
        app_commands.Choice(name="Sullin", value="Sullin"),
        app_commands.Choice(name="SeoAh", value="SeoAh"),
        app_commands.Choice(name="JiYeon", value="JiYeon"),

    ]



tree_guild = 1207625911709597737

register = {}
old = {}

# Function to save the register dictionary to a file
def save_register():
    with open('register.pkl', 'wb') as f:
        pickle.dump(register, f)


# Function to load the register dictionary from a file
def load_register():
    global register
    if os.path.exists('register.pkl'):
        with open('register.pkl', 'rb') as f:
            register = pickle.load(f)


# Function to load the register dictionary from a file
def load_old():
    global old
    if os.path.exists('old.pkl'):
        with open('old.pkl', 'rb') as f:
            old = pickle.load(f)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('Nebula'), intents=discord.Intents().all())

    async def on_ready(self):
        # Remove the guild-specific sync to sync globally
        await self.tree.sync()
        print(f'Logged in as {self.user}')

        for guild in client.guilds:
            print(f'서버: {guild.name} (멤버 수: {guild.member_count})')



client = Client()

async def name_auto(action: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    matching_files, address = await apollo.user_search_by_name(current, action.locale)
    return [app_commands.Choice(name=num, value=num) for num in matching_files]

@client.tree.command(name="connect", description="connect discord-cosmo")
@discord.app_commands.describe(cosmo_nickname="Input cosmo nickname")
@app_commands.autocomplete(cosmo_nickname=name_auto)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def connect(action: discord.Interaction, cosmo_nickname: str):
    print(f"user!!!! : {action.user.name}")
    await perform_connect(action, cosmo_nickname)

async def perform_connect(action: discord.Interaction, cosmo_nickname: str):
    global register
    await action.response.defer(ephemeral=True)

    # Search for the Cosmo user
    cosmo_user_list, cosmo_address_list = await apollo.user_search_by_name(cosmo_nickname, action.locale)
    if not cosmo_user_list:
        await action.followup.send(translate.translate("The account doesn't exist.", action.locale))
        return

    # Find an exact match (case-insensitive)
    cosmo_user = None
    cosmo_address = None
    for user, address in zip(cosmo_user_list, cosmo_address_list):
        if user.lower() == cosmo_nickname.lower():
            cosmo_user = user
            cosmo_address = address
            break

    if not cosmo_user:
        await action.followup.send(translate.translate("The account doesn't exist.", action.locale))
        return

    # Allow connection even if the Cosmo account is already verified by another user
    # Add or update the user's connection
    register[action.user.id] = {
        'cosmo_address': cosmo_address,
        'verified': False  # Mark as unverified
    }
    save_register()

    await action.followup.send(
        translate.translate(
            f"{cosmo_user} and {action.user.name} are connected", action.locale
        )
    )


# 소문자 이름을 키로 하고, 정확한 대소문자를 값으로 하는 딕셔너리 생성
triples_member_map = {name.lower(): name for name in triples_member_names}


# 자동 완성 함수
async def member_autocomplete(interaction: discord.Interaction, current: str):
    # 현재 입력된 텍스트와 매칭되는 멤버 이름 필터링 (대소문자 무시)
    suggestions = [
        app_commands.Choice(name=name, value=name)
        for name in triples_member_names
        if current.lower() in name.lower()
    ]
    # 최대 25개의 선택지 반환
    return suggestions[:25]




@client.tree.command(name="collection", description="Show cosmo profile")
@app_commands.choices(
    sort=[
        app_commands.Choice(name="newest", value="newest"),
        app_commands.Choice(name="oldest", value="oldest"),
    ],
    season=season,
    class_=class_,
    artist=artist,
    array=collection_array
)
@app_commands.autocomplete(member=member_autocomplete)
@app_commands.autocomplete(cosmo_nickname=name_auto)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def collection(
    action: discord.Interaction,
    cosmo_nickname: Optional[str],
    discord_user: Optional[discord.User],
    sort: Optional[str],
    season: Optional[str],
    class_: Optional[str],
    member: Optional[str],
    #gridable: Optional[bool], # cosmo api -> apollo api => Can load gridable status
    sendable: Optional[bool],
    artist: Optional[str],
    array: Optional[int]
):
    print(f"user!!!! : {action.user.name}")
    if member:
        # 사용자가 입력한 값을 소문자로 변환하여 키로 사용
        member_key = member.lower()
        if member_key not in triples_member_map:
            await action.response.send_message(
                translate.translate(f"'{member}' is not a valid member name, please try again.", action.locale),
                ephemeral=True
            )
            return

    # 정확한 대소문자를 가진 멤버 이름 가져오기
        member = triples_member_map[member_key]

    await action.response.defer(ephemeral=False)


    if array:
        objekt_per_page = array
    else:
        objekt_per_page = 9

    # User validation and data retrieval
    cosmo_user, cosmo_address, discord_nickname = await get_user_info(
        action, cosmo_nickname, discord_user
    )
    if not cosmo_user:
        return  # Error messages are handled within get_user_info

    # Set default sort option
    if sort is None:
        sort = 'newest'

    # Search options and filters
    options = {
        "artist": artist,
        "season": season,
        "sort": sort,
        "class": class_,
        "member": member,
        # "gridable": gridable,
        "transferable": sendable,
        'cosmo_address': cosmo_address,
        'cosmo_nickname': cosmo_user,
        'discord_nickname': discord_nickname,
    }
    filters = {k: str(v) for k, v in options.items() if v is not None}

    # Fetch search results and total pages
    objekt_search_result = await apollo.objekt_search(cosmo_address, filters)

    total_page = math.ceil(objekt_search_result['total'] / objekt_per_page)
    page = 1

    # Generate initial image
    img = await collection_img.create_image(options, objekt_search_result, 0, (page, total_page), objekt_per_page)

    # Create and send the message with pagination view
    view = CollectionView(
        options, objekt_search_result, cosmo_user, page, total_page, objekt_per_page
    )
    await action.followup.send(
        files=[discord.File(fp=img, filename=f"{cosmo_user}.webp")], view=view
    )


async def get_user_info(action, cosmo_nickname, discord_user):
    # Check for both inputs provided
    if cosmo_nickname and discord_user:
        await action.followup.send(
            translate.translate('Please provide only one of cosmo_nickname or discord_user.', action.locale),
            ephemeral=True,
        )
        return None, None, None

    # When neither is provided, check registered info
    if not cosmo_nickname and not discord_user:
        if action.user.id not in register:
            await action.followup.send(
                translate.translate(
                    'Please provide a cosmo_nickname or discord_user, or connect your account using /connect.',
                    action.locale,
                ),
                ephemeral=True,
            )
            return None, None, None
        user_info = register[action.user.id]
        cosmo_address = user_info['cosmo_address']
        cosmo_user = await apollo.user_search_byaddress(cosmo_address)
        if cosmo_user == None:
            cosmo_user = ('hidden')
        discord_nickname = action.user.name
        return cosmo_user, cosmo_address, discord_nickname

    # If cosmo_nickname is provided
    if cosmo_nickname:
        cosmo_user_list, cosmo_address_list = await apollo.user_search_by_name(cosmo_nickname, action.locale)
        if not cosmo_user_list:
            await action.followup.send(
                translate.translate('The account does not exist.', action.locale),
                ephemeral=True,
            )
            return None, None, None
        cosmo_user = cosmo_user_list[0]
        cosmo_address = cosmo_address_list[0]
        discord_nickname = 'unknown'
        # Check if the address is registered and verified
        if cosmo_address in register:
            # Get the Discord user ID associated with this Cosmo address
            discord_user_id = register[cosmo_address]['discord_user_id']
            # Fetch the user's info
            user_info = register[discord_user_id]
            discord_nickname = (await client.fetch_user(discord_user_id)).name
        return cosmo_user, cosmo_address, discord_nickname

    # If discord_user is provided
    if discord_user:
        if discord_user.id not in register:
            await action.followup.send(
                translate.translate(
                    f'{discord_user.name} has not connected a Cosmo account.', action.locale
                ),
                ephemeral=True,
            )
            return None, None, None
        user_info = register[discord_user.id]
        cosmo_address = user_info['cosmo_address']
        cosmo_user = await apollo.user_search_byaddress(cosmo_address)
        if cosmo_user == None:
            cosmo_user = 'hidden'
        discord_nickname = discord_user.name

        return cosmo_user, cosmo_address, discord_nickname


class CollectionView(discord.ui.View):
    def __init__(self, options, objekt_search_result, cosmo_user, page, total_page, objekt_per_page, title_name='Collect', list_slug=None):
        super().__init__(timeout=None)
        self.options = options
        self.objekt_search_result = objekt_search_result
        self.cosmo_user = cosmo_user
        self.page = page
        self.total_page = total_page

        self.objekt_per_page = objekt_per_page
        self.title_name = title_name


        # Buttons
        self.first_page_button = discord.ui.Button(
            label="|<", style=discord.ButtonStyle.blurple
        )
        self.previous_page_button = discord.ui.Button(
            label="<", style=discord.ButtonStyle.blurple
        )
        self.next_page_button = discord.ui.Button(
            label=">", style=discord.ButtonStyle.blurple
        )
        self.last_page_button = discord.ui.Button(
            label=">|", style=discord.ButtonStyle.blurple
        )

        # Set callbacks
        self.first_page_button.callback = self.first_page_callback
        self.previous_page_button.callback = self.previous_page_callback
        self.next_page_button.callback = self.next_page_callback
        self.last_page_button.callback = self.last_page_callback

        self.update_buttons()

        # Add buttons to the view
        self.add_item(self.first_page_button)
        self.add_item(self.previous_page_button)
        self.add_item(self.next_page_button)
        self.add_item(self.last_page_button)

        if list_slug:
            self.go_web_button = discord.ui.Button(
                label="Apollo", style=discord.ButtonStyle.gray,
                url=f"https://apollo.cafe/@{cosmo_user}/list/{list_slug}"
            )

            self.add_item(self.go_web_button)

    def update_buttons(self):
        self.first_page_button.disabled = self.page == 1
        self.previous_page_button.disabled = self.page == 1
        self.next_page_button.disabled = self.page == self.total_page
        self.last_page_button.disabled = self.page == self.total_page

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.defer()

        start_after_num = (self.page - 1) * self.objekt_per_page

        while len(self.objekt_search_result['objekts']) <= self.page * self.objekt_per_page and self.objekt_search_result['hasNext']:
            print(len(self.objekt_search_result['objekts']), self.page * self.objekt_per_page)
            filters = {k: str(v) for k, v in self.options.items() if v is not None}
            filters['page']= self.objekt_search_result['nextStartAfter']
            print(filters)
            objekt_search_result_add = await apollo.objekt_search(self.options['cosmo_address'], filters)
            self.objekt_search_result['objekts'].extend(objekt_search_result_add['objekts'])
            self.objekt_search_result['hasNext'] = objekt_search_result_add['hasNext']
            self.objekt_search_result['nextStartAfter'] = objekt_search_result_add.get('nextStartAfter')

        img = await collection_img.create_image(
            self.options, self.objekt_search_result, start_after_num, (self.page, self.total_page), self.objekt_per_page, title=self.title_name if self.title_name else None
        )
        self.update_buttons()
        await interaction.edit_original_response(
            attachments=[discord.File(fp=img, filename=f"{self.cosmo_user}.webp")], view=self
        )

    async def first_page_callback(self, interaction: discord.Interaction):
        self.page = 1
        await self.update_message(interaction)

    async def previous_page_callback(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)

    async def next_page_callback(self, interaction: discord.Interaction):
        if self.page < self.total_page:
            self.page += 1
            await self.update_message(interaction)

    async def last_page_callback(self, interaction: discord.Interaction):
        self.page = self.total_page
        await self.update_message(interaction)


async def list_auto(action: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    global register

    # Ensure the user is registered
    user_id = action.user.id
    if user_id not in register:
        return []

    cosmo_info = register[user_id]
    cosmo_address = cosmo_info['cosmo_address']
    cosmo_nickname = await apollo.user_search_byaddress(cosmo_address)

    # Fetch Objekt lists
    name_list, slug_list = await apollo.search_objekt_list(cosmo_address, action.locale)

    # Check if any Objekt lists are available
    if not name_list:
        message = translate.translate(
            f"No Objekt lists found.\nCreate an Objekt list [here](https://apollo.cafe/@{cosmo_address})",
            action.locale
        )
        return [app_commands.Choice(name=message, value='')]

    # Create choices
    choices = [
        app_commands.Choice(name=name, value=f'{name}|{slug}')
        for name, slug in zip(name_list, slug_list)
    ]

    # Prioritize choices that match the current input
    if current:
        current_lower = current.lower()
        matching_choices = [choice for choice in choices if choice.name.lower().startswith(current_lower)]
        non_matching_choices = [choice for choice in choices if not choice.name.lower().startswith(current_lower)]
        choices = matching_choices + non_matching_choices

    # Limit to 25 choices as per Discord's autocomplete limit
    return choices[:25]


@client.tree.command(name="apollo", description="Show my apollo objekt list")
@app_commands.choices(
    sort=[
        app_commands.Choice(name="newest", value="newest"),
        app_commands.Choice(name="oldest", value="oldest"),
    ],
    season=season,
    class_=class_,
    member=triples_member,
    artist=artist,
    array=collection_array
)
@app_commands.autocomplete(list=list_auto)
@discord.app_commands.describe(list="select my apollo's list")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def apollo_list(
    action: discord.Interaction,
    list: str,
    artist: Optional[str],
    sort: Optional[str],
    member: Optional[str],
    class_: Optional[str],
    season: Optional[str],
    array: Optional[int]
):
    print(f"user!!!! : {action.user.name}")
    if action.user.id not in register:
        await action.response.send_message(
            translate.translate(
                'Please connect your Cosmo ID first using /connect', action.locale
            ),
            ephemeral=True,
        )
        return

    # Validate the list parameter
    list_parts = list.split('|')
    if len(list_parts) != 2:
        cosmo_address = register[action.user.id]['cosmo_address']
        cosmo_nickname = await apollo.user_search_byaddress(cosmo_address)
        await action.response.send_message(
            translate.translate(
                f"Invalid Objekt list.\nCreate Objekt lists [here](https://apollo.cafe/@{cosmo_address})",
                action.locale,
            ),
            ephemeral=True,
        )
        return

    await action.response.defer(ephemeral=False)

    if array:
        objekt_per_page = array
    else:
        objekt_per_page = 9


    # User and list info
    cosmo_address = register[action.user.id]['cosmo_address']
    cosmo_user = await apollo.user_search_byaddress(cosmo_address)
    discord_nickname = action.user.name
    list_name, list_slug = list_parts

    # Default sort option
    if sort is None:
        sort = 'newest'

    # Options and filters
    options = {
        "artist": artist,
        "season": season,
        "sort": sort,
        "class": class_,
        "member": member,
        'cosmo_address': cosmo_address,
        'cosmo_nickname': cosmo_user,
        'discord_nickname': discord_nickname,
        'list_name': list_name,
        'list_slug': list_slug,
    }
    filters = {k: v for k, v in options.items() if k in ("artist", "season", "sort", "class", "member") and v is not None}

    # Fetch search results and total pages
    page = 1
    objekt_search_result = await apollo.objekt_list_search(cosmo_address, list_slug, filters)
    total_page = math.ceil(objekt_search_result['total'] / objekt_per_page)

    # Generate initial image
    img = await collection_img.create_image(options, objekt_search_result, 0, (page, total_page), objekt_per_page, title='apollo')

    title_name = 'Apollo'
    # Create and send the message with pagination view
    view = CollectionView(options, objekt_search_result, cosmo_user, page, total_page, objekt_per_page, title_name, list_slug)
    await action.followup.send(
        files=[discord.File(fp=img, filename=f"{cosmo_user}.webp")], view=view
    )

"""
class ApolloListView(discord.ui.View):
    def __init__(self, options, objekt_search_result, cosmo_user, list_slug, page, total_page, objekt_per_page: Optional[int]):
        super().__init__(timeout=None)
        self.options = options
        self.objekt_search_result = objekt_search_result
        self.cosmo_user = cosmo_user
        self.list_slug = list_slug
        self.page = page
        self.total_page = total_page
        self.objekt_per_page = objekt_per_page

        # Buttons
        self.first_page_button = discord.ui.Button(label="|<", style=discord.ButtonStyle.blurple)
        self.previous_page_button = discord.ui.Button(label="<", style=discord.ButtonStyle.blurple)
        self.next_page_button = discord.ui.Button(label=">", style=discord.ButtonStyle.blurple)
        self.last_page_button = discord.ui.Button(label=">|", style=discord.ButtonStyle.blurple)
        self.go_web_button = discord.ui.Button(
            label="Apollo", style=discord.ButtonStyle.gray,
            url=f"https://apollo.cafe/@{cosmo_user}/list/{list_slug}"
        )

        # Set callbacks
        self.first_page_button.callback = self.first_page_callback
        self.previous_page_button.callback = self.previous_page_callback
        self.next_page_button.callback = self.next_page_callback
        self.last_page_button.callback = self.last_page_callback

        self.update_buttons()

        # Add buttons to the view
        self.add_item(self.first_page_button)
        self.add_item(self.previous_page_button)
        self.add_item(self.next_page_button)
        self.add_item(self.last_page_button)
        self.add_item(self.go_web_button)

    def update_buttons(self):
        self.first_page_button.disabled = self.page == 1
        self.previous_page_button.disabled = self.page == 1
        self.next_page_button.disabled = self.page == self.total_page
        self.last_page_button.disabled = self.page == self.total_page

    async def update_message(self, interaction: discord.Interaction):
        start_after_num = (self.page - 1) * 9
        img = await collection_img.create_image(
            self.options, self.objekt_search_result, start_after_num, (self.page, self.total_page), self.objekt_per_page, title='Apollo'
        )
        self.update_buttons()
        await interaction.message.edit(
            attachments=[discord.File(fp=img, filename=f"{self.cosmo_user}.webp")], view=self
        )

        await interaction.response.defer()

    async def first_page_callback(self, interaction: discord.Interaction):
        self.page = 1
        await self.update_message(interaction)

    async def previous_page_callback(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)

    async def next_page_callback(self, interaction: discord.Interaction):
        if self.page < self.total_page:
            self.page += 1
            await self.update_message(interaction)

    async def last_page_callback(self, interaction: discord.Interaction):
        self.page = self.total_page
        await self.update_message(interaction)"""

"""
def extract_numbers(text):
    pattern = r"\{([^}]+)\}"
    match = re.search(pattern, text)
    if match:
        numbers = match.group(1).split(":")
        member = get_english_name(numbers[0])
        if member == None:
            return None
        info = {
            'season': f'{numbers[1]}01',
            'member': member,
            'number': numbers[2],
            'line': numbers[3],
        }
        return info
    else:
        return None
name_dict = {
    "S1": "Seoyeon",
    "S2": "Hyerin",
    "S3": "Jiwoo",
    "S4": "Chaeyeon",
    "S5": "Yooyeon",
    "S6": "Soomin",
    "S7": "Nakyoung",
    "S8": "Yubin",
    "S9": "Kaede",
    "S10": "Dahyun",
    "S11": "Kotone",
    "S12": "Yeonji",
    "S13": "Nien",
    "S14": "Sohyun",
    "S15": "Xinyu",
    "S16": "Mayu",
    "S17": "Lynn",
    "S18": "JooBin",
    "S19": "HaYeon",
    "S20": "ShiOn",
    "S21": "ChaeWon",
    "S22": "Sullin",
    "S23": "SeoAh",
    "S24": "JiYeon",
    "S25": 'Heejin',
    "S26": 'HaSeul',
    "S27": 'KimLip',
    "S28": 'JinSoul',
    "S29": 'Choerry',
}

def get_english_name(snum):
    return name_dict.get(snum, None)

""" #For ai obj_info. Not use now

@client.tree.command(name="objekt_info", description="Show objekt info")
@app_commands.choices(
    season=season,
)
@app_commands.autocomplete(member=member_autocomplete)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def objekt_info(action: discord.Interaction, member: str, season: str, card_number: int, offline: Optional[str]):
    print(f"user!!!! : {action.user.name}")
    if member:
        # 사용자가 입력한 값을 소문자로 변환하여 키로 사용
        member_key = member.lower()
        if member_key not in triples_member_map:
            await action.response.send_message(
                translate.translate(f"'{member}' is not a valid member name, please try again.", action.locale),
                ephemeral=True
            )
            return

    # 정확한 대소문자를 가진 멤버 이름 가져오기
    member = triples_member_map[member_key]


    await action.response.defer()

    info = {
        'season': season,
        'member': member,
        'number': card_number,
        'line': 'A' if offline else 'Z',
    }
    # Fetch metadata
    result_meta = await apollo.search_objekt_meta(info)
    if result_meta.get('total', '0') == '0':
        await action.followup.send(
            translate.translate(
                f"Are you looking for {info['member']} {info['season']} {info['number']}{info['line']}? The specified Objekt could not be found.",
                action.locale
            ),
            ephemeral=True
        )
        return

    # Fetch Objekt details
    result = await apollo.search_objekt_by_slug(info)
    if not result:
        await action.followup.send(
            translate.translate('Unable to retrieve Objekt details.', action.locale),
            ephemeral=True
        )
        return

    # Convert ISO date to Discord timestamp
    iso_date = result.get('createdAt')
    if iso_date:
        try:
            date_obj = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            unix_timestamp = int(date_obj.timestamp())
            discord_timestamp = f"<t:{unix_timestamp}:D>"
        except ValueError:
            discord_timestamp = "Unknown date format"
    else:
        discord_timestamp = "Unknown"

    # Prepare embed fields
    accent_color = result.get('accentColor', '#FFFFFF').replace('#', '')
    try:
        color_value = int(accent_color, 16)
    except ValueError:
        color_value = 0xFFFFFF  # Default white color

    collection_id = result.get('collectionId', 'Unknown')
    front_image_url = result.get('frontImage', '')

    copies = int(result_meta.get('total', '0'))
    description = result_meta.get('metadata', {}).get('description', '')
    if description:
        translated_description = translate.translate(description, action.locale)
    else:
        translated_description = 'No description available.'

    # Create the embed
    embed = discord.Embed(
        title="Objekt Information",
        color=color_value
    )
    if copies <= 10:
        rate = 'impossible'
    elif copies <= 25:
        rate = "extremely-rare"
    elif copies <= 50:
        rate = 'very-rare'
    elif copies <= 100:
        rate = 'rare'
    elif copies <= 350:
        rate = 'uncommon'
    else:
        rate = 'common'

    embed.set_author(name=collection_id)
    embed.set_image(url=front_image_url)
    embed.add_field(name="Created at", value=discord_timestamp, inline=True)
    embed.add_field(name="Copies", value=str(copies)+ f" ({rate})", inline=True)
    embed.add_field(name="Description", value=translated_description, inline=False)
    embed.set_footer(text="Powered by Apollo.cafe, and translated with DeepL")

    await action.followup.send(embed=embed)


"""# Define the choices for the artist parameter
artist_choices = [
    app_commands.Choice(name='tripleS', value='tripleS'),
    app_commands.Choice(name='artms', value='artms')
]
""" # added in config


@client.tree.command(name="profile", description="Show cosmo profile")
@app_commands.autocomplete(cosmo_nickname=name_auto)
@app_commands.describe(
    cosmo_nickname="Your Cosmo nickname",
    artist="Choose an artist",
    discord_user="Can Select a Discord user"
)
@app_commands.choices(artist=artist)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def profile(
    action: discord.Interaction,
    cosmo_nickname: Optional[str],
    artist: Optional[str],
    discord_user: Optional[discord.User]
):
    print(f"user!!!! : {action.user.name}")
    await action.response.defer()

    # Check if both cosmo_nickname and discord_user are provided
    if cosmo_nickname and discord_user:
        await action.followup.send(
            translate.translate('Please provide only one of cosmo_nickname or discord_user.', action.locale),
            ephemeral=True
        )
        return

    # Initialize variables
    cosmo_address = None
    discord_nickname = None
    user_info = None
    title_objekt_tokenId = None


    # If cosmo_nickname is provided
    if cosmo_nickname:
        cosmo_nickname_verify = cosmo_nickname
        cosmo_usernames, cosmo_addresses = await apollo.user_search_by_name(cosmo_nickname, action.locale)
        if not cosmo_usernames or cosmo_nickname_verify.lower() != cosmo_usernames[0].lower():
            await action.followup.send(
                translate.translate('The specified user could not be found.', action.locale),
                ephemeral=True
            )
            return
        cosmo_nickname = cosmo_usernames[0]
        cosmo_address = cosmo_addresses[0]
        discord_nickname = 'unknown'

        # Check if the Cosmo address is registered
        if cosmo_address in register:
            discord_user_id = register[cosmo_address]['discord_user_id']
            discord_user_info = register.get(discord_user_id)
            if discord_user_info:
                discord_nickname = (await client.fetch_user(discord_user_id)).name
                title_objekt_tokenId = register[discord_user_id]['title_objekt_tokenId']


    # If discord_user is provided
    elif discord_user:
        if discord_user.id not in register:
            await action.followup.send(
                translate.translate('The user has not linked a Cosmo nickname.', action.locale),
                ephemeral=True
            )
            return
        user_info = register[discord_user.id]
        cosmo_address = user_info['cosmo_address']
        cosmo_nickname = await apollo.user_search_byaddress(cosmo_address)
        discord_nickname = discord_user.name

    # If neither is provided, use action.user
    else:
        if action.user.id not in register:
            await action.followup.send(
                translate.translate('Please provide a discord_user or cosmo_nickname, or link your account using /connect.', action.locale),
                ephemeral=True
            )
            return
        user_info = register[action.user.id]
        cosmo_address = user_info['cosmo_address']
        print(cosmo_address)
        cosmo_nickname = await apollo.user_search_byaddress(cosmo_address)
        discord_nickname = action.user.name

    if user_info is not None and isinstance(user_info, dict) and 'title_objekt_tokenId' in user_info:
        title_objekt_tokenId = user_info['title_objekt_tokenId']
    if artist:
        artist_name = artist
    elif action.user.id in register:
        if 'default_artist' in register[action.user.id]:
            artist_name = register[action.user.id]['default_artist']
        else:
            artist_name = 'tripleS'
    else:
        artist_name = 'tripleS'

    # Prepare options for profile image generation
    options = {
        'cosmo_nickname': cosmo_nickname,
        'discord_nickname': discord_nickname,
        'cosmo_address': cosmo_address,
        'artist': artist_name,
        'title_objekt_tokenId': title_objekt_tokenId
    }
    print(options)
    # Generate and send the profile image
    image_file = await profile_img5se3.main(options)
    await action.followup.send(files=[discord.File(fp=image_file, filename="profile.png")])


@client.tree.command(name="disconnect", description="Disconnecting Nebula from Cosmo")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def disconnect(action: discord.Interaction):
    print(f"user!!!! : {action.user.name}")
    global register
    if action.user.id in register:
        register.pop(register[action.user.id]['cosmo_address'], None)
    register.pop(action.user.id, None)
    save_register()
    await action.response.send_message(translate.translate('Your account is safely disconnected.', action.locale))
    return


@client.tree.command(name="verify", description="Verify that the account is owned by you.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def verify(action: discord.Interaction):
    print(f"user!!!! : {action.user.name}")
    await perform_verify(action)

async def perform_verify(action):
    global register
    await action.response.defer(ephemeral=True)

    # Initial embed message
    initial_embed = discord.Embed(
        title=translate.translate("You'll see a QR or link to verify shortly!", action.locale),
        description=translate.translate("This is a testing feature, if the QR doesn't appear, please use /connect", action.locale),
        color=0xd95656
    )
    name = translate.translate("You don't need to enter a security number.", action.locale)
    value = (
        f"{translate.translate('Just press the Continue button that appears in the app.', action.locale)}\n"
        f"""{translate.translate("For security purposes, we only verify your nickname. We don't collect any other information.", action.locale)}"""
    )
    initial_embed.add_field(
        name=name,
        value=value,
        inline=True
    )
    original_message = await action.followup.send(embed=initial_embed, ephemeral=True)

    # Generate ticket data
    ticket_data = await teest.send_post_request()

    if not ticket_data or 'ticket' not in ticket_data:
        await action.followup.send(translate.translate('Ticket creation failed. Please try again later.', action.locale), ephemeral=True)
        return

    # Generate QR code image
    img_bytes = generate_qr_code(ticket_data['ticket'])

    # Create the authentication embed and view
    auth_embed = create_auth_embed(ticket_data['ticket'], name, value, action.locale)
    auth_view = create_auth_view(ticket_data['ticket'], action.locale)

    # Send the authentication message
    original_message = await original_message.edit(
        attachments=[discord.File(fp=img_bytes, filename="qr.png")],
        view=auth_view,
        embed=auth_embed
    )

    # Wait for user authentication
    user_data = await wait_for_authentication(ticket_data['ticket'], original_message)
    if not user_data:
        await action.followup.send(translate.translate('The time has expired.', action.locale), ephemeral=True)
        return

    # Update the register with authenticated user data
    await update_register(action.user.id, user_data, action.locale)

    await action.followup.send(translate.translate("The ownership of your Cosmo account has been verified.", action.locale), ephemeral=True)


def generate_qr_code(ticket: str) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"cosmo://ticket-login?t={ticket}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


def create_auth_embed(ticket: str, name, value, locale) -> discord.Embed:
    future_time = datetime.now() + timedelta(seconds=180)
    unix_timestamp = int(future_time.timestamp())
    embed = discord.Embed(
        title=f"{translate.translate('Time remaining', locale)} : <t:{unix_timestamp}:R>",
        description=translate.translate("Take a picture of the QR code with your regular camera, or tap Open Cosmo app", locale),
        color=0xfb00ff
    )
    embed.add_field(
        name=name,
        value=value,
        inline=True
    )
    return embed


def create_auth_view(ticket: str, locale) -> discord.ui.View:
    cosmo_button = discord.ui.Button(
        label=translate.translate("Verify with the Cosmo app", locale),
        style=discord.ButtonStyle.link,
        url=f"http://login.objektify.xyz/redirect?t={ticket}"
    )
    view = discord.ui.View(timeout=180)
    view.add_item(cosmo_button)
    return view


async def wait_for_authentication(ticket: str, original_message: discord.WebhookMessage) -> dict:
    url = (
        f"https://shop.cosmo.fans/bff/v1/users/auth/login/native/qr/ticket"
        f"?ticket={ticket}&tid={uuid.uuid4()}"
    )
    timeout = 180  # seconds
    start_time = datetime.now()

    async with aiohttp.ClientSession() as session:
        while (datetime.now() - start_time).seconds < timeout:
            async with session.get(url) as response:
                data = await response.json()
                print(data)  # For debugging purposes; remove or replace with logging in production

                if 'message' in data:
                    await original_message.delete()
                    return None

                if data.get('status') == 'wait_for_certify':
                    await original_message.delete()
                    return data['user']

            await asyncio.sleep(1)

    await original_message.delete()
    return None


async def update_register(discord_user_id: int, user_data: dict, locale):
    global register
    cosmo_nickname = user_data.get('nickname')
    if not cosmo_nickname:
        return

    # Fetch the Cosmo address using the nickname
    cd = await apollo.user_search_by_name(cosmo_nickname, None)
    cosmo_address = str(cd[1][0])
    if not cosmo_address:
        return

    # Check if the Cosmo account is already verified by another user
    previous_user_id = None
    for user_id, info in register.items():
        if (
            isinstance(info, dict) and
            info.get('cosmo_address') == cosmo_address and
            info.get('verified')
        ):
            # Cosmo account is verified by another user
            previous_user_id = user_id
            break  # Break the loop as we found the previous user

    if previous_user_id:
        # Revoke verification from the previous user
        previous_user_info = register.get(previous_user_id, {})
        previous_user_info['verified'] = False
        previous_user_info.pop('cosmo_address', None)
        register[previous_user_id] = previous_user_info

        # Remove the cosmo_address key pointing to the previous user
        register.pop(cosmo_address, None)

        # Notify the previous user that their verification has been revoked
        try:
            previous_user = await client.fetch_user(previous_user_id)
            await previous_user.send(translate.translate(
                "Your Cosmo account verification has been revoked because it has been verified by another user.",
                locale
            ))
        except Exception as e:
            # Handle exceptions, e.g., user has DMs closed
            pass

    # Update the register with the verified account for the new user
    register[discord_user_id] = {
        'cosmo_address': cosmo_address,
        'verified': True  # Mark as verified
    }
    register[cosmo_address] = {'discord_user_id': discord_user_id}
    save_register()


@client.tree.command(name="nebula", description="customize your nebula")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def nebula(action: discord.Interaction):
    print(f"user!!!! : {action.user.name}")
    view = nebulaView()

    await action.response.send_message(translate.translate('Choose options', action.locale), view=view, ephemeral=True)

class connectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.name = discord.ui.TextInput(label="Write Cosmo nickname", placeholder='jpark', max_length=16, default='', style=discord.TextStyle.short)

        self.name.callback = self.name_callback

    async def name_callback(self, interaction: discord.Interaction):
        await perform_connect(interaction, self.name.value)


class nebulaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Buttons
        self.profile_image = discord.ui.Button(label="Set title objekt", style=discord.ButtonStyle.blurple)
        self.default_artist = discord.ui.Button(label="Set default artist", style=discord.ButtonStyle.blurple)

        # Set callbacks
        self.profile_image.callback = self.profile_image_callback
        self.default_artist.callback = self.default_artist_callback

        # Add buttons to the view
        self.add_item(self.profile_image)
        self.add_item(self.default_artist)

    async def default_artist_callback(self, interaction: discord.Interaction):
        global register
        if not interaction.user.id in register:
            view = connectView()
            await interaction.response.send_message(translate.translate('First connect your account', interaction.locale), view=view)
            return
        view = setArtistView()
        await interaction.response.send_message(view=view, ephemeral=True)

    async def profile_image_callback(self, interaction: discord.Interaction):
        global register
        if not await check_user_account(interaction):
            return

        options = {
            "artist": None,
            "season": None,
            "sort": 'newest',
            "class": None,
            "member": None,
            'cosmo_address': None,
            'cosmo_nickname': None,
            'discord_nickname': None,
            'list_name': None,
            'list_slug': None,
        }

        filters = {k: v for k, v in options.items() if v is not None}

        # Fetch search results and total pages
        objekt_search_result = await apollo.objekt_search(register[interaction.user.id]['cosmo_address'], filters)
        total_page = math.ceil(objekt_search_result['total'] / 18)
        img = await collection_img.create_image(options, objekt_search_result, 0 ,(1, total_page), 18, 'choose')
        page = 1
        view = title_objekt_view(interaction, objekt_search_result, page)
        await interaction.followup.send(files=[discord.File(fp=img, filename=f"choose.webp")], ephemeral=True, view=view)

async def check_user_account(action: discord.Interaction):
    await action.response.defer(ephemeral=True)
    global register

    if not action.user.id in register:
        msg = translate.translate('First, verify your account', action.locale)
        view = verify_induce_view(action)
        await action.followup.send(msg, ephemeral=True, view=view)
        return False

    if register[action.user.id]['verified'] == False:
        msg = translate.translate('You must first verify your account', action.locale)
        view = verify_induce_view(action)
        await action.followup.send(msg, ephemeral=True, view=view)
        return False

    return True


class setArtistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # Uis
        self.select = discord.ui.Select(placeholder='Select default Artist')
        self.select.add_option(label=f"tripleS",
                                   value=f"tripleS",
                                   description=f"")
        self.select.add_option(label=f"ARTMS",
                               value=f"ARTMS",
                               description=f"")

        # Set callbacks
        self.select.callback = self.select_callback


        # Add buttons to the view
        self.add_item(self.select)
    async def select_callback(self, interaction: discord.Interaction):
        global register
        if not interaction.user.id in register:
            view = connectView()
            await interaction.response.send_message(translate.translate('First connect your account', interaction.locale), view=view)
            return
        register[interaction.user.id]['default_artist'] = str(self.select.values[0])
        save_register()
        await interaction.response.send_message(f"Now default artist is {register[interaction.user.id]['default_artist']}", ephemeral=True)


class verify_induce_view(discord.ui.View):
    def __init__(self, action: discord.Interaction):
        super().__init__(timeout=None)
        self.action = action


        # Buttons
        self.verify_button = discord.ui.Button(label=translate.translate('Verify Now', action.locale), style=discord.ButtonStyle.green)

        # Set callbacks
        self.verify_button.callback = self.verify_button_callback

        # Add buttons to the view
        self.add_item(self.verify_button)

    async def verify_button_callback(self, action: discord.Interaction):
        await perform_verify(action)


class title_objekt_view(discord.ui.View):
    def __init__(self, action: discord.Interaction, objekt_search_result, page):
        super().__init__(timeout=None)
        self.action = action
        self.objekt_search_result = objekt_search_result
        collections = objekt_search_result['objekts'][0:18]


        self.collections = objekt_search_result['objekts']
        self.objekt_search_result = objekt_search_result
        self.page = page
        self.total_page = math.ceil(objekt_search_result['total'] / 18)


        # Uis
        self.select = discord.ui.Select(placeholder=translate.translate('Select title Objekt', action.locale))
        for i in range(len(collections)):
            print(collections[i]['collectionId'])
            self.select.add_option(label=f"{collections[i]['collectionId']}",
                              value=f"{collections[i]['tokenId']}|{str(collections[i]['objektNo']).zfill(5)}",
                              description=f"#{str(collections[i]['objektNo']).zfill(5)}")

        # Buttons
        self.first_page_button = discord.ui.Button(
                label="|<", style=discord.ButtonStyle.blurple
            )
        self.previous_page_button = discord.ui.Button(
                label="<", style=discord.ButtonStyle.blurple
            )
        self.next_page_button = discord.ui.Button(
                label=">", style=discord.ButtonStyle.blurple
            )
        self.last_page_button = discord.ui.Button(
                label=">|", style=discord.ButtonStyle.blurple
            )


        # Set callbacks
        self.select.callback = self.select_callback
        self.first_page_button.callback = self.first_page_callback
        self.previous_page_button.callback = self.previous_page_callback
        self.next_page_button.callback = self.next_page_callback
        self.last_page_button.callback = self.last_page_callback

        self.update_buttons()


        # Add buttons to the view
        self.add_item(self.select)
        self.add_item(self.first_page_button)
        self.add_item(self.previous_page_button)
        self.add_item(self.next_page_button)
        self.add_item(self.last_page_button)

    async def select_callback(self, action2: discord.Interaction):
        global register
        register[action2.user.id]['title_objekt_tokenId'] = self.select.values[0].split('|')[0]
        save_register()
        await action2.response.send_message(translate.translate('title OBJEKT now set!', action2.locale), ephemeral=True)


    def update_buttons(self):
        self.first_page_button.disabled = self.page == 1
        self.previous_page_button.disabled = self.page == 1
        self.next_page_button.disabled = self.page == self.total_page
        self.last_page_button.disabled = self.page == self.total_page
        collections = self.collections[18*(self.page-1):18*(self.page)]

        # Clear and re-add select options
        self.select.options.clear()  # Clear previous options
        for i in range(len(collections)):
            print(collections[i]['collectionId'])
            self.select.add_option(label=f"{collections[i]['collectionId']}",
                                   value=f"{collections[i]['tokenId']}|{str(collections[i]['objektNo']).zfill(5)}",
                                   description=f"#{str(collections[i]['objektNo']).zfill(5)}")


    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.defer()

        start_after_num = (self.page - 1) * 18
        options = {
            "artist": None,
            "season": None,
            "sort": 'newest',
            "class": None,
            "member": None,
            'cosmo_address': None,
            'cosmo_nickname': None,
            'discord_nickname': None,
            'list_name': None,
            'list_slug': None,
        }
        img = await collection_img.create_image(
            options, self.objekt_search_result, start_after_num, (self.page, self.total_page), 18, 'choose'
        )
        self.update_buttons()


        await interaction.edit_original_response(
            attachments=[discord.File(fp=img, filename=f"choose.webp")], view=self
        )

    async def first_page_callback(self, interaction: discord.Interaction):
        self.page = 1
        await self.update_message(interaction)

    async def previous_page_callback(self, interaction: discord.Interaction):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)

    async def next_page_callback(self, interaction: discord.Interaction):
        if self.page < self.total_page:
            self.page += 1
            await self.update_message(interaction)

    async def last_page_callback(self, interaction: discord.Interaction):
        self.page = self.total_page
        await self.update_message(interaction)


@client.tree.command(name="activity", description="Show trade history")
@app_commands.choices(
    artist=artist
)
@app_commands.autocomplete(cosmo_nickname=name_auto)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def activity(
    action: discord.Interaction,
    cosmo_nickname: Optional[str],
    discord_user: Optional[discord.User],
    artist: Optional[str],
):
    print(f"user!!!! : {action.user.name}")
    await action.response.defer()

    # User validation and data retrieval
    cosmo_user, cosmo_address, discord_nickname = await get_user_info(
        action, cosmo_nickname, discord_user
    )
    if not cosmo_user:
        return  # Error messages are handled within get_user_info


    if artist:
        artist_name = artist
    elif action.user.id in register:
        if 'default_artist' in register[action.user.id]:
            artist_name = register[action.user.id]['default_artist']
        else:
            artist_name = 'tripleS'
    else:
        artist_name = 'tripleS'

    img = await activity_img.main(cosmo_user, cosmo_address, discord_nickname, artist_name)

    if type(img) == str:
        await action.followup.send(img)
        return

    await action.followup.send(files=[discord.File(fp=img, filename=f"activity.webp")])

load_register()

print(register)


if __name__ == "__main__":
    import sys

    # 스크립트 실행 시 "test"라는 인자가 있는지 확인
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("test 인자를 받았습니다!")
        token = os.getenv('nebula_test') #Test
    else:
        print("test 인자가 없습니다.")
        token = os.getenv('nebula')

    print(token)
    client.run(token)