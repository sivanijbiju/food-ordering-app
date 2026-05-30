from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

app.secret_key = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)


# ---------------- USER MODEL ---------------- #

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    email = db.Column(db.String(100))

    password = db.Column(db.String(200))

    role = db.Column(db.String(20))


# ---------------- FOOD MODEL ---------------- #

class Food(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(db.String(100))

    price = db.Column(db.String(50))

    image = db.Column(db.String(200))


# ---------------- ORDER MODEL ---------------- #

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(db.String(100))

    price = db.Column(db.String(50))


# ---------------- CART MODEL ---------------- #

class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(db.String(100))

    price = db.Column(db.String(50))

    image = db.Column(db.String(200))


# ---------------- HOME ---------------- #

@app.route('/')
def home():
    return redirect('/dashboard')



# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        email = request.form['email']

        password = request.form['password']

        role = request.form.get('role', 'user')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)

        db.session.commit()

        flash('Registration Successful')

        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session['user'] = user.email

            session['role'] = user.role

            flash('Login Successful')

            return redirect('/dashboard')

        else:

            flash('Invalid Email or Password')

    return render_template('login.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:

        return redirect('/login')

    return render_template('dashboard.html')


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    flash('Logged Out Successfully')

    return redirect('/login')


# ---------------- ADD FOOD ---------------- #

@app.route('/addfood', methods=['GET', 'POST'])
def addfood():

    if 'user' not in session:

        return redirect('/login')

    if request.method == 'POST':

        food_name = request.form['food_name']

        price = request.form['price']

        image = request.files['image']

        image.save(os.path.join(
            app.config['UPLOAD_FOLDER'],
            image.filename
        ))

        new_food = Food(
            food_name=food_name,
            price=price,
            image=image.filename
        )

        db.session.add(new_food)

        db.session.commit()

        flash('Food Added Successfully')

        return redirect('/viewfood')

    return render_template('addfood.html')


# ---------------- VIEW FOOD ---------------- #

@app.route('/viewfood')
def viewfood():

    search = request.args.get('search')

    if search:

        foods = Food.query.filter(
            Food.food_name.contains(search)
        ).all()

    else:

        foods = Food.query.all()

    return render_template(
        'viewfood.html',
        foods=foods
    )


# ---------------- UPDATE FOOD ---------------- #

@app.route('/updatefood/<int:id>', methods=['GET', 'POST'])
def updatefood(id):

    food = Food.query.get(id)

    if request.method == 'POST':

        food.food_name = request.form['food_name']

        food.price = request.form['price']

        db.session.commit()

        flash('Food Updated Successfully')

        return redirect('/viewfood')

    return render_template(
        'updatefood.html',
        food=food
    )


# ---------------- DELETE FOOD ---------------- #

@app.route('/deletefood/<int:id>')
def deletefood(id):

    food = Food.query.get(id)

    db.session.delete(food)

    db.session.commit()

    flash('Food Deleted Successfully')

    return redirect('/viewfood')


# ---------------- ORDER ---------------- #

@app.route('/order/<int:id>')
def order(id):

    food = Food.query.get(id)

    new_order = Order(
        food_name=food.food_name,
        price=food.price
    )

    db.session.add(new_order)

    db.session.commit()

    flash('Order Placed Successfully')

    return redirect('/viewfood')


# ---------------- ADD TO CART ---------------- #

@app.route('/addtocart/<int:id>')
def addtocart(id):

    food = Food.query.get(id)

    cart_item = Cart(
        food_name=food.food_name,
        price=food.price,
        image=food.image
    )

    db.session.add(cart_item)

    db.session.commit()

    flash('Item Added To Cart')

    return redirect('/viewfood')


# ---------------- CART ---------------- #

@app.route('/cart')
def cart():

    cart_items = Cart.query.all()

    return render_template(
        'cart.html',
        cart_items=cart_items
    )


# ---------------- DELETE CART ---------------- #

@app.route('/deletecart/<int:id>')
def deletecart(id):

    item = Cart.query.get(id)

    db.session.delete(item)

    db.session.commit()

    flash('Item Removed From Cart')

    return redirect('/cart')


# ---------------- CHECKOUT ---------------- #

@app.route('/checkout')
def checkout():

    cart_items = Cart.query.all()

    total = 0

    for item in cart_items:

        price = item.price.replace('₹', '')

        total += int(price)

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        total=total
    )
@app.route('/payment')
def payment():

    cart_items = Cart.query.all()

    total = 0

    for item in cart_items:

        price = item.price.replace('₹', '')

        total += int(price)

    return render_template(
        'payment.html',
        total=total
    )

# ---------------- PLACE ORDER ---------------- #

@app.route('/placeorder')
def placeorder():

    cart_items = Cart.query.all()

    for item in cart_items:

        new_order = Order(
            food_name=item.food_name,
            price=item.price
        )

        db.session.add(new_order)

    Cart.query.delete()

    db.session.commit()

    flash('Order Placed Successfully')

    return redirect('/orderhistory')

@app.route('/orderhistory')
def orderhistory():

    orders = Order.query.all()

    return render_template(
        'orderhistory.html',
        orders=orders
    )

@app.route('/profile')
def profile():

    if 'user' not in session:

        return redirect('/login')

    user = User.query.filter_by(
        email=session['user']
    ).first()

    return render_template(
        'profile.html',
        user=user
    )
@app.route('/adminorders')
def adminorders():

    if session.get('role') != 'admin':

        flash('Access Denied')

        return redirect('/dashboard')

    orders = Order.query.all()

    return render_template(
        'adminorders.html',
        orders=orders
    )
@app.route('/deleteorder/<int:id>')
def deleteorder(id):

    if session.get('role') != 'admin':

        flash('Access Denied')

        return redirect('/dashboard')

    order = Order.query.get(id)

    db.session.delete(order)

    db.session.commit()

    flash('Order Deleted Successfully')

    return redirect('/adminorders')

@app.route('/health')
def health():
    return "Application Running"
# ---------------- CREATE DATABASE ---------------- #

with app.app_context():

    db.create_all()


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=9000, ssl_context='adhoc')
