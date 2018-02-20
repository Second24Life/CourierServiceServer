from flask import render_template, Blueprint, request, flash, session, redirect, g, json, url_for
from flask_json import JsonError, json_response
from flask_login import login_required

from app_kkp import app, db, lm, json_kkp

from clients.models import Order, Client, OrderType, OrderStatus, IssuePoint

from datetime import datetime



orders_brouser_blu = Blueprint('brouser_orders', __name__, url_prefix = '/brouser/orders')


@orders_brouser_blu.route('/')
def getOrders():
	orders = Order.query.order_by(Order.dateOfCreation).all()

	return render_template('orders/orders.html', orders = orders)

@orders_brouser_blu.route('/<int:id>')
@login_required
def getOrder(id):
	order = Order.query.filter(Order.id  ==  id).first()
	client = Client.query.filter(Client.id == order.clientId).first()
	orderType = OrderType.query.filter(OrderType.id == order.typeId).first()
	orderStatus = OrderType.query.filter(OrderType.id == order.statusId).first()

	return render_template('orders/order.html', order = order, client = client,\
	type = orderType, status = orderStatus)

@orders_brouser_blu.route('/free')
def getFreeOrders():
	orders = Order.query.order_by(Order.statusId == 5).all()

	return render_template('orders/orders.html', orders = orders)