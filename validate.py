import db
import re


def hash_pswd(plain_text_password):
    from bcrypt import hashpw, gensalt
    return hashpw(plain_text_password.encode('utf-8'), gensalt())


def check_pswd(plain_text_pswd, hashed_pswd):
    from bcrypt import checkpw
    return checkpw(plain_text_pswd.encode('utf-8'), hashed_pswd)


def generate_registration_code():
    from secrets import choice
    from string import ascii_uppercase, digits
    return ''.join(choice(ascii_uppercase + digits) for _ in range(5))


def validate_registration_code(code, real_code):
    if code.len() != real_code.len():
        return False

    return code == real_code


def pswd_is_strong(pswd):
    from password_strength import PasswordStats
    strength = PasswordStats(pswd).strength()
    return strength > 0.6


def validate_order(form):
    # TODO: Validate order form here
    # for key in request.form:
    #     if request.form[key] == '':
    #         return render_template('order.html',
    #                                error='Не все поля заполнены!'
    #                                )
    return None


def validate_register(pswd, pswd_repeat, email, name, phone, city):
    if not name.replace(' ', '').isalpha():
        return 'Your name has illegal characters!'
    if 4 > len(name):
        return 'Your name is too short'
    if 20 < len(name):
        return 'Your name is too long'
    if 6 > len(pswd):
        return 'Password is too short! (less than 6 symbols)'
    if 100 < len(pswd):
        return 'Password is too long! (more than 100 symbols)'
    if pswd != pswd_repeat:
        return "Passwords must match"
    if not pswd_is_strong(pswd):
        return 'Password is not strong enough'
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'   # Not sure if this is correct code
    if not re.fullmatch(email_regex, email):
        return 'Invalid email'
    valid_cities = ['', 'Kyiv', 'Kiev']
    if city not in valid_cities:
        return 'Unsupported city'
    if len(phone) < 8 or len(phone) > 12 or not phone.isnumeric():
        return 'Invalid phone number'

    if db.is_email_in_db(email):
        return 'This email is already in use!'

    return None


def validate_login(email, pswd):
    db_pswd = db.get_pswd_by_email(email)

    if db_pswd is None:
        return

    db_pswd = str(db_pswd)
    db_pswd = db_pswd[4:len(db_pswd)-1]
    db_pswd = db_pswd.rstrip('\\x00')
    db_pswd = db_pswd[0:len(db_pswd)-1]
    db_pswd = db_pswd.encode('utf-8')

    if not check_pswd(pswd, db_pswd):
        return

    user_id = db.get_user_id_by_email(email)

    return user_id


def validate_products(ptype, price_min, price_max, sort, page, from_top):
    try:
        return int(price_max) >= int(price_min) > 0 \
               and int(page) > 0 > int(sort) \
               and (from_top == '0' or from_top == '1') \
               and ptype \
               and ptype.replace(' ', '').isalpha()
    except ValueError:
        return False
