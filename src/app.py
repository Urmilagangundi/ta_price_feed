from flask import session, Flask, request, jsonify, flash, render_template, redirect, url_for
from sqlalchemy.sql.expression import and_
import pandas as pd
from datetime import datetime
from models import db, PricingFeeds
from flask_migrate import Migrate
import json

app = Flask(__name__, template_folder='templates/upload')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET' and request.args.get('search_context'):
        feed_data = json.loads(request.args.get('search_context'))
        results = get_query(PricingFeeds, feed_data)
        return render_template('search_results.html', results=results, count=len(results), search_context=json.dumps(feed_data))
    if request.method == 'GET':
        return redirect(url_for('home'))
    if request.method == 'POST':
        store_id = request.form.get('store_id')
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        product_date = request.form.get('date')
        sku = request.form.get('sku')
        feed_data = {}
        if store_id:
            store_id, error = validate_store_id(store_id)
            if error:
                flash(error)
                return redirect(request.url)
            feed_data['store_id'] = store_id
        if product_name:
            error = validate_product_name(product_name)
            if error:
                flash(error)
                return redirect(request.url)
            feed_data['product_name'] = product_name
        if price:
            price, error = validate_price(price)
            if error:
                flash(error)
                return redirect(request.url)
            feed_data['price'] = price
        if product_date:
            product_date, error = validate_date(product_date)
            if error:
                flash(error)
                return redirect(request.url)
            feed_data['product_date'] = product_date
        if sku:
            feed_data['sku'] = sku
        results = get_query(PricingFeeds, feed_data)
        return render_template('search_results.html', results=results, count=len(results), search_context=json.dumps(feed_data))


@app.route('/edit/<pid>', methods=['GET', 'POST'])
def edit(pid):
    search_context = None
    if request.args.get('search_context'):
        search_context = request.args.get('search_context')
    if request.method == 'GET':
        price_feed = PricingFeeds.query.filter(PricingFeeds.id == pid).first()
        return render_template('edit.html', result=price_feed, search_context=search_context)
    if request.method == 'POST':
        # post operation here
        store_id = request.form.get('store_id')
        if store_id:
            store_id, error = validate_store_id(store_id)
            if error:
                flash(error)
                return redirect(request.url)

        product_name = request.form.get('product_name')
        if product_name:
            error = validate_product_name(product_name)
            if error:
                flash(error)
                return redirect(request.url)

        price = request.form.get('price')
        if price:
            price, error = validate_price(price)
            if error:
                flash(error)
                return redirect(request.url)

        product_date = request.form.get('date')
        if product_date:
            product_date, error = validate_date(product_date)
            if error:
                flash(error)
                return redirect(request.url)

        price_feed = PricingFeeds.query.filter(PricingFeeds.id == pid).update(request.form)

        db.session.commit()
        flash("Data updated successfully")
        if search_context:
            return redirect(url_for('search')+'?search_context='+search_context)
        else:
            return redirect(url_for('search'))


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        file = request.files.get('price_feeds')
        if not file:
            flash('No file available')
            return redirect(request.url)
        if 'csv' not in file.filename:
            flash('Not a valid file')
            return redirect(request.url)
        price_feed_df = pd.read_csv(file, header=0,
                                    names=['Store ID', 'SKU', 'Product Name', 'Price', 'Date'])
        price_feed_df.dropna(inplace=True)
        if not len(price_feed_df):
            flash('Please upload valid price feed data')
            return redirect(request.url)
        if len(price_feed_df) > 1000:
            flash('Please upload file with rows not more than 100.')
            return redirect(request.url)
        price_feed_df['SKU'] = price_feed_df['SKU'].astype('str')
        for each_row in price_feed_df.to_dict('records'):
            valid_status, error_message = validate_price_feed(each_row)
            if not valid_status:
                flash(error_message)
                return redirect(request.url)
            price_feeds = PricingFeeds.query.filter((PricingFeeds.store_id == each_row['Store ID']) &
                                                    (PricingFeeds.price == each_row['Price']) &
                                                    (PricingFeeds.product_date == each_row['Date']) &
                                                    (PricingFeeds.product_name == each_row['Product Name']) &
                                                    (PricingFeeds.sku == each_row['SKU'])).first()
            if price_feeds:
                continue
            new_feed = PricingFeeds(store_id=each_row['Store ID'], price=each_row['Price'],
                                    product_date=each_row['Date'], product_name=each_row['Product Name'],
                                    sku=each_row['SKU'])
            db.session.add(new_feed)
            db.session.commit()
        flash("Price Feed has been successfully uploaded")
        return redirect(request.url)
    else:
        return redirect(url_for('home'))


def get_query(table, feed_data):
    conditions = [getattr(table, field_name) == feed_data[field_name]
                  for field_name in feed_data]
    return table.query.filter(and_(*conditions)).all()


def validate_store_id(store_id):
    try:
        store_id = int(store_id)
    except ValueError:
        return False, 'Store IDs should be integers.'
    return store_id, False


def validate_product_name(product_name):
    if not product_name.isalpha():
        return 'Invalid Product Name'
    return False


def validate_date(product_date):
    try:
        product_date = datetime.strptime(product_date, '%Y-%m-%d').date()
        return product_date, False
    except:
        return False, 'Invalid Date'


def validate_price(price):
    try:
        valid_price = int(price)
        try:
            if valid_price != float(price):
                valid_price = float(price)
        except ValueError:
            return valid_price, False
    except ValueError:
        try:
            valid_price = float(price)
        except ValueError:
            return False, 'Invalid Price'
    return valid_price, False


def validate_price_feed(price_feed_data):
    valid_status = False

    price_feed_data['Store ID'], error = validate_store_id(price_feed_data['Store ID'])
    if error:
        return valid_status, error

    error = validate_product_name(price_feed_data['Product Name'])
    if error:
        return valid_status, error

    price_feed_data['Date'], error = validate_date(price_feed_data['Date'])
    if error:
        return valid_status, error
    price_feed_data['Price'], error = validate_price(price_feed_data['Price'])

    return True, ''


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://local_user:123456@localhost/tiger_analytics'
db.init_app(app)
with app.app_context():
    db.create_all()
Migrate(app, db)
if __name__ == '__main__':
    app.run(debug=True)
