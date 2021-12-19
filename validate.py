import re
import bcrypt
import db


def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


def password_is_strong(password):
    from password_strength import PasswordStats
    strength = PasswordStats(password).strength()
    return strength > 0.6


def order(form):
    # TODO: Validate order form here
    # for key in request.form:
    #     if request.form[key] == '':
    #         return render_template('order.html',
    #                                error='Не все поля заполнены!'
    #                                )
    return None


def register(form):
    email = form['email']
    password = form['password']
    password_repeat = form['password_repeat']
    name = form['name']
    phone = form['phone']

    if 6 > len(password):
        return 'Password is too short! (less than 6 symbols)'
    if 100 < len(password):
        return 'Password is too long! (more than 100 symbols)'
    if not password_is_strong(password):
        return 'Password not strong enough!'
    if password != password_repeat:
        return "Passwords must match!"
    # TODO: Check email correctness with RE

    if db.is_email_in_db(email):
        return 'This email is already in use!'

    return None


def login(email, password):
    db_password = db.get_password_by_email(email)

    if db_password is None:
        return

    db_password = str(db_password)
    db_password = db_password[4:len(db_password)-1]
    db_password = db_password.rstrip('\\x00')
    db_password = db_password[0:len(db_password)-1]
    db_password = db_password.encode('utf-8')

    if not check_password(password, db_password):
        return

    user_id = db.get_user_id_by_email(email)

    return user_id


def products(ptype, price_min, price_max, sort, page, from_top):
    if not (price_min is None or price_min.isnumeric()) \
            or not (price_max is None or price_max.isnumeric()) \
            or not (page is None or page.isnumeric()) \
            or not (sort is None or sort.isnumeric()) \
            or not (from_top is None or from_top == '0' or from_top == '1'):
        return False

    return len(ptype) != 0 and ptype.replace(' ', '').isalpha()
