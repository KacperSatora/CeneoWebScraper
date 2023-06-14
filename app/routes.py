from app import app
from flask import render_template, request, redirect, url_for
from app.utils import get_element
import requests
import json
import bs4 as BeautifulSoup
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/extract', methods=['POST','GET'])
def extract():
    if request.method == 'POST':
        product_code = request.form['product_id']
        all_opinions = []
    url = f"https://www.ceneo.pl/{product_code}#tab=reviews"
    while (url):
        print(url)
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        opinions = page.select("div.js_product-review")
        for opinion in opinions:
            single_opinion = {}
            for key, value in selectors.items():
                single_opinion[key] = get_element(opinion, *value)
            all_opinions.append(single_opinion)
        try:
            url = "https://www.ceneo.pl" + \
                get_element(page, "a.pagination__next", "href")
        except TypeError:
            url = None

    print(len(all_opinions))
    try:
        os.mkdir("./static/opinions")
    except FileExistsError:
        pass
    with open(f"./opinions/{product_code}.json", "w", encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)

    
    opinions = pd.read_json(f"./opinions/{product_code}.json")
    # opinions.score = opinions.score.map(
    #     lambda x: float(x[:-2].replace(",", ".")))

    opinions.score = opinions.score.map(
        lambda x: float(x.split("/")[0].replace(",", ".")))
    stats = {
        "pros_count": int(opinions.pros.map(bool).sum()),
        "cons_count": int(opinions.cons.map(bool).sum()),
        "avg_score": opinions.score.mean().round(2)
    }
    

    # opinions_count = len(opinions.index)
    opinions_count = opinions.shape[0]



    # histogram częstości występowania poszczególnych ocen
    score = opinions.score.value_counts().reindex(
        list(np.arange(0, 5.5, 0.5)), fill_value=0)
    # print(score)
    score.plot.bar(color="hotpink")
    plt.xticks(rotation=0)
    plt.title("Histogram ocen")
    plt.xlabel("Liczba gwiazdek")
    plt.ylabel("Liczba opinii")
    plt.ylim(0,max(score.values)+10)
    for index, value in enumerate(score):
        plt.text(index, value + 0.5, str(value), ha="center")
    # plt.show()
    try:
        os.mkdir("./plots")
    except FileExistsError:
        pass
    plt.savefig(f"./plots/{product_code}_score.png")
    plt.close()

    # udział poszczególnych rekomendacji w ogólnej liczbie opinii
    recommendation = opinions["recommendation"].value_counts(
        dropna=False).sort_index()
    print(recommendation)
    recommendation.plot.pie(
        label="",
        autopct="%1.1f%%",
        labels=["Nie polecam", "Polecam", "Nie mam zdania"],
        colors=["crimson", "forestgreen", "gray"]
    )
    plt.legend(bbox_to_anchor=(1.0, 1.0))
    plt.savefig(f"./plots/{product_code}_recommendation.png")
    plt.close()
    stats['score'] = score.to_dict()
    stats['recommendation'] = recommendation.to_dict()
    

    return render_template("extract.html")

@app.route('/product/<product_code>')
def product(product_code):
    return render_template("product.html", product_code=product_code)

@app.route('/products')
def products():
    return render_template("products.html")

@app.route('/author')
def author():
    return render_template("author.html")

selectors = {
    "opinion_id": [None, "data-entry-id"],
    "author": ["span.user-post__author-name"],
    "recommendation": ["span.user-post__author-recomendation > em"],
    "score": ["span.user-post__score-count"],
    "purchased": ["div.review-pz"],
    "published_at": ["span.user-post__published > time:nth-child(1)", "datetime"],
    "purchased_at": ["span.user-post__published > time:nth-child(2)", "datetime"],
    "thumbs_up": ["button.vote-yes > span"],
    "thumbs_down": ["button.vote-no > span"],
    "content": ["div.user-post__text"],
    "pros": ["div.review-feature__col:has(> div.review-feature__title--positives) > div.review-feature__item", None, True],
    "cons": ["div.review-feature__col:has(> div.review-feature__title--negatives) > div.review-feature__item", None, True]
}