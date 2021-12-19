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
        if 'user_is_logged_in' in session and session['user_is_logged_in']:
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


@app.route('/404')
def not_found():
    return 404


@app.route('/test')
def test():
    return 'H'


@app.route('/products')
def products_page():
    # TODO: Fill in products.html

    # TODO: Get all the parameters from GET and parse them
    ptype = request.args.get('type')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')
    sort = request.args.get('sort')
    page = request.args.get('page')
    from_top = request.args.get('from_top')

    if validate.products(ptype=ptype, price_min=price_min, price_max=price_max, sort=sort, page=page, from_top=from_top):
        price_min = 0 if price_min is None else int(price_min)
        price_max = 65534 if price_max is None else int(price_min)
        sort = 0 if sort is None else int(sort)
        page = 0 if page is None else int(page)
        from_top = bool(from_top)
        product = db.get_products_page_by_parameters(ptype=ptype, price_min=price_min, price_max=price_max, sort=sort, page=page, from_top=from_top)
        if len(product) != 0:
            return render_template('products.html', product=product)
        else:
            return redirect(url_for('not_found'))
    else:
        return redirect(url_for('products_page'))


@app.route('/product/<int:product_id>')
def product_page(product_id):
    # TODO: Complete product.html
    # TODO: Get product info from database from product id, and render the product page with that info
    product, maker = db.get_product_page_info_by_product_id(product_id)
    return render_template('product.html', product=product, maker=maker)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/order_list')
@login_required
def order_list_page():
    # TODO: Complete order_list.html
    # TODO: Get the orders from the database based on session['user'].id, gather other data from the database based on
    #  that, and render the order_list page with all that info
    return render_template('order_list.html')


@app.route('/cart')
@login_required
def cart_page():
    # TODO: Get the product ids from session['user'].cart, get each product's info in a looping over the list from the
    #  database, and render the cart page with all that info
    return render_template('cart.html')


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order_page():
    if request.method == 'POST':
        validation_error = validate.order(request.form)
        if validation_error is None:
            # TODO: Get all necessary fields from the user object
            user_id = session['user_id']
            products = session['user_cart']
            # TODO: Get all necessary fields from request.form
            phone_number = request.form['phone_number']
            delivery_date = request.form['delivery_date'].replace('T', ' ')
            delivery_type = 1
            delivery_address = 'Pushkina 25'
            payment_type = 1
            db.put_orders(user_id=user_id, delivery_date=delivery_date, delivery_type=delivery_type,
                          delivery_address=delivery_address, payment_type=payment_type, products=products)
            session['user_cart'] = []

            return redirect(url_for('order_list_page'))
        else:
            return render_template('order.html', error=validation_error)

    cart = session['user_cart']


    return render_template('order.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        validation_error = validate.register(request.form)
        if validation_error is None:
            # TODO: Send email confirmations using Python.
            # 1. Generate a random n-length code
            # 2. Save the login, password and the code to the user session
            # 3. Redirect user to the page of entering the code
            #    TODO: Create the page of entering the code (entry field and submit button, methods POST and GET)
            # 4. On the user entering a code and POSTing it, check if it's the same as the one in the session['
            # 5a. If it isn't, update the page, placing the error in it
            # 5b. If it is,
            #     1. Create a new entry in the database
            #     2a. If something goes wrong, redirect the user to a page with the error "Something went wrong..." 
            #     And reset session
            #     2b. If everything goes right, redirect the user to a page with the success
            request.form['hashed_password'] = validate.hash_password(request.form['password'])
            db.put_user(request.form['email'], request.form['name'], request.form['hashed_password'])
        else:
            return render_template('login.html', error=validation_error)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        validation_result = validate.login(user_email, user_password)
        if type(validation_result) is int:
            session['user_id'] = validation_result
            session['user_cart'] = db.get_cart_by_id(validation_result)

            session['user_is_logged_in'] = True

            return redirect(url_for('index_page'))
        else:
            return render_template('login.html', error='Неправильный логин или пароль')
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout_page():
    # TODO: Save user data here

    session['user_is_logged_in'] = False

    return redirect(url_for('index_page '))


app.run()
