import json
import os
import threading
import webbrowser

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_FILE = "/app/data/dictionary.json"


def load_dictionary():
    if not os.path.exists(DICTIONARY_FILE):
        return {}

    try:
        with open(DICTIONARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_dictionary(dictionary):
    with open(DICTIONARY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dictionary,
            f,
            ensure_ascii=False,
            indent=2,
        )


dictionary = load_dictionary()


@app.route("/")
def index():
    return render_template("index.html", dictionary=dictionary)


@app.post("/replace")
def replace_text():
    data = request.get_json()

    text = data.get("text", "")

    # Сначала более длинные слова.
    # Это помогает избежать частичных совпадений.
    replacements = sorted(
        dictionary.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    result = text

    for old, new in replacements:
        result = result.replace(old, new)

    return jsonify({"result": result})

@app.post("/replace/reverse")
def replace_text_reverse():
    data = request.get_json()

    text = data.get("text", "")

    # Обратный словарь:
    # значение замены -> исходное значение
    reverse_dictionary = {}

    for old, new in dictionary.items():
        # Если несколько исходных значений имеют
        # одинаковую замену, однозначно восстановить
        # исходное значение невозможно.
        if new not in reverse_dictionary:
            reverse_dictionary[new] = old

    # Сначала заменяем более длинные значения.
    replacements = sorted(
        reverse_dictionary.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    result = text

    for new, old in replacements:
        result = result.replace(new, old)

    return jsonify({"result": result})

@app.post("/dictionary/add")
def add_dictionary_entry():
    data = request.get_json()

    old = data.get("old", "")
    new = data.get("new", "")

    if not old:
        return jsonify({
            "success": False,
            "error": "Исходное слово не может быть пустым",
        }), 400

    dictionary[old] = new
    save_dictionary(dictionary)

    return jsonify({
        "success": True,
        "dictionary": dictionary,
    })


@app.post("/dictionary/delete")
def delete_dictionary_entry():
    data = request.get_json()

    old = data.get("old", "")

    if old in dictionary:
        del dictionary[old]
        save_dictionary(dictionary)

    return jsonify({
        "success": True,
        "dictionary": dictionary,
    })


@app.get("/dictionary")
def get_dictionary():
    return jsonify(dictionary)


def open_browser():
    webbrowser.open("http://0.0.0.0:5000")


if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )



