from flask import render_template, Blueprint, request, flash, session, redirect, g, json, url_for
from flask_json import JsonError, json_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug import check_password_hash, generate_password_hash

from app_kkp import app, db, lm, json_kkp

from .models import Client, Order, OrderType, OrderStatus

from datetime import datetime


#Регистрируем основной url для клиента и объявляем его как переменную для дальнейшего использования
clients_brouser_blu = Blueprint('brouser_clients', __name__, url_prefix = '/brouser/clients')


#Используется чтобы получения клиента
@lm.user_loader
def load_client(id):
	return Client.query.get(int(id))

#Проверка авторизован ли пользователь или нет
@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.lastSeen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

#Получаем информацию о клиентах
@clients_brouser_blu.route('/')
def getClients():
	clients = Client.query.order_by(Client.id).all()

	return render_template('clients/clients.html', clients = clients)

#Метод для регистрации клиентов
@clients_brouser_blu.route('/singUpClient', methods = ['GET', 'POST'])
def singUpClient():
	form = RegisterClientForm(request.form)

	if form.validate_on_submit():
		client = Client(name = form.name.data, surname = form.surname.data, \
			patronymic = form.patronymic.data, phoneNumber = form.phoneNumber.data,\
			email = form.email.data, password = generate_password_hash(form.password.data))

		db.session.add(client)
		db.session.commit()

		session['remember_me'] = True

		flash('Thanks for registering')

		return redirect(url_for('clients.getClient', id = client.id))
	return render_template('clients/register.html', form = form)

#Метод для авторизации клиента
@clients_brouser_blu.route('/login', methods = ['GET', 'POST'])
def loginClient():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('clients.getClients'))

	form = LoginForm(request.form)

	if form.validate_on_submit():
		client = Client.query.filter(Client.email  ==  form.email.data).first()

		if client and check_password_hash(client.password, form.password.data):
			session['remember_me'] = form.remember_me.data

			remember_me = False
			if 'remember_me' in session:
				remember_me = session['remember_me']
				session.pop('remember_me', None)

			login_user(client, remember = remember_me)

		return redirect(url_for('clients.getClient', id = client.id))
	return render_template('clients/login.html', form = form)

#Метод для выхода из аккаунта
@clients_brouser_blu.route('/logout', methods = ['GET', 'POST'])
def logOutClient():
	logout_user()
	return redirect(url_for('clients.getClients'))

#Получаем информацию о конкретном клиенте
@clients_brouser_blu.route('/<int:id>/profile')
@login_required
def getClient(id):
	client = Client.query.filter(Client.id  ==  id).first()

	return render_template('clients/profile.html', client = client)

#Метод для изменения информации о своем аккаунте
@clients_brouser_blu.route('/<int:id>/profile/edit', methods = ['GET', 'POST'])
@login_required
def editProfile(id):
	form = EditClientForm(request.form)
	if form.validate_on_submit():
		g.user.name = form.name.data
		g.user.surname = form.surname.data
		g.user.patronymic = form.patronymic.data
		g.user.phoneNumber = form.phoneNumber.data
		#g.user.password = generate_password_hash(form.password.data)
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('clients.getClient', id = g.user.id))
	else:
		form.name.data = g.user.name
		form.surname.data = g.user.surname 
		form.patronymic.data = g.user.patronymic
		form.phoneNumber.data = g.user.phoneNumber
		#form.password.data = g.user.password
	return render_template('clients/profileEdit.html', client = g.user, form = form)
	
@clients_brouser_blu.route('/<int:id>/profile/editPhoto', methods = ['GET', 'POST'])
def editProfilePhoto(id):
	pass

#Метод для полечения информации о всех заказах
@clients_brouser_blu.route('/<int:id>/orders', methods = ['GET'])
def getOrders(id):
	client = Client.query.filter(Client.id  ==  id).first()
	clientOrders = client.orders

	return render_template('clients/orders.html', client = client, orders = clientOrders)

#Метод для создания заказа
@clients_brouser_blu.route('/<int:id>/orders/create', methods = ['GET', 'POST'])
def createOrder(id):
	form = CreateOrder(request.form)
	form.typeId.choices = [(t.id, t.name) for t in OrderType.query.order_by(OrderType.name)]
	form.statusId.choices = [(s.id, s.name) for s in OrderStatus.query.order_by(OrderStatus.name)]

	if form.validate_on_submit():
		order = Order(typeId = form.typeId.data, clientId = id,	statusId = form.statusId.data, issuePointId = None, \
			numberOfAddresses = form.numberOfAddresses.data, informationAboutAddresses = form.informationAboutAddresses.data, \
			description = form.description.data, cost = form.cost.data)

		db.session.add(order)
		db.session.commit()

		return redirect(url_for('orders.getOrder', id = order.id))
	return render_template('orders/createOrder.html', form = form)