import deepl_api


def deepl_lang(lang_code):
    lang_code = str(lang_code)
    languages = {
        "ko": 'KO',
        "en-US": 'EN-US',
        "en-GB": 'EN-GB',
        "bg": 'BG',
        "zh-CN": 'ZH',
        "zh-TW": 'ZH',
        #"hr": croatian,
        "cs": 'CS',
        "id": 'ID',
        "da": 'DA',
        "nl": 'NL',
        "fi": 'FI',
        "fr": 'FR',
        "de": 'DE',
        "el": 'EL',
        #"hi": hindi,
        "hu": 'HU',
        "it": 'IT',
        "ja": 'JA',
        "lt": 'LT',
        "no": 'NB',
        "pl": 'PL',
        "pt-BR": 'PT-BR',
        "ro": 'RO',
        "ru": 'RU',
        "es-ES": 'ES',
        "sv-SE": 'SV',
        #"th": thai,
        "tr": 'TR',
        "uk": 'UK',
        #"vi": vietnamese
        # 필요한 만큼 추가할 수 있습니다.
    }

    return languages.get(lang_code, 'EN-US')

def translate(txt: str, lang, default = 'en-US'):
    lang = str(lang)
    if lang == default:
        return txt
    return str(deepl_api.translate(txt, deepl_lang(lang)))