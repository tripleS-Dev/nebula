from discord import app_commands


triples_member_names = [ # I make it before add artms, so It's real name is 'modhaus_member_names' is correct
        "SeoYeon", "HyeRin", "JiWoo", "ChaeYeon", "YooYeon", "SooMin",
        "NaKyoung", "YuBin", "Kaede", "DaHyun", "Kotone", "YeonJi",
        "Nien", "SoHyun", "Xinyu", "Mayu", "Lynn", "JooBin",
        "HaYeon", "ShiOn", "ChaeWon", "Sullin", "SeoAh", "JiYeon",

        'HeeJin', 'HaSeul', 'KimLip', 'JinSoul', 'Choerry'
    ]

season=[
        app_commands.Choice(name="Atom01", value="Atom01"),
        app_commands.Choice(name="Binary01", value="Binary01"),
        app_commands.Choice(name="Cream01", value="Cream01"),
        app_commands.Choice(name="Divine01", value="Divine01"),
        app_commands.Choice(name="Ever01", value="Ever01"),
    ]
class_=[
        app_commands.Choice(name="First", value="First"),
        app_commands.Choice(name="Double", value="Double"),
        app_commands.Choice(name="Special", value="Special"),
        app_commands.Choice(name="Premier", value="Premier"),
        app_commands.Choice(name="Welcome", value="Welcome"),
        app_commands.Choice(name="Zero", value="Zero"),
    ]
artist=[
        app_commands.Choice(name='tripleS', value='tripleS'),
        app_commands.Choice(name='ARTMS', value='ARTMS')
    ]
collection_array=[
        app_commands.Choice(name='3x3', value=9),
        app_commands.Choice(name='6x3', value=18),
        #app_commands.Choice(name='9x3', value=27),
]

season_color = ['#FFDD00', '#00FF00', '#FF7477', '#B301FE', '#33ecfd']
season_color_dict = {
        "Atom01": "#FFDD00",
        "Binary01": "#00FF00",
        "Cream01": "#FF7477",
        "Divine01": "#B301FE",
        "Ever01": "#33ecfd",
}

season_percent_value = {
                'Atom01': 0,
                'Binary01': 0,
                'Cream01': 0,
                'Divine01': 0,
                'Ever01': 0,
            }

season_names = []


como_contract = {
    'triples': "0x58AeABfE2D9780c1bFcB713Bf5598261b15dB6e5",
    'artms': '0x8254D8D2903B20187cBC4Dd833d49cECc219F32E',
}
objekt_contract = {
    'triples': "0xA4B37bE40F7b231Ee9574c4b16b7DDb7EAcDC99B",
    'artms': '0x0fB69F54bA90f17578a59823E09e5a1f8F3FA200',
}

# Month information
month_end = [31,28,31,30,31,30,31,31,30,31,30,31]
month_start = [4,7,7,3,5,1,3,6,2,    3,6,1] #2025, 2024


gravity_address = {
    'triples': "0xc3E5ad11aE2F00c740E74B81f134426A3331D950",
    'artms': "0x8466e6E218F0fe438Ac8f403f684451D20E59Ee3"
}