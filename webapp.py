import random
import time

from flask import Flask, render_template, request

from calcs import plot_expression

from llm_parser import text_to_expression

import logging
import numpy as np

from mistral_embed_demo import get_embedding, cosine_similarity
from llm_parser import check_relevance


# Docs and examples for Flask: https://flask.palletsprojects.com/en/stable/
app = Flask(__name__)  # To run, use flask --app webapp run --debug

messages_db = []  # list of dicts: {nick, text, embedding}

logging.basicConfig(
    filename="friend_app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


@app.route("/")  # http://127.0.0.1:5000/
def main_page():
    plot_file = ''
    user_input = ''  # TODO: real input

    if user_input.strip() != '':
        rnd_suffix = ''  # some random suffix to caching in browser
        plot_file = f"plot_{rnd_suffix}.png"
        plot_expression(user_input, 0, 4, f"static/{plot_file}")

    return render_template('plot_func.html')  # Add parameters for the template

@app.route("/test")  # http://127.0.0.1:5000/test
def test_route():
    x = random.randint(0, 10)

    return render_template('main_page.html', lucky_num=x)

@app.route("/plot_graph_api") # http://127.0.0.1:5000/plot_graph_api
def plot_graph_api():
    user_prompt = request.args.get('func_expr', '')

    if not user_prompt.strip():
        return {"error": "Empty input"}, 400

    # converts text to math expression
    func_expr = text_to_expression(user_prompt)

    rnd_suffix = random.randint(0, 1000000)
    plot_file = f"plot_{rnd_suffix}.png"

    plot_expression(func_expr, 0, 4, f"static/{plot_file}")

    return {
        'parsed_expression': func_expr,
        'plot_image_url': f'static/{plot_file}'
    }

@app.route("/friend", methods=["GET", "POST"]) # http://127.0.0.1:5000/friend
def find_friend():
    recommendations = []

    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        message = request.form.get("message", "").strip()

        if nickname and message:
            emb = get_embedding(message)

            # compute cosine similarity
            scored = []
            for item in messages_db:
                sim = cosine_similarity(emb, item["embedding"])
                scored.append((sim, item))

            scored.sort(reverse=True, key=lambda x: x[0])
            top3 = scored[:3]

            logging.info(f"NEW MESSAGE from {nickname}: {message}")
            logging.info(
                "TOP-3 COS SIM: " +
                ", ".join([f"{x[1]['nick']}={x[0]:.3f}" for x in top3])
            )

            # LLM filtering
            for sim, item in top3:
                if check_relevance(message, item["text"]):
                    recommendations.append({
                        "nick": item["nick"],
                        "text": item["text"],
                        "similarity": round(sim, 3)
                    })

            # store new message LAST (important!)
            messages_db.append({
                "nick": nickname,
                "text": message,
                "embedding": emb
            })

    return render_template(
        "friend.html",
        recommendations=recommendations
    )


