<!DOCTYPE html>
<html>
<head>
    <title>도서관 청구기호 조회</title>
</head>
<body>

<h2>책 제목 입력</h2>

<textarea id="books" rows="10" cols="50"></textarea><br><br>

<button onclick="searchBooks()">검색</button>

<h3>결과</h3>
<table border="1">
    <thead>
        <tr>
            <th>책 제목</th>
            <th>청구기호</th>
        </tr>
    </thead>
    <tbody id="result"></tbody>
</table>

<script>
async function searchBooks() {
    const books = document.getElementById("books").value
        .split("\n")
        .map(b => b.trim())
        .filter(b => b !== "");

    const res = await fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ books })
    });

    const data = await res.json();

    const resultTable = document.getElementById("result");
    resultTable.innerHTML = "";

    data.forEach(item => {
        const row = `<tr>
            <td>${item.book}</td>
            <td>${item.call_number}</td>
        </tr>`;
        resultTable.innerHTML += row;
    });
}
</script>

</body>
</html>
