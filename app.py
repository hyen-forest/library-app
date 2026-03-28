from flask import Flask, render_template, request, jsonify
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_SEARCH_URL = "https://lib.changwon.go.kr/book/search.php"
BASE_DETAIL_URL = "https://lib.changwon.go.kr/book/dataView.php"

def get_call_number(book_name):
    try:
        params = {
            "lib_code": "cl",
            "search_keyword": book_name,
            "search_type": "detail"
        }

        res = requests.get(BASE_SEARCH_URL, params=params)
        html = res.text

        # 🔥 핵심: book_key 직접 추출
        keys = re.findall(r"book_key=(\d+)", html)

        if not keys:
            return "검색 결과 없음"

        # 중복 제거
        keys = list(dict.fromkeys(keys))

        # 여러 개 시도
        for key in keys[:5]:
            detail_params = {
                "lib_code": "cl",
                "book_key": key,
                "manage_code": "PA",
                "page_type": "search"
            }

            detail_res = requests.get(BASE_DETAIL_URL, params=detail_params)
            soup = BeautifulSoup(detail_res.text, "html.parser")

            rows = soup.select("table tr")

            for row in rows:
                if "청구기호" in row.text:
                    td = row.find("td")
                    if td and td.text.strip():
                        return td.text.strip()

        return "청구기호 없음"

    except Exception as e:
        return f"오류: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    books = data.get("books", [])

    results = []

    for book in books:
        call_number = get_call_number(book)
        results.append({
            "book": book,
            "call_number": call_number
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run()
