from flask import Flask, render_template, request
import requests
from book import Book


app = Flask(__name__)
APIKEY = "AIzaSyAopt9TPwB3x_wIObGU-kczXh4petc66B4"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        books = []
        query = request.form.get("query")
        result = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&key={APIKEY}").json()
        for item in result["items"]:
            volume_info = item.get("volumeInfo", {})
            title = volume_info.get("title", "No Title Available")
            subtitle = volume_info.get("subtitle", "No Subtitle Available")
            publisher = volume_info.get("publisher", "No Publisher Listed")
            publishDate = volume_info.get("publishedDate", "No Publish Date Available")
            authors = volume_info.get("authors", ["No Authors Listed"])
            thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "/static/assets/img/default.png")
            description = volume_info.get("description", "No Description Available")
            id = item.get("id")
            
            book = Book(title, publishDate, subtitle, publisher, authors, thumbnail, description, id)
            books.append(book)
        return render_template("search.html", books=books)
    else:
        return render_template("search.html", books=[])
    
@app.route("/search/details/", methods=["POST", "GET"])
def details():
    if request.method == "GET":
        return render_template("portfolio-details.html")
    else:
        book = request.form.get("book")
        return render_template("portfolio-details.html", book=book)

@app.route("/mylib")
def mylib():
    # return render_template("search.html")
    pass
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)