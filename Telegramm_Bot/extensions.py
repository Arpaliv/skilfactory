from config import currency_list, API_KEY
import requests
import json
import telebot


class APIException (Exception):
    pass


class APIWorker:
    @staticmethod
    def get_price(base, quote, amount):
        base = base
        quote = quote
        req = 'https://currate.ru/api/?get=rates&pairs=' + base + quote + '&key=' + API_KEY
        r = requests.get(req)
        text = json.loads(r.content)
        convert = float(text['data'][base + quote])
        answer = f'{amount}  {currency_list[base][0]} соответствуют {round(amount * convert, 2)} {currency_list[quote][0]}'
        return answer


class MessageHandler:
    @staticmethod
    def text_interpritator(text: str):
        try:
            if text.isdigit():
                return float(text)
            else:
                for key in currency_list:
                    for value in currency_list[key]:
                        if text == value:
                            return key
        except APIException(f'Валюта {text} не найдена!'):
            raise APIException

    @staticmethod
    def message_recipient(text: telebot.types.Message):
        answer = []
        text = text.lower()
        text = text.replace('"', '')
        text = text.replace("'", '')
        text = text.replace(',', '.')
        text = text.split(' ')
        while text.count(' ') > 0:
            text.pop(text.index(' '))
        if len(text) != 3:
            raise APIException('Неправильное количество параметров!')
        for _a in text:
            _a = MessageHandler.text_interpritator(_a)
            answer.append(_a)
        if answer[0] == answer[1]:
            raise APIException(f'Невозможно перевести одинаковые валюты {currency_list[answer[0]][0]}!')
        return APIWorker.get_price(answer[0], answer[1], answer[2])
