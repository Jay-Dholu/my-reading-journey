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

from sqlalchemy.exc import IntegrityError

from forms import Book, Login, SignUp, Data, RequestReset, ResetPassword, ResendVerification, EditProfile
from models import Record, User, db


load_dotenv('.env')

SECRET_KEY = os.environ.get('SECRET_KEY')
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myreadingjourney.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


mail = Mail(app)
csrf = CSRFProtect(app)
db.init_app(app)

s = Serializer(app.config['SECRET_KEY'])

with app.app_context():
    db.create_all()


def send_verification_email(user):
    """Generates and sends a verification email to the user."""
    token = s.dumps(user.email, salt='email-confirm-salt')
    confirm_url = url_for('verify_email', token=token, _external=True)
    
    msg = Message(
        "Confirm Your Email Address - My Reading Journey",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.html = render_template('verify_email.html', confirm_url=confirm_url, user=user)
    mail.send(msg)


@app.before_request
def check_user_session():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            flash("Your session was invalid and has been cleared. Please log in again.", "warning")


@app.context_processor
def inject_user():
    current_user = None
    if 'user_id' in session:
        current_user = db.session.get(User, session['user_id'])
    return dict(current_user=current_user)


@app.route("/")
@app.route("/home")
def home():
    json_form = Data()
    user_id = session.get('user_id')
    books = []

    if not user_id:
        flash("Please log in to add a book.", "warning")
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])

    if user:
        books = Record.query.filter_by(user_id=user.id).order_by(Record.reading_started.asc()).all()
        print(f"User ID: {user.id}, Books found: {len(books)}")

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
            send_verification_email(new_user)
        except IntegrityError:
            db.session.rollback()
            flash('User ID already exists. Please choose a different one.', 'danger')

        flash("Account created successfully! Please check your email to verify your account.", "success")
        return redirect(url_for('login'))
    
    return render_template("sign_up.html", title='Sign Up | My Reading Journey', form=form, json_form=json_form)


@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=1800)         # Verify the token that expires in 30 minutes
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first_or_404()

    if user.is_verified:
        flash('Account already verified. Please log in.', 'info')
    else:
        user.is_verified = True
        db.session.commit()
        flash('Your account has been verified! You can now log in.', 'success')
        
    return redirect(url_for('login'))


@app.route("/resend_verification", methods=['GET', 'POST'])
def resend_verification():
    # If user is already logged in, redirect them home
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = ResendVerification()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if a user with that email exists
        if user:
            # Check if they are already verified
            if user.is_verified:
                flash('This account has already been verified. Please log in.', 'info')
                return redirect(url_for('login'))
            else:
                # Resend the verification email
                send_verification_email(user)
                flash('A new verification email has been sent. Please check your inbox.', 'success')
                return redirect(url_for('login'))
        else:
            # For security, don't reveal that the user does not exist.
            # Just show a generic success message.
            flash('If an account with that email exists, a new verification email has been sent.', 'success')
            return redirect(url_for('login'))
            
    return render_template('resend_verification.html', title='Resend Verification', form=form, json_form=Data())


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    json_form = Data()

    if form.validate_on_submit():
        user = None

        if form.email.data:
            user = User.query.filter_by(email=form.email.data).first()
        elif form.userid.data:
            user = User.query.filter_by(userid=form.userid.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                if not user.is_verified:
                    message = Markup(f"Your account is not verified. <a href='{url_for('resend_verification')}' class='auth-link'>Resend verification email?</a>")
                    flash(message, 'warning')
                    return redirect(url_for('login'))
                
                session['user_id'] = user.id
                session.permanent = True
                flash(f"Welcome {user.name}", "success")
                return redirect(url_for('home'))
            else:
                flash("Incorrect password. Please try again.", "danger")
        else:
            flash("User does not exist. Please check your details.", "danger")

    return render_template("login.html", title='Login | My Reading Journey', form=form, json_form=json_form)
    

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('home'))
    

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if not session.get('user_id'):
        flash("You must be logged in to edit your profile.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash("User not found. Please log in again.", "danger")
        session.clear()
        return redirect(url_for('login'))

    form = EditProfile()
    form.meta.current_user_id = user.id

    if form.validate_on_submit():
        user.name = form.name.data
        user.userid = form.userid.data
        user.email = form.email.data
        
        if form.password.data:
            user.password = generate_password_hash(form.password.data)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        
        return redirect(url_for('home'))
    
    # Pre-populate the form on the initial GET request
    elif request.method == 'GET':
        form.name.data = user.name
        form.userid.data = user.userid
        form.email.data = user.email

    json_form = Data()

    return render_template('settings.html', title='Settings | My Reading Journey', form=form, json_form=json_form)


@app.route("/delete_account", methods=['POST'])
def delete_account():
    user_id = session.get('user_id')

    if not user_id:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if user:
        db.session.query(Record).filter_by(user_id=user.id).delete()   # First, delete all books associated with the user

        db.session.delete(user)     # Then, delete the user
        db.session.commit()

        session.clear() # Log the user out
        flash("Your account and all associated data have been permanently deleted.", "success")
    
    return redirect(url_for('home'))


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if session.get('user_id'):
        return redirect(url_for('home'))
        
    form = RequestReset()
    json_form = Data()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = s.dumps(user.email, salt='password-reset-salt')    # Generate token (expires in 30 minutes) 
            reset_url = url_for('reset_password', token=token, _external=True)

            # Send the email
            msg = Message(
                "Password Reset Request",
                sender=EMAIL, # Can be a generic sender
                recipients=[user.email]
            )
            msg.body = f"""To reset your password, visit the following link:\n{reset_url}\n\nIf you did not make this request then simply ignore this email and no changes will be made."""
            mail.send(msg)
        flash(f"A password reset link has been sent to email {user.email}.", "info")

        return redirect(url_for('login'))

    return render_template('forgot_password.html', title='Forgot Password | My Reading Journey', form=form, json_form=json_form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if session.get('user_id'):
        return redirect(url_for('home'))
     
    try:
        # Verify the token and get the email
        email = s.loads(token, salt='password-reset-salt', max_age=1800) # 30 minutes
    except:
        flash('The password reset link is invalid or has expired.', 'warning')
        return redirect(url_for('forgot_password'))
        
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    form = ResetPassword()
    json_form = Data()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'info')
        flash("You are now able to log in.", 'success')

        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password | My Reading Journey', form=form, json_form=json_form)


@app.route("/about")
def about():
    json_form = Data()
    return render_template('about.html', title='About | My Reading Journey', json_form=json_form)


@app.route("/developer")
def developer():
    json_form = Data()
    return render_template('developer.html', title='Developer | My Reading Journey', json_form=json_form)


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
            isbn=form.isbn.data,
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
        book.isbn = form.isbn.data
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
            "isbn": book.isbn if book.isbn else None,
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
            data = json.load(file.stream)    # using text mode to read file
        except (json.JSONDecodeError, UnicodeDecodeError):
            flash("Invalid JSON format. The file could not be read.", "danger")
            return redirect(url_for("home"))

        user_id = session["user_id"]
        book_count = 0
        for entry in data:
            title = entry.get("title")
            if not title:
                continue

            isbn_raw = entry.get("isbn")
            isbn = isbn_raw.strip() if isinstance(isbn_raw, str) else None

            new_book = Record(
                title=title,
                author=entry.get("author"),
                isbn=isbn,
                genre=entry.get("genre"),
                rating=float(entry.get("rating", 0.0) or 0.0),
                description=entry.get("description"),
                cover_image=entry.get("cover_image"),
                reading_started=datetime.fromisoformat(entry["reading_started"]) if entry.get(
                    "reading_started") else None,
                reading_finished=datetime.fromisoformat(entry["reading_finished"]) if entry.get(
                    "reading_finished") else None,
                user_id=user_id
            )
            db.session.add(new_book)
            book_count += 1

        try:
            db.session.commit()
            flash(f"{book_count} book(s) uploaded successfully!", "success")
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Database error: {e}. Please check your data for issues (e.g., duplicate unique fields).", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {e}", "danger")

        return redirect(url_for("home"))
    
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
