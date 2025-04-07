import os
from pprint import pprint
from sys import prefix

import deepl


deepl_api = os.getenv('deepl_api')
auth_key = deepl_api  # Replace with your key
translator = deepl.Translator(auth_key)



# Glossary 만들기
glossary_name = "EN2KR_Original"
source_lang = "EN"  # 소스 언어
target_lang = "KO"

# 용어 목록 정의 (단어 -> 동일한 단어로 유지)
entries = {
    "objekt": "Objekt",
    "tripleS": "tripleS",
    "first": "First",
    "second": "Second",
    "third": "Third",
    "special": "Special",
    "premier": "Premier",
    "atom": "Atom",
    "binary": "Binary",
    "cream": "Cream",
    "divine": "Divine",
    "ever": "Ever",
    "Gifted": "증정합니다.",
}


def makeGlossary(entries, glossary_name, source_lang, target_lang):

    #Glossary 생성
    glossary = translator.create_glossary(glossary_name, source_lang, target_lang, entries)
    print(glossary)

#makeGlossary(entries, glossary_name, source_lang, target_lang) # 32515198-5c2c-4291-8f88-8125928e7c64

def removeGlossary_all():
    a = translator.list_glossaries()
    for b in a:
        print(b)
        translator.delete_glossary(b)

def showGlossary_all():
    a = translator.list_glossaries()
    for b in a:
        print(b)


#showGlossary_all()
#removeGlossary_all()

def translate(text, lang):
    print(lang)
    if lang == 'KO':
        glossary = '32515198-5c2c-4291-8f88-8125928e7c64'
        print('적용!')
    else:
        glossary = None

    result = translator.translate_text(text, target_lang=lang, glossary=glossary, source_lang='EN')
    return result

#print(translate("""Gifted to attendees of the 'tripleS Come True' world tour.""", 'KO'))  # "Bonjour, le monde !"