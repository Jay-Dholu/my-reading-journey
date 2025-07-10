import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from flask import Flask, session, flash, redirect, render_template, url_for, make_response
from flask_wtf.csrf import CSRFProtect

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from sqlalchemy.exc import IntegrityError

from forms import Book, Login, SignUp, Data
from models import Record, User, db

load_dotenv("")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

csrf = CSRFProtect(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/home")
def home():
    json_form = Data()
    if not session.get('user_id'):
        flash("Please log in to add a book.", "warning")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    books = []

    if user_id:
        user = User.query.get(user_id)
        if user:
            books = Record.query.filter_by(user_id=user.id).order_by(Record.reading_started.desc()).all()

    return render_template("index.html", title="Home | My Reading Journey", books=books, json_form=json_form)


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    form = SignUp()
    json_form = Data()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        existing_email = User.query.filter_by(email=form.email.data).first()
        existing_userid = User.query.filter_by(userid=form.userid.data).first()

        if existing_email and existing_userid:
            flash("Email and User ID already taken. Please choose another.", "danger")
            return redirect(url_for('sign_up'))

        if existing_email:
            flash("Email already taken. Please choose another.", "danger")
            return redirect(url_for('sign_up'))

        if existing_userid:
            flash("User ID already taken. Please choose another.", "danger")
            return redirect(url_for('sign_up'))

        new_user = User(
            name=form.name.data,
            userid=form.userid.data,
            email=form.email.data,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('User ID already exists. Please choose a different one.', 'danger')

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))
    
    return render_template("sign_up.html", title='Sign Up | My Reading Journey', form=form, json_form=json_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    json_form = Data()

    if form.validate_on_submit():
        user = None
        identifier = None

        if form.email.data:
            user = User.query.filter_by(email=form.email.data).first()
            identifier = "email"
        elif form.userid.data:
            user = User.query.filter_by(userid=form.userid.data).first()
            identifier = "userid"

        if not user:
            flash(f"{identifier.title().replace('id', ' ID')} does not exist!", "warning")
            return redirect(url_for('login'))

        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session.permanent = True
            flash(f"Welcome {user.name}", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html", title='Login | My Reading Journey', form=form, json_form=json_form)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('home'))


@app.route("/about")
def about():
    json_form = Data()
    return render_template('about.html', title='About | My Reading Journey', json_form=json_form)


@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if not session.get('user_id'):
        flash("Please log in to add a book.", "warning")
        return redirect(url_for('login'))

    form = Book()
    json_form = Data()

    if form.validate_on_submit():
        filename = None
        if form.cover_image.data:
            image = form.cover_image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_book = Record(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            rating=form.rating.data,
            description=form.description.data,
            cover_image=filename,
            reading_started = form.reading_started.data,
            reading_finished = form.reading_finished.data,
            user_id=session.get('user_id'),
        )
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template("add_book.html", title="Add Book | My Reading Journey", json_form=json_form, form=form)


@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Record.query.get_or_404(book_id)
    form = Book(obj=book)
    json_form = Data()

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.genre = form.genre.data
        book.rating = form.rating.data
        book.description = form.description.data
        book.reading_started = form.reading_started.data
        book.reading_finished = form.reading_finished.data

        if form.cover_image.data:
            image = form.cover_image.data
            filename = secure_filename(image.filename)

            if filename:
                upload_path = os.path.join(app.root_path, 'static/uploads', filename)
                image.save(upload_path)
                book.cover_image = filename

        db.session.commit()
        flash("Book updated successfully!", "success")
        return redirect(url_for("home"))

    return render_template("edit_book.html", title='Edit | My Reading Journey', json_form=json_form, form=form, book=book)


@app.route("/delete_book/<int:book_id>", methods=['POST', 'GET'])
def delete_book(book_id):
    book = Record.query.get_or_404(book_id)
    name = book.title

    if book.user_id != session.get('user_id'):
        flash("You don't have permission to delete this book.", "danger")
        return redirect(url_for('home'))

    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{name}' deleted successfully!", "success")
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def view_book(book_id):
    book = Record.query.get_or_404(book_id)
    json_form = Data()
    return render_template('book_details.html', title=f'{book.title} | My Reading Journey', book=book, json_form=json_form)


@app.route("/download", methods=['GET'])
def download_books():
    if not session.get('user_id'):
        flash("Please login to download books!", "warning")
        return redirect(url_for('login'))
    
    user_id = session["user_id"]
    books = Record.query.filter_by(user_id=user_id).all()

    if not books:
        flash("You have no books to download", "info")
        return redirect(url_for('home'))

    book_data = []
    for book in books:
        book_data.append({
            "title": book.title,
            "author": book.author if book.author else None,
            "genre": book.genre if book.genre else None,
            "rating": book.rating if book.rating else None,
            "description": book.description if book.description else None,
            "reading_started": book.reading_started.isoformat() if book.reading_started else None,
            "reading_finished": book.reading_finished.isoformat() if book.reading_finished else None,
            "cover_image": book.cover_image if book.cover_image else None
        })

    response = make_response(json.dumps(book_data, indent=4))
    response.headers["Content-Disposition"] = "attachment; filename=books_backup.json"
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/upload", methods=["POST"])
def upload_books():
    if not session.get("user_id"):
        flash("Please login to upload books!", "warning")
        return redirect(url_for("login"))

    form = Data()
    if form.validate_on_submit():
        file = form.json_file.data

        try:
            data = json.load(file)
        except json.JSONDecodeError:
            flash("Invalid JSON format.", "danger")
            return redirect(url_for("home"))

        user_id = session["user_id"]

        for entry in data:
            title = entry.get("title") or None
            author = entry.get("author") or None
            genre = entry.get("genre") or None
            description = entry.get("description") or None
            cover_image = entry.get("cover_image") or None
            rating = entry.get("rating")

            try:
                rating = float(rating) if rating is not None else 0.0
            except ValueError:
                rating = 0.0

            def parse_date(value):
                try:
                    return datetime.fromisoformat(value) if value else None
                except (ValueError, TypeError):
                    return None

            reading_started = parse_date(entry.get("reading_started"))
            reading_finished = parse_date(entry.get("reading_finished"))

            new_book = Record(
                title=title,
                author=author,
                genre=genre,
                rating=rating,
                description=description,
                cover_image=cover_image,
                reading_started=reading_started,
                reading_finished=reading_finished,
                user_id=user_id
            )
            db.session.add(new_book)

        db.session.commit()
        flash("Data uploaded successfully!", "success")
        return redirect(url_for("home"))

    flash("Upload failed. Please ensure file is valid JSON.", "danger")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
