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
            "search_type": "simple"   # 🔥 여기 바뀜
        }

        res = requests.get(BASE_SEARCH_URL, params=params)
        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 결과에서 링크 직접 찾기
        links = soup.find_all("a", href=True)

        detail_links = []
        for a in links:
            if "dataView.php" in a["href"]:
                detail_links.append(a["href"])

        if not detail_links:
            return "검색 결과 없음"

        # 중복 제거
        detail_links = list(dict.fromkeys(detail_links))

        # 여러 개 시도
        for link in detail_links[:5]:
            detail_url = BASE_URL + link

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
