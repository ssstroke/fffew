from deeppavlov import build_model
from flask import Flask, request

squad_ru_bert_model_module = Flask(__name__)

squad_ru_bert_model = build_model('squad_ru_bert', download=True, install=True)
content = open('context.txt', 'r', encoding='utf-8').read()


def process_message(message_text):
    answer = squad_ru_bert_model([content], [message_text])
    if abs(answer[2][0] - 1.) < 1e-3:
        return answer[0][0]
    elif answer[0][0] != '':
        return 'К сожалению, я не могу дать точного ответа на ваш вопрос.\nПопробуйте перефразировать его.'
    else:
        return ''


@squad_ru_bert_model_module.route('/squad_ru', methods=["POST"])
def predict():
    data = request.json["data"]
    print(data)
    result = process_message(data)  # Замените на вашу функцию модели
    print(result)
    return {"result": result}


if __name__ == '__main__':
    squad_ru_bert_model_module.run(port=5001)  # Укажите уникальный порт для каждой модели
