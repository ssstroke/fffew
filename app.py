import json
import requests
from flask import Flask, request

app = Flask(__name__)
state = 'start_state'


def get_token():
    return "7080809279:AAGPHW4Gejko-JotbwCQvnXPWpdWLJ7m0xA"


def send_message(chat_id, text, reply_markup):
    method = "sendMessage"
    token = get_token()
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text, 'reply_markup': json.dumps(reply_markup)}
    requests.post(url, data=data)


@app.route('/', methods=["POST"])
def handle_message():
    global state
    chat_id = request.json["message"]["chat"]["id"]
    text = request.json["message"]["text"]

    match text:
        case "/start":
            state = 'start_state'
            send_message(chat_id, 'Привет!\n'
                                  'Я знаю всё о серии игр Hotline Miami. '
                                  'Я могу рассказать об игре, порекомендовать похожие игры, '
                                  'а также могу предоставить ссылки, где можно купить игру.', {"remove_keyboard": True})
        case _:
            send_message(chat_id, 'Пожалуйста, подождите несколько секунд', {"remove_keyboard": True})
            few_shot_answer = send_message_to_few_shot_roberta_model(text)["result"]
            print(few_shot_answer)
            match few_shot_answer:
                case 'facts':
                    check_and_process(chat_id, text, fact_processing)
                case 'similar_games':
                    check_and_process(chat_id, text, recommend_similar)
                case 'where_to_buy':
                    check_and_process(chat_id, text, where_to_buy)
                case 'oos':
                    send_message(chat_id, "К сожалению, я не могу понять ваш вопрос."
                                          "Попробуйте его перефразировать.", {"remove_keyboard": True})
                case _:
                    send_message(chat_id, "Ошибка сервера", {"remove_keyboard": True})

    return {"ok": True}


def send_message_to_few_shot_roberta_model(text):
    few_shot_result = requests.post("http://localhost:5002/few_shot", json={"data": str(text)}).json()
    return few_shot_result


def send_message_to_squad_ru_bert_model(text):
    few_shot_result = requests.post("http://localhost:5001/squad_ru", json={"data": str(text)}).json()
    return few_shot_result


def check_and_process(chat_id, text, process_function):
    global state
    if text != 'Назад':
        process_function(chat_id, text)
    else:
        state = 'start_state'
        send_message(chat_id, 'Что бы вы ещё хотели узнать? '
                              'Я могу рассказать об игре, порекомендовать похожие игры, '
                              'а также могу предоставить ссылки, где можно купить игру.',
                     {"remove_keyboard": True})


def fact_processing(chat_id, text):
    result = send_message_to_squad_ru_bert_model(text)["result"]
    if result != "":
        send_message(chat_id, result, {"keyboard": [["Назад"]], "resize_keyboard": True,
                                       "one_time_keyboard": False})


def recommend_similar(chat_id, text):
    send_message(chat_id,
                 "Похожие на Hotline Miami игры: "
                 "Katana: ZERO, Ruiner, Ghostrunner, Darkwood, Heat Signature, Furi.",
                 {"keyboard": [["Назад"]],
                  "resize_keyboard": True,
                  "one_time_keyboard": False})


def where_to_buy(chat_id, text):
    send_message(chat_id,
                 "Hotline Miami доступна для покупки в: "
                 "Steam: https://store.steampowered.com/app/219150/Hotline_Miami "
                 "Humble Bundle: https://www.humblebundle.com/store/agecheck/hotline-miami "
                 "GOG: https://www.gog.com/en/game/hotline_miami",
                 {"keyboard": [["Назад"]],
                  "resize_keyboard": True,
                  "one_time_keyboard": False})


if __name__ == '__main__':
    app.run()
