import requests
res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "anKyCfnpJiYHnlTkOD7Q", "isbns": "0345347951"})
print(res.json())
