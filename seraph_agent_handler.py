import logging
import random
from logging.config import fileConfig

from aiogram import Router, types, F
from aiogram.dispatcher.filters import Command

import file_db
from config import ChatWarsAgentBot_id

fileConfig('logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)
router = Router()
db = file_db.Singleton()


@router.message(
    # F.chat.type == 'private',
    F.forward_from.id == ChatWarsAgentBot_id,
    F.text.startswith('Почти')
)
async def words_game(message: types.Message):
    lines = get_word_strings(message.text)
    pairs = get_word_pairs(lines)
    word = word_processing(pairs)
    text = color_processing(word)
    if message.chat.type == 'private':
        await message.answer(text)
    else:
        await message.reply(text)


@router.message(
    # F.chat.type == 'private',
    F.forward_from.id == ChatWarsAgentBot_id,
    F.text.startswith('🎉 Шикарно')
)
async def words_game_win(message: types.Message):
    lines = get_word_strings(message.text)
    pairs = get_word_pairs(lines)
    word = word_processing(pairs)
    text = 'Спасибо за список слов.\nОни могут быть добавлены в базу, если их не было.\nПоздравляю с победой'

    if message.chat.type == 'private':
        await message.answer(text)
    else:
        await message.reply(text)


@router.message(
    # F.chat.type == 'private',
    F.forward_from.id == ChatWarsAgentBot_id,
    F.text.startswith('Close one')
)
async def words_game_en(message: types.Message):
    lines = get_word_strings(message.text)
    pairs = get_word_pairs(lines)
    word = word_processing(pairs, language='en')
    text = color_processing(word)
    if message.chat.type == 'private':
        await message.answer(text)
    else:
        await message.reply(text)


@router.message(
    # F.chat.type == 'private',
    F.forward_from.id == ChatWarsAgentBot_id,
    F.text.startswith('🎉 Sweet')
)
async def words_game_en_win(message: types.Message):
    lines = get_word_strings(message.text)
    pairs = get_word_pairs(lines)
    word = word_processing(pairs, language='en')
    text = 'Thank You for the word list.\nThem will be added to the database, if not yet.\nCongratulations'
    if message.chat.type == 'private':
        await message.answer(text)
    else:
        await message.reply(text)


def color_processing(word):
    if word.is_loose:
        if word.language == 'ru':
            return 'Жаль что не угадали'
        elif word.language == 'en':
            return 'sad that you didn\'t guess'
    green = word.has_green()
    yellow = word.has_yellow()
    words = None
    if green is not None:
        words_fdb = db.words_get_by_exist_symbol(word.language, green)
        words = untuple_list(words_fdb)
    elif yellow is not None:
        words_fdb = db.words_get_by_exist_symbol(word.language, yellow)
        words = untuple_list(words_fdb)
    else:
        words_fdb = db.words_get_by_not_exist_symbol(word.language, word.black[0])
        words = untuple_list(words_fdb)
    words_len = len(words)
    words = search_green_variants(word, words)
    words_len = len(words)
    words = search_black_variants(word, words)
    words_len = len(words)
    words = search_yellow_variants(word, words)
    words_len = len(words)
    text = ''
    if word.language == 'ru':
        text = get_result_ready_for_ru_user(words)
    elif word.language == 'en':
        text = get_result_ready_for_en_user(words)
    return text


def get_word_strings(text):
    """
        'Почти!
    Попробуй угадать!

     Ц Е З А Р Ь
    ⬛️🟩⬛️🟨⬛️⬛️
     Б Е Д Л А М
    ⬛️🟩⬛️🟨🟨⬛️
     Г Е Е Н Н А
    🟨🟩🟨⬛️⬛️🟩

    Количество попыток: 3. 3 баллов можно получить. Ответь на это сообщение одним словом.'
        """
    lines = text.splitlines()
    res = []
    for line in lines:
        if line.casefold().startswith('почти'):
            continue
        elif line.casefold().startswith('попробуй'):
            continue
        elif line.casefold().startswith('🎉 Шикарно'.casefold()):
            continue
        elif line.casefold().startswith('🎉 Sweet'.casefold()):
            continue
        elif line.casefold().startswith('Close one'.casefold()):
            continue
        elif line.casefold().startswith('Try to guess'.casefold()):
            continue
        elif line.casefold().startswith('количество'.casefold()):
            break
        elif line.casefold().endswith('Reply to me with answer.'.casefold()):
            break
        elif line.casefold().startswith('Получно'.casefold()):
            break
        elif line.casefold().startswith('You earned'.casefold()):
            break
        elif line.casefold().startswith('Очень жаль, попытки закончились'.casefold()):
            li = line.split()
            line = li[-1].replace('.', '').casefold()
            db.words_add_word_if_new('ru', line)
            break
        elif line == '':
            continue
        else:
            res.append(line.replace(' ', '').replace('️', '').casefold())  # Второй реплейс для смайла двойного
    return res


def get_word_pairs(lines: list):
    pairs = {}
    while len(lines) > 0:
        key = lines.pop(0)
        value = lines.pop(0)
        pairs.update({key: value})
    return pairs


def word_processing(pairs: dict, language='ru'):
    keys = pairs.keys()
    word = Word(language=language)
    for key in keys:
        value = pairs.get(key)
        get_colored_word(key, value, word)
        db.words_add_word_if_new(language, key)
    if len(keys) == 6:
        word.is_loose = True
    return word


def get_colored_word(text, check, word):
    log.info(f'{text}: {check}')
    text_list = list(text)
    check_list = list(check)
    for i in range(0, 6):
        if check_list[i] == '🟩':
            word.green[i] = text_list[i]
            if text_list[i] in word.black:
                word.black.remove(text_list[i])
        elif check_list[i] == '🟨':
            if text_list[i] in word.black:
                word.black.remove(text_list[i])
            word.add_yellow(i, text_list[i])
        else:
            if text_list[i] not in word.green:
                if text_list[i] not in word.yellow:
                    word.add_black(text_list[i])
    return word


def untuple_list(words_fdb):
    words = []
    for word_fdb in words_fdb:
        words.append(word_fdb[0])
    return words


def search_green_variants(word, word_list: list):
    green = word.green
    for i in range(0, 6):
        bad_words = []
        if green[i] is None:
            continue
        for w in word_list:
            w_list = list(w)
            if w_list[i] != green[i]:
                bad_words.append(w)
        for bad in bad_words:
            word_list.remove(bad)
    return word_list


def search_black_variants(word, word_list: list):
    for black in word.black:
        bad_words = []
        for w in word_list:
            w_list = list(w)
            if black in w_list:
                bad_words.append(w)
        for bad in bad_words:
            word_list.remove(bad)
    return word_list


def search_yellow_variants(word, word_list: list):
    yellow = word.yellow
    for i in range(0, 6):
        bad_words = []
        if len(yellow[i]) == 0:
            continue
        for w in word_list:
            w_list = list(w)
            if w_list[i] in yellow[i]:
                bad_words.append(w)
        for bad in bad_words:
            word_list.remove(bad)
    for char in word.chars:
        bad_words = []
        for w in word_list:
            if char not in list(w):
                bad_words.append(w)
        for bad in bad_words:
            word_list.remove(bad)
    return word_list


def get_result_ready_for_ru_user(words: list):
    text = ''
    l = len(words)
    text += f'Подходящих вариантов найдено: {l}\n'
    if l > 20:
        text += 'случайная выборка из 20 возможно подходящих вариантов:\n'
        r20 = random.choices(words, k=20)
        for i in range(0, 20):
            text += f'{i + 1:02d}. {r20[i].swapcase()}\n'
    elif l <= 0:
        text += 'Держитесь там как нибудь'
    else:
        for i in range(0, l):
            text += f'{i + 1:02d}. {words[i].swapcase()}\n'
    return text


def get_result_ready_for_en_user(words: list):
    text = ''
    l = len(words)
    text += f'Suitable guesses found: {l}\n'
    if l > 20:
        text += 'Random 20 possible guesses:\n'
        r20 = random.choices(words, k=20)
        for i in range(0, 20):
            text += f'{i + 1:02d}. {r20[i].swapcase()}\n'
    elif l <= 0:
        text += 'Sorry, I don\t know this word!'
    else:
        for i in range(0, l):
            text += f'{i + 1:02d}. {words[i].swapcase()}\n'
    return text


class Word:
    green = [None, None, None, None, None, None]
    yellow = [[], [], [], [], [], []]
    black = []
    chars = []
    language: str
    is_loose: bool = False

    def __init__(self, language='ru'):
        self.green = [None, None, None, None, None, None]
        self.yellow = [[], [], [], [], [], []]
        self.black = []
        self.chars = []
        self.language = language
        self.is_loose = False

    def add_black(self, s):
        if s not in self.black:
            if s not in self.chars:
                self.black.append(s)

    def add_yellow(self, i, s):
        if s not in self.yellow[i]:
            self.yellow[i].append(s)
        if s not in self.chars:
            self.chars.append(s)
        if s in self.black:
            self.black.remove(s)

    def has_green(self):
        for g in self.green:
            if g is not None:
                return g
        return None

    def has_yellow(self):
        if len(self.chars) > 0:
            return self.chars[0]
        return None
