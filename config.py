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


season_color = ['#FFDD00', '#00FF00', '#FF7477', '#B301FE', '#33ecfd']
season_color_dict = {
        "atom": "#FFDD00",
        "binary": "#00FF00",
        "cream": "#FF7477",
        "divine": "#B301FE",
        "ever": "#33ecfd",
}
season_names = []