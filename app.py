from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from datetime import datetime

from webforms import LoginForm, UserForm, PasswordForm, ProductForm, SearchForm


app = Flask(__name__)
app.config.from_envvar("APP_SETTINGS")


db = SQLAlchemy(app)
migrate = Migrate(app, db)


UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Clients.query.get(int(user_id))


@app.route('/')
def index():
    products = Products.query.order_by(Products.product_name)
    return render_template("index.html", products=products)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


# Register / Add a Product
@app.route('/register', methods=['GET', 'POST'])
def register():
    username = None
    form = UserForm()
    if form.validate_on_submit():
        client = Clients.query.filter_by(email=form.email.data).first()
        if client is None:
            hashed_pw = generate_password_hash(form.password_hash.data)
            client = Clients(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(client)
            db.session.commit()
        username = form.username.data
        form.username.data = ''
        form.email.data = ''
        form.password_hash = ''
    ordered_clients = Clients.query.order_by(Clients.date_added)

    return render_template('register.html', form=form, username=username, ordered_clients=ordered_clients)


@app.route('/importing', methods=['GET', 'POST'])
def importing():
    username = current_user.username
    if username == 'Ionut':
        product_name = None
        form = ProductForm()
        if form.validate_on_submit():
            product = Products.query.filter_by(product_name=form.product_name.data).first()
            if product is None:
                product = Products(product_name=form.product_name.data, price=form.price.data,
                                   description=form.description.data, product_image=form.product_image.data)
                db.session.add(product)
                db.session.commit()
            product_name = form.product_name.data
            form.price.data = ''
            form.description.data = ''
            form.product_image.data = ''
            flash("You added the product succesfully! Great Job!")
        ordered_products = Products.query.order_by(Products.product_name)

        return render_template('importing.html', form=form, product_name=product_name, ordered_products=ordered_products)


# Dashboard / Search / Products
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Clients.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.profile_pic = request.files['profile_pic']

        if request.files['profile_pic']:

            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            unique_pic = str(uuid.uuid1()) + "_" + pic_filename
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_pic))
            name_to_update.profile_pic = unique_pic
            try:
                db.session.commit()
                flash("User Updated Successfully")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
            except:
                flash("Error! Looks like there was a problem, try again later.")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
        else:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                       form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)
    return render_template("dashboard.html")


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    products = Products.query
    if form.validate_on_submit():
        product.search = form.searched.data

        products = products.filter(Products.product_name.like('%' + product.search + '%'))
        products = products.order_by(Products.product_name).all()

        return render_template('search.html', form=form, searched=product.search, products=products)
    else:
        return redirect(url_for('products'))


@app.route('/products')
def products():
    products = Products.query.order_by(Products.product_name)
    return render_template('products.html', products=products)


@app.route('/products/<int:id>')
def product(id):
    product = Products.query.get_or_404(id)
    return render_template('product.html', product=product)


# Update the user / Edit product / Buy product
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Clients.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.profile_pic = request.files['profile_pic']

        if request.files['profile_pic']:

            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            unique_pic = str(uuid.uuid1()) + "_" + pic_filename
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_pic))
            name_to_update.profile_pic = unique_pic
            try:
                db.session.commit()
                flash("User Updated Successfully")
                return render_template("update.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
            except:
                flash("Error! Looks like there was a problem, try again later.")
                return render_template("update.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
        else:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                   form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                    id = id)


#IMAGE DOES'T WORK, SOLVE IT
@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Products.query.get_or_404(id)
    form = ProductForm()
    if form.validate_on_submit():
        product.product_name = form.product_name.data
        product.price = form.price.data
        product.description = form.description.data
        product.product_image = request.files['product_image']

        if request.files['product_image']:
            pic_filename = secure_filename(product.product_image.filename)
            unique_product_pic = str(uuid.uuid1()) + "_" + pic_filename
            product.product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_product_pic))
            product.profile_pic = unique_product_pic
            try:

                db.session.add(product)
                db.session.commit()

                flash("Product has been updated")
                return redirect(url_for('product', id=product.id))

            except:
                flash("Error! Looks like there was a problem, try again later.")
                return render_template('edit_product.html', form=form, product=product, id=id)

        else:
            db.session.commit()
            flash("Product has been updated")
            return render_template('product.html', form=form, product=product, id=id)

    form.product_name.data = product.product_name
    form.price.data = product.price
    form.description.data = product.description
    form.product_image.data = product.product_image
    return render_template('edit_product.html', form=form)


@app.route('/products/buy/<int:id>', methods=['GET', 'POST'])
def buy(id):
    product_to_buy = Products.query.get_or_404(id)
    flash(f"You bought {product_to_buy.product_name} for {product_to_buy.price} $")
    return redirect(url_for('products'))


# Delete user / Delete product
@app.route('/delete/<int:id>')
def delete(id):
    client_to_delete = Clients.query.get_or_404(id)
    username = None
    form = UserForm()
    try:
        db.session.delete(client_to_delete)
        db.session.commit()
        flash("User Deleted Succesfully!")

        ordered_clients = Clients.query.order_by(Clients.date_added)
        return render_template("admin.html", form=form,
                                            username=username,
                                            ordered_clients=ordered_clients)
    except:
        flash("Whoops, there was a problem deleting user, try again.")


@app.route('/products/delete/<int:id>')
def delete_product(id):
    product_to_delete = Products.query.get_or_404(id)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash("Product deleted successfully!")

        ordered_products = Products.query.order_by(Products.product_name)
        return render_template("products.html",
                           ordered_products=ordered_products)

    except:
        flash("Whoops, there was a problem deleting the product, try again later.")


#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        client = Clients.query.filter_by(username=form.username.data).first()
        if client:
            if check_password_hash(client.password_hash, form.password.data):
                login_user(client)
                flash("Login Successfully!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That user doesn't exist.")
    return render_template("login.html", form=form)


#Logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))


#Test PW
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''

        pw_to_check = Clients.query.filter_by(email=email).first()

        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


#Admin
@app.route('/admin')
@login_required
def admin():
    username = current_user.username
    if username == 'Ionut':
        ordered_clients = Clients.query.order_by(Clients.date_added)
        return render_template("admin.html", ordered_clients=ordered_clients)
    else:
        flash("Sorry, you must be the admin to acces this page.")
        return redirect(url_for('dashboard'))



# Database Tabels (Clients and Products)
class Clients(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(10000), nullable=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Name %r>' % self.name


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(500), nullable=False, unique=False)
    price = db.Column(db.Integer, primary_key=False)
    description = db.Column(db.String(1000), nullable=True, unique=False)
    product_image = db.Column(db.String(10000), nullable=True)



if __name__ == '__main__':
    app.run(debug=True)