from datetime import timedelta
from secrets import token_urlsafe

from flask import Flask, render_template, request, redirect, url_for, session
from jinja2 import *
import db
import validate

app = Flask(__name__)

app.config['SECRET_KEY'] = token_urlsafe(64)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


def login_required(func):
    def wrapper():
        if 'user_is_logged_in' in session:
            return func()
        else:
            return redirect(url_for('login_page'))
    wrapper.__name__ = func.__name__
    return wrapper

# from telegram import Bot
# from telegram.ext import Updater, CommandHandler
# import requests

# tg_bot = Bot(token='2137464088:AAHVdrnk00CYWJQQEPSJsieOLI9_19CE3RA')
# tg_updater = Updater(token='2137464088:AAHVdrnk00CYWJQQEPSJsieOLI9_19CE3RA', use_context=True)
# tg_dispatcher = tg_updater.dispatcher

# TODO: Figure out how to fix the telegram bot bug
# The telegram bot bug is: because of the telegram bot, for some reason, you have to stop the program twice for it to
# actually stop.

# def tg_start(update, context):
#     context.bot.send_message(update.effective_chat.id, "Привет!")
#
#
# def callback_request(update, context):
#     data = requests.get('http://localhost:5000/api/orders').json()
#     print(data)
#     context.bot.send_message(chat_id=update.effective_chat.id, text='orderssss')
#     if data:
#         context.bot.send_message(chat_id=update.effective_chat.id, text=str(data[-1]))
#
#
# def callback_alarm(context):
#     context.bot.send_message(chat_id=context.job.context, text='BEEP!')
#
#
# def callback_timer(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text='Начинаем!')
#     tg_updater.job_queue.run_repeating(callback_alarm, 1, context=update.message.chat_id)
#
#
# tg_start_handler = CommandHandler('start', tg_start, run_async=True)
# tg_dispatcher.add_handler(tg_start_handler)
# tg_callback_timer_handler = CommandHandler('timer', callback_timer, run_async=True)
# tg_dispatcher.add_handler(tg_callback_timer_handler)
# tg_callback_request_handler = CommandHandler('request', callback_request, run_async=True)
# tg_dispatcher.add_handler(tg_callback_request_handler)
#
# tg_updater.start_polling()


@app.errorhandler(404)
def not_found(e):
    return "404"


@app.route('/products')
def products_page():
    ptype = request.args.get('type')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')
    sort = request.args.get('sort')
    page = request.args.get('page')
    from_top = request.args.get('from_top')
    if price_min is None:
        price_min = 0
    if price_max is None:
        price_max = 65534
    if sort is None:
        sort = 0
    if page is None:
        page = 0
    if from_top is None:
        from_top = True

    if validate.validate_products(ptype=ptype, price_min=price_min, price_max=price_max, sort=sort, page=page,
                                  from_top=from_top):
        price_min = int(price_min)
        price_max = int(price_min)
        sort = int(sort)
        page = int(page)
        from_top = bool(int(from_top))
        product = db.get_products_page_by_parameters(ptype=ptype, price_min=price_min, price_max=price_max, sort=sort,
                                                     page=page, from_top=from_top)
        if len(product) != 0:
            # GETed valid details, some products found
            return render_template('products.html', product=product)
        # GETed valid details, no products found
        return redirect(url_for('not_found'))
    # GETed invalid details
    return redirect(url_for('products_page'))


@app.route('/product/<int:product_id>')
def product_page(product_id):
    product, maker = db.get_product_page_info_by_product_id(product_id)
    return render_template('product.html', product=product, maker=maker)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/order_list')
@login_required
def order_list_page():
    orders = db.get_orders(session['user_id'])
    return render_template('order_list.html', orders=orders)


@app.route('/cart')
@login_required
def cart_page():
    cart = db.get_full_cart(session['user_cart'])
    return render_template('cart.html', cart=cart)


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order_page():
    if request.method == 'POST':
        validation_error = validate.validate_order(request.form)
        if validation_error is None:
            # POSTed valid order details

            # Unused right now:
            phone_number = request.form['phone_number']

            user_id = session['user_id']
            products = session['user_cart']
            delivery_date = request.form['delivery_date'].replace('T', ' ')
            # TODO: Get these fields from request.form
            delivery_type = 1
            delivery_address = 'Pushkina 25'
            payment_type = 1
            db.put_orders(user_id=user_id, delivery_date=delivery_date, delivery_type=delivery_type,
                          delivery_address=delivery_address, payment_type=payment_type, products=products)
            session['user_cart'] = []

            return redirect(url_for('order_list_page'))
        # POSTed invalid order details
        return render_template('order.html', error=validation_error)
    # Didn't POST
    cart = db.get_full_cart(session['user_cart'])
    # TODO: Get the other necessary details for order.html

    return render_template('order.html', cart=cart)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        pswd = request.form['password']
        pswd_repeat = request.form['password_repeat']
        email = request.form['email']
        name = request.form['name']
        phone = request.form['phone']
        city = request.form['city']

        validation_error = validate.validate_register(pswd=pswd, pswd_repeat=pswd_repeat, email=email, name=name,
                                                      phone=phone, city=city)
        if validation_error is None:
            # POSTed valid registration details

            session['reg_code'] = validate.generate_registration_code()
            # TODO: Send the code to the user by email
            session['reg_hashed_pswd'] = validate.hash_pswd(pswd)
            session['reg_email'] = email
            session['reg_name'] = name
            session['reg_phone'] = phone
            session['reg_city'] = city
            session['reg'] = None

            return redirect(url_for('register_page_code'))
        # POSTed invalid registration details
        return render_template('login.html', error=validation_error)
    # Didn't POST
    return render_template('register.html')


@app.route('/register/code', methods=['GET', 'POST'])
def register_page_code():
    if 'reg' in session:
        if request.method == 'POST':
            code = session['reg_code']
            if validate.validate_registration_code(request.form['code'], code):
                # Did register, POSTed correct code

                hashed_pswd = session['reg_hashed_pswd']
                email = session['reg_email']
                name = session['reg_name']
                phone = session['reg_phone']
                city = session['reg_city']
                db.put_user(hashed_pswd=hashed_pswd, email=email, name=name, phone=phone, city=city)

                del session['reg_hashed_pswd']
                del session['reg_email']
                del session['reg_name']
                del session['reg_phone']
                del session['reg_city']
                del session['reg_code']
                del session['reg']

                return redirect(url_for('index_page'))
            # Did register, POSTed wrong code
            return render_template('register_code.html', error=True)
        # Did register, didn't POST
        return render_template('register_code.html')   # TODO: Create register_code.html
    # Didn't register
    return redirect(url_for('register_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        validation_result = validate.validate_login(user_email, user_password)
        if type(validation_result) is int:
            # POSTed correct login details
            session['user_id'] = validation_result
            session['user_cart'] = db.get_cart_by_user_id(session['user_id'])
            session['user_is_logged_in'] = None

            session.permanent = True

            return redirect(url_for('index_page'))
        # POSTed wrong login details
        return render_template('login.html', error='Неправильный логин или пароль')
    # Didn't POST
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout_page():
    # TODO: Save user data here

    del session['user_is_logged_in']

    return redirect(url_for('index_page'))


app.run(host='0.0.0.0')
