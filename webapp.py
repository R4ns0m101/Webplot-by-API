import random
import time

from flask import Flask, render_template, request

from calcs import plot_expression

from llm_parser import text_to_expression

# Docs and examples for Flask: https://flask.palletsprojects.com/en/stable/
app = Flask(__name__)  # To run, use flask --app webapp run --debug

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

