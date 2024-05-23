from flask import Flask, request
from deeppavlov import build_model
from deeppavlov.core.commands.utils import parse_config

few_shot_roberta_model_module = Flask(__name__)

model_config = parse_config('few_shot_roberta')
model_config['chainer']['pipe'][-1]['confidence_threshold'] = 0.2
few_shot_roberta_model = build_model(model_config, download=True, install=True)

dataset = [
    ["Какой сюжет в игре", "facts"],
    ["В каком жанре выполнена игра", "facts"],
    ["На каком игровом движке сделана игра", "facts"],
    ["Что нужно делать в игре", "facts"],
    ["Где происходят действия игры", "facts"],
    ["Кем была выпущена игра", "facts"],
    ["Есть ли в игре мультиплеер", "facts"],
    ["Для каких платформ существует игра", "facts"],
    ["Как зовут главного героя", "facts"],
    ["С кем борется главный герой", "facts"],

    ["Похожие игры", "similar_games"],
    ["Во что похожего можно поиграть", "similar_games"],
    ["Какие схожие игры можно поиграть", "similar_games"],
    ["Во что подобное можно поиграть", "similar_games"],
    ["Подскажи подобные игры", "similar_games"],
    ["Схожие игры", "similar_games"],
    ["Есть ли ещё игры похожие на Holtine Miami", "similar_games"],
    ["Знаешь похожие игры", "similar_games"],
    ["Хочу похожую игру", "similar_games"],
    ["Есть похожие игры", "similar_games"],

    ["где купить", "where_to_buy"],
    ["как купить игру", "where_to_buy"],
    ["где продаётся игра", "where_to_buy"],
    ["в каких магазинах продаётся игра", "where_to_buy"],
    ["Я хочу купить игру", "where_to_buy"],
    ["где купить эту игру", "where_to_buy"],
    ["дай сайты где купить игру", "where_to_buy"],
    ["где можно купить игру", "where_to_buy"],
    ["я бы купил эту игру", "where_to_buy"],
    ["хорошая игра", "where_to_buy"]
]


def process_message(message_text):
    return few_shot_roberta_model([message_text], dataset)[0]


@few_shot_roberta_model_module.route('/few_shot', methods=["POST"])
def predict():
    data = request.json["data"]
    result = process_message(data)
    return {"result": result}


if __name__ == '__main__':
    print(few_shot_roberta_model([
        "какой сюжет в игре", "похожие игры", "где купить игру"
    ], dataset))
    few_shot_roberta_model_module.run(port=5002)
