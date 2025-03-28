import os

import deepl


deepl_api = os.getenv('deepl_api')
auth_key = deepl_api  # Replace with your key
translator = deepl.Translator(auth_key)


def translate(text, lang):
    result = translator.translate_text(text, target_lang=lang)
    return result

#print(translate('nice!!', 'KO'))  # "Bonjour, le monde !"