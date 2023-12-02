from flask import Flask, render_template, request, flash, redirect, url_for, session
from config import *
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "154624"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User( username=form.username.data,
                     email=form.email.data,
                     password=form.password.data,
                    role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('You have logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/inventory')
@login_required
def inventory():
    products = Product.query.all()
    batches = Batch.query.all()
    return render_template('inventory.html', products=products, batches=batches)


@app.route('/orders')
@login_required
def orders():
    products = Product.query.all()
    orders = Order.query.all()
    form = OrderForm()
    form.product.choices = [(p.id, p.name) for p in products]
    return render_template('orders.html', products=products, orders=orders, form=form)


@app.route('/accounting')
@login_required
def accounting():
    if current_user.role == 'accountant':
        orders = Order.query.filter(Order.status != 'Pending').all()
        return render_template('accounting.html', orders=orders)
    else:
        flash('You are not authorized to access this page!', 'danger')
        return redirect(url_for('home'))


@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    form = OrderForm()
    if form.validate_on_submit():
        product = Product.query.get(form.product.data)
        order = Order(product_id=product.id, user_id=current_user.id, customer=form.customer.data, quantity=form.quantity.data)
        db.session.add(order)
        db.session.commit()
        flash('You have placed an order successfully!', 'success')
    return redirect(url_for('orders'))


@app.route('/orders/<int:order_id>/update', methods=['GET', 'POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    form = UpdateOrderForm()
    if form.validate_on_submit():
        status = form.status.data
        order.status = status
        db.session.commit()
        flash(f'Order {order.id} status has been updated to {order.status}!', 'success')
        return redirect(url_for('orders'))
    else:
        return render_template('update_order_status.html', order=order, form=form)


@app.route('/clear_order/<int:order_id>', methods=['POST'])
@login_required
def clear_order(order_id):
    if current_user.role == 'accountant':
        order = Order.query.get_or_404(order_id)
        order.status = 'Cleared'
        db.session.commit()
        flash(f'Order {order.id} has been cleared!', 'success')
    else:
        flash('You are not authorized to clear orders!', 'danger')
    return redirect(url_for('accounting'))


@app.route('/update_inventory', methods=['POST'])
@login_required
def update_inventory():
    form = UpdateInventoryForm()
    if form.validate_on_submit():
        rfid = form.rfid.data
        batch = Batch.query.filter_by(rfid=rfid).first()
        if batch:
            product = Product.query.get(batch.product_id)
            product.quantity += batch.quantity
            db.session.delete(batch)
            db.session.commit()
            flash(f'Inventory has been updated with {batch.quantity} units of {product.name}!', 'success')
        else:
            flash('Invalid RFID!', 'danger')
    return redirect(url_for('inventory'))


if __name__ == '__main__':
    app.run()