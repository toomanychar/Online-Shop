import mariadb
from os.path import isfile


connection_parameters = {
    "user": "admin",
    "password": "not password",
    "host": "localhost",
    "database": "online_shop_test"
}


def get_connection():
    return mariadb.connect(**connection_parameters)


def get(command):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(command)

    command_result = cursor.fetchall()

    cursor.close()
    connection.close()
    return command_result


def put(command):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(command)

    connection.commit()

    cursor.close()
    connection.close()
    return None


def is_email_in_db(email):
    result = get(f'SELECT 1 FROM user WHERE email = "{email}"')
    return len(result) != 0


def get_password_by_email(email):
    result = get(f'SELECT password FROM user WHERE email = "{email}"')
    if len(result) != 0:
        return result[0][0]
    else:
        return None


def get_user_id_by_email(email):
    result = get(f'SELECT user_id FROM user WHERE email = "{email}"')
    if len(result) != 0:
        return result[0][0]
    else:
        return None


def put_user(form):
    email = form['email']
    name = form['name']
    hashed_password = form['hashed_password']

    return put(f'INSERT INTO user (email, name, password) VALUES ("{email}", "{name}", "{hashed_password}")')


def put_orders(user_id, delivery_date, delivery_type, delivery_address, payment_type, products):
    put(f'INSERT INTO orders (user_id, delivery_date, delivery_type, delivery_address, payment_type, order_status) VALUES ({user_id}, CONVERT("{delivery_date}", DATETIME), {delivery_type}, "{delivery_address}", {payment_type}, 0)')
    order_id = get(f'SELECT order_id FROM orders WHERE user_id = {user_id} AND delivery_date = CONVERT("{delivery_date}", DATETIME) AND delivery_type = {delivery_type} AND delivery_address = "{delivery_address}" AND payment_type = {payment_type} AND order_status = 0')
    order_id = order_id[0][0]
    for product in products:
        put(f'INSERT INTO orders_products (order_id, product_id, product_count) VALUES ({order_id}, {product[0]}, {product[1]})')
    return None


def get_cart_by_id(user_id):
    result = get(f'SELECT product_id, product_count FROM basket WHERE user_id = {user_id}')
    return result


def get_product_page_info_by_product_id(product_id):
    product, maker = {}, {}

    product_results = get(f'SELECT type, name, base_price, maker_id FROM product WHERE product_id = {product_id}')
    if len(product_results) != 0:
        product['type'] = product_results[0][0]

        product['name'] = product_results[0][1]

        product['price'] = product_results[0][2]

        product['imgs'] = []
        for i in range(30):   # Hardcoded limit of amount of images
            fn = f'static/images/product/{product_id}_{i}.jpg'
            if isfile(fn):
                product['imgs'].append(fn)
            else:
                break
        if len(product['imgs']) == 0:
            product['imgs'] = ['static/images/missing_product.png']

        maker['id'] = product_results[0][3]

        maker_results = get(f'SELECT name FROM user WHERE user_id = {maker["id"]}')
        if len(maker_results) != 0:
            maker['name'] = maker_results[0][0]
            fn = f'static/images/user/{maker["id"]}.jpg'
            if isfile(fn):
                maker['img'] = fn
            else:
                maker['img'] = 'static/images/missing_user.png'
        else:
            maker['name'] = 'Unknown maker'

            maker['img'] = 'static/images/missing_user.png'
    return product, maker


def get_products_page_by_parameters(ptype, price_min, price_max, sort, page):
    sorting_methods = []
    sorting_method = sorting_methods[sort]
    command = f'SELECT name, base_price, sale_percent FROM product WHERE type = "{ptype}" AND base_price - base_price * sale_percent / 100 <= {price_max} AND base_price - base_price * sale_percent / 100 >= {price_min}'

    return products