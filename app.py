import os
import json
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer
from dotenv import load_dotenv

from flask import Flask, request, session, flash, redirect, render_template, url_for, make_response
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from markupsafe import Markup

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId

import cloudinary
import cloudinary.uploader

from forms import Book, Login, SignUp, Data, RequestReset, ResetPassword, ResendVerification, EditProfile

load_dotenv('.env')

app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
MONGO_URI = os.environ.get('MONGO_URI')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set! Please add it to your .env file and Render environment.")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    db = client.myreadingjourney
    users_collection = db.users
    books_collection = db.books
    users_collection.create_index("email", unique=True)
    users_collection.create_index("userid", unique=True)
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error: Could not connect to MongoDB Atlas. Check your MONGO_URI. \n{e}")
    client = None
    db = None
    users_collection = None
    books_collection = None


mail = Mail(app)
csrf = CSRFProtect(app)
s = Serializer(app.config['SECRET_KEY'])


def send_verification_email(user):
    token = s.dumps(user['email'], salt='email-confirm-salt')
    confirm_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message(
        "Confirm Your Email Address - My Reading Journey",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user['email']]
    )
    msg.html = render_template('verify_email.html', confirm_url=confirm_url, user=user)
    mail.send(msg)


@app.before_request
def check_user_session():
    if 'user_id' in session and users_collection is not None:
        try:
            user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
            if not user:
                session.clear()
                flash("Your session was invalid and has been cleared. Please log in again.", "warning")
        except Exception:
            session.clear()


@app.context_processor
def inject_user():
    current_user = None
    if 'user_id' in session and users_collection is not None:
        try:
            current_user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        except Exception:
            current_user = None
    return dict(current_user=current_user)


@app.route("/")
@app.route("/home")
def home():
    if not session.get('user_id'):
        flash("Please log in to view your bookshelf.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    books = []
    if users_collection is not None:
        books = list(books_collection.find({'user_id': ObjectId(user_id)}).sort('reading_started', 1))

    json_form = Data()
    return render_template("index.html", title="Home - My Reading Journey", books=books, json_form=json_form)


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    form = SignUp()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        if users_collection.find_one({"email": form.email.data}):
            flash("Email already taken. Please choose another.", "danger")
        elif users_collection.find_one({"userid": form.userid.data}):
            flash("User ID already taken. Please choose another.", "danger")
        else:
            new_user = {
                "name": form.name.data,
                "userid": form.userid.data,
                "email": form.email.data,
                "password": hashed_password,
                "theme": "light",
                "is_verified": False
            }
            users_collection.insert_one(new_user)
            send_verification_email(new_user)
            flash("Account created successfully! Please check your email to verify your account.", "success")
            return redirect(url_for('login'))

    return render_template("sign_up.html", title='Sign Up - My Reading Journey', form=form, json_form=Data())


@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=1800)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    user = users_collection.find_one({"email": email})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    if user.get('is_verified'):
        flash('Account already verified. Please log in.', 'info')
    else:
        users_collection.update_one({'_id': user['_id']}, {'$set': {'is_verified': True}})
        flash('Your account has been verified! You can now log in.', 'success')
        
    return redirect(url_for('login'))


@app.route("/resend_verification", methods=['GET', 'POST'])
def resend_verification():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = ResendVerification()
    if form.validate_on_submit():
        user = users_collection.find_one({"email": form.email.data})
        if user:
            if user.get('is_verified'):
                flash('This account has already been verified. Please log in.', 'info')
            else:
                send_verification_email(user)
                flash('A new verification email has been sent. Please check your inbox.', 'success')
        else:
            flash('If an account with that email exists, a new verification email has been sent.', 'success')
        return redirect(url_for('login'))
            
    return render_template('resend_verification.html', title='Resend Verification', form=form, json_form=Data())


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = None
        if form.email.data:
            user = users_collection.find_one({"email": form.email.data})
        elif form.userid.data:
            user = users_collection.find_one({"userid": form.userid.data})

        if user and check_password_hash(user["password"], form.password.data):
            if not user.get('is_verified'):
                message = Markup(f"Your account is not verified. <a href='{url_for('resend_verification')}' class='auth-link'>Resend verification email?</a>")
                flash(message, 'warning')
                return redirect(url_for('login'))
            
            session['user_id'] = str(user["_id"])
            session.permanent = True
            flash(f"Welcome {user['name']}", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please check your details and try again.", "danger")

    return render_template("login.html", title='Login - My Reading Journey', form=form, json_form=Data())
    

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('login'))


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if not session.get('user_id'):
        flash("You must be logged in to edit your profile.", "warning")
        return redirect(url_for('login'))

    try:
        user_oid = ObjectId(session.get('user_id'))
        user = users_collection.find_one({'_id': user_oid})
    except Exception:
        user = None

    if not user:
        flash("User not found. Please log in again.", "danger")
        session.clear()
        return redirect(url_for('login'))

    form = EditProfile()
    if form.validate_on_submit():
        email_changed = form.email.data != user['email']
        userid_changed = form.userid.data != user['userid']

        if email_changed and users_collection.find_one({'email': form.email.data}):
            flash('This Email Address is already taken. Please choose another one.', 'danger')
        elif userid_changed and users_collection.find_one({'userid': form.userid.data}):
            flash('This User ID is already taken. Please choose another one.', 'danger')
        else:
            update_data = {
                'name': form.name.data,
                'userid': form.userid.data,
                'email': form.email.data,
            }
            if form.password.data:
                update_data['password'] = generate_password_hash(form.password.data)
            
            users_collection.update_one({'_id': user_oid}, {'$set': update_data})
            flash("Profile updated successfully!", "success")
            return redirect(url_for('home'))

    if request.method == 'GET':
        form.name.data = user['name']
        form.userid.data = user['userid']
        form.email.data = user['email']

    return render_template('settings.html', title='Settings', form=form, json_form=Data())


@app.route("/delete_account", methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user_oid = ObjectId(user_id)
    books_collection.delete_many({'user_id': user_oid})
    users_collection.delete_one({'_id': user_oid})

    session.clear()
    flash("Your account and all associated data have been permanently deleted.", "success")
    return redirect(url_for('home'))


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    form = RequestReset()
    if form.validate_on_submit():
        user = users_collection.find_one({"email": form.email.data})
        if user:
            token = s.dumps(user['email'], salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset Request", recipients=[user['email']])
            msg.body = f"To reset your password, visit the following link:\n{reset_url}\n\nIf you did not make this request, ignore this email."
            mail.send(msg)
        flash(f"A password reset link has been sent to {form.email.data}.", "info")
        return redirect(url_for('login'))
    return render_template('forgot_password.html', title='Forgot Password', form=form, json_form=Data())


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash('The password reset link is invalid or has expired.', 'warning')
        return redirect(url_for('forgot_password'))
        
    user = users_collection.find_one({"email": email})
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        users_collection.update_one({'_id': user['_id']}, {'$set': {'password': hashed_password}})
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password', form=form, json_form=Data())


@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if not session.get('user_id'):
        flash("Please log in to add a book.", "warning")
        return redirect(url_for('login'))

    form = Book()
    if form.validate_on_submit():
        filename = None
        if form.cover_image.data:
            image = form.cover_image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_book = {
            "title": form.title.data,
            "author": form.author.data,
            "isbn": form.isbn.data,
            "genre": form.genre.data,
            "rating": float(form.rating.data) if form.rating.data else 0.0,
            "description": form.description.data,
            "cover_image": filename,
            "reading_started": datetime.combine(form.reading_started.data, datetime.min.time()) if form.reading_started.data else None,
            "reading_finished": datetime.combine(form.reading_finished.data, datetime.min.time()) if form.reading_finished.data else None,
            "user_id": ObjectId(session.get('user_id')),
        }
        books_collection.insert_one(new_book)
        flash("Book added successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template("add_book.html", title="Add Book", form=form, json_form=Data())


@app.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    try:
        book_oid = ObjectId(book_id)
    except:
        return "Invalid Book ID", 404

    book = books_collection.find_one({'_id': book_oid})
    if not book or str(book.get('user_id')) != session.get('user_id'):
        flash("Book not found or you don't have permission to edit it.", "danger")
        return redirect(url_for('home'))

    form = Book()
    if form.validate_on_submit():
        update_data = {
            "title": form.title.data,
            "author": form.author.data,
            "isbn": form.isbn.data,
            "genre": form.genre.data,
            "rating": float(form.rating.data) if form.rating.data else 0.0,
            "description": form.description.data,
            "reading_started": datetime.combine(form.reading_started.data, datetime.min.time()) if form.reading_started.data else None,
            "reading_finished": datetime.combine(form.reading_finished.data, datetime.min.time()) if form.reading_finished.data else None,
        }
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            form.cover_image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_data["cover_image"] = filename

        books_collection.update_one({'_id': book_oid}, {'$set': update_data})
        flash("Book updated successfully!", "success")
        return redirect(url_for("home"))
    
    if request.method == 'GET':
        form.title.data = book.get('title')
        form.author.data = book.get('author')
        form.isbn.data = book.get('isbn')
        form.genre.data = book.get('genre')
        form.rating.data = book.get('rating')
        form.description.data = book.get('description')
        form.reading_started.data = book.get('reading_started')
        form.reading_finished.data = book.get('reading_finished')

    return render_template("edit_book.html", title=f'Edit {book["title"]}', form=form, book=book, json_form=Data())


@app.route("/delete_book/<book_id>", methods=['POST'])
def delete_book(book_id):
    try:
        book_oid = ObjectId(book_id)
    except:
        return "Invalid Book ID", 404
        
    book = books_collection.find_one({'_id': book_oid})
    if not book or str(book.get('user_id')) != session.get('user_id'):
        flash("Book not found or you don't have permission to delete it.", "danger")
    else:
        books_collection.delete_one({'_id': book_oid})
        flash(f"Book '{book['title']}' deleted successfully!", "success")

    return redirect(url_for('home'))


@app.route('/book/<book_id>')
def view_book(book_id):
    try:
        book_oid = ObjectId(book_id)
    except:
        return "Invalid Book ID", 404

    book = books_collection.find_one({'_id': book_oid})
    if not book or str(book.get('user_id')) != session.get('user_id'):
        flash("Book not found or you don't have permission to view it.", "danger")
        return redirect(url_for('home'))

    return render_template('book_details.html', title=book['title'], book=book, json_form=Data())


@app.route("/download")
def download_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session["user_id"]
    books = list(books_collection.find({'user_id': ObjectId(user_id)}))

    if not books:
        flash("You have no books to download", "info")
        return redirect(url_for('home'))

    for book in books:
        book['_id'] = str(book['_id'])
        book['user_id'] = str(book['user_id'])
        if book.get('reading_started'):
            book['reading_started'] = book['reading_started'].isoformat()
        if book.get('reading_finished'):
            book['reading_finished'] = book['reading_finished'].isoformat()

    response = make_response(json.dumps(books, indent=4))
    response.headers["Content-Disposition"] = "attachment; filename=books_backup.json"
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/upload", methods=["POST"])
def upload_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = Data()
    if form.validate_on_submit():
        file = form.json_file.data
        try:
            data = json.load(file.stream)
        except (json.JSONDecodeError, UnicodeDecodeError):
            flash("Invalid JSON format. The file could not be read.", "danger")
            return redirect(url_for("home"))

        user_id = ObjectId(session["user_id"])
        books_to_add = []
        for entry in data:
            if not entry.get("title"):
                continue

            books_to_add.append({
                "title": entry.get("title"),
                "author": entry.get("author"),
                "isbn": entry.get("isbn"),
                "genre": entry.get("genre"),
                "rating": float(entry.get("rating", 0.0) or 0.0),
                "description": entry.get("description"),
                "cover_image": entry.get("cover_image"),
                "reading_started": datetime.fromisoformat(entry["reading_started"]) if entry.get("reading_started") else None,
                "reading_finished": datetime.fromisoformat(entry["reading_finished"]) if entry.get("reading_finished") else None,
                "user_id": user_id
            })
        
        if books_to_add:
            books_collection.insert_many(books_to_add)
            flash(f"{len(books_to_add)} book(s) uploaded successfully!", "success")
        else:
            flash("No valid book entries found in the file.", "warning")

        return redirect(url_for("home"))
    
    flash("File upload failed. Please try again with a valid JSON file.", "danger")
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template('about.html', title='About', json_form=Data())


@app.route("/developer")
def developer():
    return render_template('developer.html', title='Developer', json_form=Data())


if __name__ == "__main__":
    app.run(debug=True)
