from flask import Flask, render_template, request, redirect, url_for
import requests
from book import Book, RBook
import sqlite3
from sqlite3 import Error
import hashlib
from datetime import datetime

connectionpath = "./freader.db"


def dateEncoder(date, mode):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if mode == "date":
        try:
        # Convert named date to YYYY MM DD
            fdate = date.replace(",", "")
            fdate = fdate.split(" ")
            month = months.index(fdate[0])+1
            day = fdate[1][:-2]
            if len(day) == 1:
                day = f"0{day}"
            elif len(str(month)) == 1:
                month = f"0{month}"
            year = fdate[2]
            return f"{year}-{month}-{day}"
        except:
            return date
    else:
        try:
            fdate = date.split("-")
            year = fdate[0]
            month = fdate[1]
            day = fdate[2]
            
            # Convert month to name
            
            month = months[int(month) - 1]
            
            # Convert day to name
            if day[-1] == "1":
                day = f"{day}st"
            elif day[-1] == "2":
                day = f"{day}nd"
            elif day[-1] == "3":
                day = f"{day}rd"
            else:
                day = f"{day}th"
            
            return f"{month} {day}, {year}"
        except:
            return date

def hashgen(password):
    salt = "2e78f89c6"
    passwordtohash = password + salt
    return hashlib.sha256(passwordtohash.encode()).hexdigest()
def get_connection(file):
    conn = None
    try:
        conn = sqlite3.connect(file)
        return conn
    except Error as e:
        print(e)
    return conn

app = Flask(__name__)
APIKEY = "AIzaSyAopt9TPwB3x_wIObGU-kczXh4petc66B4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Kids/OneDrive/Documents/Python/Reader/freader.db'  # Replace with your database URI

@app.route("/")
def home():
    return render_template("index.html", user=request.cookies.get("sessioncookie"))

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
            
            authors = ", ".join(authors)
            
            book = Book(title, publishDate, subtitle, publisher, authors, thumbnail, description, id)
            books.append(book)
        return render_template("search.html", books=books, user=request.cookies.get("sessioncookie"))
    else:
        return render_template("search.html", books=[], user=request.cookies.get("sessioncookie"))

@app.route("/mylib", methods=["POST", "GET"])
def mylib():
    if request.method == "POST":
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            c.execute(f"DELETE FROM addedbooks WHERE book_id = {request.form.get('book_id')}")
            book = c.fetchone()
            c.close()
        user_id = request.cookies.get('sessioncookie')
        if user_id:
            with get_connection(connectionpath) as conn:
                c = conn.cursor()
                c.execute(f"SELECT * FROM accounts WHERE user_id = {user_id}")
                user = c.fetchone()
                c.close()
            if user:
                with get_connection(connectionpath) as conn:
                    c = conn.cursor()
                    c.execute(f"SELECT * FROM addedbooks WHERE user_id = {user_id}")
                    books = c.fetchall()
                    c.close()
                rbooks = []
                for book in books:
                    print(book)
                    rbook = RBook(book[2], book[6], book[4], book[5], book[3], book[7], book[8], book[0], book[9], dateEncoder(book[10], "natural"), dateEncoder(book[11], "natural"))
                    rbooks.append(rbook)

                def days_between(d1, d2):
                    try:
                        d1 = datetime.strptime(d1, "%Y-%m-%d")
                        d2 = datetime.strptime(d2, "%Y-%m-%d")
                        return abs((d2 - d1).days)
                    except ValueError:
                        return "Invalid date"
                app.jinja_env.globals.update(days_between=days_between)
                return render_template("mybooks.html", books=rbooks , days_between=days_between, user=request.cookies.get("sessioncookie"))
            else:
                return redirect(url_for('login', redirection="mylib"))
        else:
            return redirect(url_for('login', redirection="mylib"))
    else:
        user_id = request.cookies.get('sessioncookie')
        if user_id:
            with get_connection(connectionpath) as conn:
                c = conn.cursor()
                c.execute(f"SELECT * FROM accounts WHERE user_id = {user_id}")
                user = c.fetchone()
                c.close()
            if user:
                books = []
                with get_connection(connectionpath) as conn:
                    c = conn.cursor()
                    c.execute(f"SELECT * FROM addedbooks WHERE user_id = {user_id}")
                    books = c.fetchall()
                    c.close()
                rbooks = []
                for book in books:
                    print(book)
                    rbook = RBook(book[2], book[6], book[4], book[5], book[3], book[7], book[8], book[0], book[9], dateEncoder(book[10], "natural"), dateEncoder(book[11], "natural"))
                    rbooks.append(rbook)

                def days_between(d1, d2):
                    try:
                        d1 = datetime.strptime(d1, "%Y-%m-%d")
                        d2 = datetime.strptime(d2, "%Y-%m-%d")
                        return abs((d2 - d1).days)
                    except ValueError:
                        return "Invalid date"
                app.jinja_env.globals.update(days_between=days_between)
                return render_template("mybooks.html", books=rbooks , days_between=days_between, user=request.cookies.get("sessioncookie"))
            else:
                return redirect(url_for('login', redirection="mylib"))
            
        else:
            return redirect(url_for('login', redirection="mylib"))
    
@app.route("/about")
def about():
    return render_template("about.html", user=request.cookies.get("sessioncookie"))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        
        return render_template("login.html", user=request.cookies.get("sessioncookie"))
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashgen(password)
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM accounts WHERE email = '{email}' AND password = '{hashed_password}'")
            user = c.fetchone()
            c.close()
        if user:
            # Success!
            response = redirect(url_for("mylib"))
            response.set_cookie('sessioncookie', str(user[0]))
            return response
        else:
            return redirect(url_for('signup'))

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", user=request.cookies.get("sessioncookie"))
    else:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashgen(password)
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            c.execute(f"INSERT INTO accounts (username, email, password) VALUES ('{username}','{email}', '{hashed_password}')")
            c.close()
        return redirect(url_for('login', redirection="mylib"))

@app.route("/search/addbook", methods=["POST"])
def addbook():
    user_id = request.cookies.get('sessioncookie')
    if user_id:
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM accounts WHERE user_id = {user_id}")
            user = c.fetchone()
            c.close()
        if user:
            # Success!
            if request.method == "POST":
                title = request.form.get("title")
                authors = request.form.get("authors")
                subtitle = request.form.get("subtitle")
                publisher = request.form.get("publisher")
                publishDate = request.form.get("publishedDate")
                thumbnail = request.form.get("thumbnail")
                description = request.form.get("description")
                id = request.form.get("id")
                book = Book(title, publishDate, subtitle, publisher, authors, thumbnail, description, id)
                return render_template("addbook.html", book=book, user=request.cookies.get("sessioncookie"))
        else:
            return redirect(url_for('login', redirection="addbook"))
    else:
        return redirect(url_for('login', redirection="addbook"))
    

@app.route("/search/addbook/submit", methods=["POST"])
def savebook():
    if request.method == "POST":
        title = request.form.get("title")
        authors = request.form.get("authors")
        subtitle = request.form.get("subtitle")
        publisher = request.form.get("publisher")
        publishDate = request.form.get("publishDate")
        thumbnail = request.form.get("thumbnail")
        description = request.form.get("description")
        id = request.form.get("id")
        rating = request.form.get("rating")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            print(''.join(authors))
            print(f"INSERT INTO addedbooks (user_id, book_title, book_authors, book_subtitle, book_publisher, book_publishdate, book_thumbnail, book_description, rating, started_reading, ended_reading) VALUES ('{request.cookies.get('sessioncookie')}', '{title}', '{authors}','{subtitle}','{publisher}','{publishDate}','{thumbnail}','{description}','{rating}','{start_date}','{end_date}')")
            try:
                c.execute(f"INSERT INTO addedbooks (user_id, book_title, book_authors, book_subtitle, book_publisher, book_publishdate, book_thumbnail, book_description, rating, started_reading, ended_reading) VALUES (\"{request.cookies.get('sessioncookie')}\", \"{title}\", \"{authors}\",\"{subtitle}\",\"{publisher}\",\"{publishDate}\",\"{thumbnail}\",\"{description}\",\"{rating}\",\"{start_date}\",\"{end_date}\")")
            except:
                return "<h1>Something definetly went wrong.</h1>\n<p>It could be because of these reasons:</p>\n<ul>\n<li>The book has data we could not process</li>\n<li>You have already added this book to your library</li>\n<li>You forgot to enter something</li>\n</ul>\n<h2>Sorry for the inconvenience</h2>\n<a href='/search'>Go Back</a>"
            c.close()
        return redirect(url_for('mylib'))
    
@app.route("/logout")
def logout():
    response = redirect(url_for("home"))
    response.set_cookie('sessioncookie', '', expires=0)
    return response
            
@app.route("/startreading", methods=["POST"])
def startreading():
    if request.method == "POST":
        title = request.form.get("title")
        authors = request.form.get("authors")
        subtitle = request.form.get("subtitle")
        publisher = request.form.get("publisher")
        publishDate = request.form.get("publishDate")
        thumbnail = request.form.get("thumbnail")
        description = request.form.get("description")
        description = description.replace('"','\"')
        start_date = datetime.today().strftime("%Y-%m-%d")
        print(f"INSERT INTO addedbooks (user_id, book_title, book_authors, book_subtitle, book_publisher, book_publishdate, book_thumbnail, book_description, rating, started_reading, ended_reading) VALUES (\"{request.cookies.get('sessioncookie')}\", \"{title}\", \"{authors}\",\"{subtitle}\",\"{publisher}\",\"{publishDate}\",\"{thumbnail}\",\"{description}\",\"{None}\",\"{start_date}\",\"{None}\")")
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            
            c.execute(f"INSERT INTO addedbooks (user_id, book_title, book_authors, book_subtitle, book_publisher, book_publishdate, book_thumbnail, book_description, rating, started_reading, ended_reading) VALUES (\"{request.cookies.get('sessioncookie')}\", \"{title}\", \"{authors}\",\"{subtitle}\",\"{publisher}\",\"{publishDate}\",\"{thumbnail}\",\"{description}\",\"{None}\",\"{start_date}\",\"{None}\")")
            
            c.close()
        return redirect(url_for("mylib"))

@app.route("/edit", methods=["POST"])
def edit():
    user_id = request.cookies.get('sessioncookie')
    if user_id:
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            c.execute(f"SELECT * FROM accounts WHERE user_id = {user_id}")
            user = c.fetchone()
            c.close()
        if user:
            # Success!
            if request.method == "POST":
                title = request.form.get("title")
                authors = request.form.get("authors")
                subtitle = request.form.get("subtitle")
                publisher = request.form.get("publisher")
                publishDate = request.form.get("publishDate")
                thumbnail = request.form.get("thumbnail")
                description = request.form.get("description")
                id = request.form.get("id")
                rating = request.form.get("rating")
                start_date = dateEncoder(request.form.get("start_date"), mode="date")
                end_date = dateEncoder(request.form.get("end_date"), mode="date")
                book = RBook(title, publishDate, subtitle, publisher, authors, thumbnail, description, id, rating, start_date, end_date)
                return render_template("edit.html.jinja", book=book, user=request.cookies.get("sessioncookie"))
        else:
            return redirect(url_for('login', redirection="edit"))
    else:
        return redirect(url_for('login', redirection="edit"))
     
@app.route("/editbook", methods=["POST"])
def editbook():
    if request.method == "POST":
        id = request.form.get("id")
        title = request.form.get("title")
        subtitle = request.form.get("subtitle")
        authors = request.form.get("authors")
        publisher = request.form.get("publisher")
        publishedDate = request.form.get("publishedDate")
        thumbnail = request.form.get("thumbnail")
        description = request.form.get("description")
        rating = request.form.get("rating")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            try:
                c.execute(f"UPDATE addedbooks SET book_title = \"{title}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_subtitle = \"{subtitle}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_authors = \"{authors}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_publisher = \"{publisher}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_publishdate = \"{publishedDate}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_thumbnail = \"{thumbnail}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET book_description = \"{description}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET rating = \"{rating}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET started_reading = \"{start_date}\" WHERE book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET ended_reading = \"{end_date}\" WHERE book_id = \"{id}\"")
            except Error as e:
                print(e)
                return "<h1>Error</h1>"
            c.close()
        return redirect(url_for("mylib"))
               

@app.route("/finish", methods=["POST"])
def finish():
    if request.method == "POST":
        id = request.form.get("id")
        title = request.form.get("title")
        end_date = request.form.get("end_date")
        rating = request.form.get("rating")
        with get_connection(connectionpath) as conn:
            c = conn.cursor()
            try:
                c.execute(f"UPDATE addedbooks SET ended_reading = \"{dateEncoder(end_date, mode='date')}\" WHERE book_title = \"{title}\" AND book_id = \"{id}\"")
                c.execute(f"UPDATE addedbooks SET rating = \"{rating}\" WHERE book_title = \"{title}\" AND book_id = \"{id}\"")

            except Error as e:
                print(e)
                return "<h1>Error</h1>"
            c.close()
        return redirect(url_for("mylib"))
@app.route("/finishbook", methods=["POST"])
def finishbook():
    id = request.form.get("id")
    title = request.form.get("title")
    subtitle = request.form.get("subtitle")
    authors = request.form.get("authors")
    publisher = request.form.get("publisher")
    publishedDate = request.form.get("publishedDate")
    thumbnail = request.form.get("thumbnail")
    description = request.form.get("description")
    rating = request.form.get("rating")
    start_date = request.form.get("start_date")
    end_date = datetime.today().strftime("%Y-%m-%d")
    book = RBook(title, publishedDate, subtitle, publisher, authors, thumbnail, description, id, rating, start_date, end_date)
    return render_template("finish.html", book=book)
    
    

if __name__ == "__main__":
    app.run(debug=True)