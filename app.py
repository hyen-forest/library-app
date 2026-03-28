from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_SEARCH_URL = "https://lib.changwon.go.kr/book/search.php"
BASE_URL = "https://lib.changwon.go.kr"

def get_call_number(book_name):
    try:
        params = {
            "lib_code": "cl",
            "search_keyword": book_name,
            "search_type": "detail"
        }

        res = requests.get(BASE_SEARCH_URL, params=params)
        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 모든 상세페이지 링크 가져오기
        links = soup.select("a[href*='dataView']")

        if not links:
            return "검색 결과 없음"

        # 🔥 여러 개 순회하면서 실제 청구기호 있는 것 찾기
        for link in links[:5]:  # 최대 5개까지만 검사
            detail_url = BASE_URL + link["href"]

            detail_res = requests.get(detail_url)
            detail_soup = BeautifulSoup(detail_res.text, "html.parser")

            rows = detail_soup.select("table tr")

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
