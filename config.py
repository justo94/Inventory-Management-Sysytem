from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
import datetime
from peewee import*
from os import path
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///midlands.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', backref='product', lazy=True)
    batches = db.relationship('Batch', backref='product', lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rfid = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


# Forms
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('manager', 'Manager'), ('accountant', 'Accountant'), ('staff', 'Staff')], validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class OrderForm(FlaskForm):
    product = SelectField('Product', coerce=int, validators=[DataRequired()])
    customer = StringField('Customer', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Place Order')


class UpdateOrderForm(FlaskForm):
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Delivered', 'Delivered')], validators=[DataRequired()])
    submit = SubmitField('Update Order Status')


class UpdateInventoryForm(FlaskForm):
    rfid = StringField('RFID', validators=[DataRequired()])
    submit = SubmitField('Update Inventory')
