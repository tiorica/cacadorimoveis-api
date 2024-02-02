# API APPLICATION FOR CACADORIMOVEIS

from datetime import datetime
import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

from messaging.sender import message_broker_send_message

application = Flask(__name__)
application.config['SECRET_KEY'] = 'minha_chave_123'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cacadorimoveis.db'

login_manager = LoginManager()
db = SQLAlchemy(application)
login_manager.init_app(application)
login_manager.login_view = 'login'
CORS(application)

# Modelagem
# User (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

# Scrap(id, date_time_initial, date_time_end, real_state_id, protocol)
class Scrap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time_initial = db.Column(db.DateTime, nullable=False)
    date_time_end = db.Column(db.DateTime, nullable=True)
    real_state_id = db.Column(db.Integer, db.ForeignKey('real_state.id'), nullable=False)
    protocol = db.Column(db.String(36), nullable=False)

# RealState(id, name, display_name, url_site, url_for_sale, url_to_rent, xpath_to_check_valid_page, card_xpath, properties_list_xpath, platform)
class RealState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(240), nullable=False)
    url_site = db.Column(db.String(120), nullable=False)
    url_for_sale = db.Column(db.String(120), nullable=False)
    url_to_rent = db.Column(db.String(120), nullable=False)
    xpath_to_check_valid_page = db.Column(db.String(240), nullable=False)
    card_xpath = db.Column(db.String(240), nullable=False)
    properties_list_xpath = db.Column(db.String(240), nullable=False)
    platform = db.Column(db.String(120), nullable=False)
    scrap = db.relationship('Scrap', backref='real_state', lazy=True)

# Authentication
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  

# Routes
# Root route
@application.route('/')
def main_route():
    return jsonify({"application:": "cacadorimoveis-api","version":"0.0.1"})

@application.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({"message": "User logged in"}), 200
    
    return jsonify({"message": "Unauthorized! Invalid credentials."}), 400
    
@application.route('/logout', methods=["POST"])
# @login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out"}), 200 

# Real State Routes
# Real State list route
@application.route('/api/real_state', methods=["GET"])
def get_all_real_state():
    response_real_state_list = RealState.query.all()
    real_state_list = []
    for real_state in response_real_state_list:
        real_sate_data = {
            "id": real_state.id,
            "name": real_state.name
        }
        real_state_list.append(real_sate_data)
    
    return jsonify(real_state_list)

# Real State add route
@application.route('/api/real_state/add', methods=["POST"])
@login_required
def real_state_add():
    data = request.json
    if 'name' in data and 'url_for_sale' and 'url_to_rent' in data:
        real_state = RealState(
            name=data["name"],
            display_name=data["display_name"],
            url_site=data["url_site"],
            url_for_sale=data["url_for_sale"], 
            url_to_rent=data["url_to_rent"],
            xpath_to_check_valid_page=data["xpath_to_check_valid_page"],
            card_xpath=data["card_xpath"],
            properties_list_xpath=data["properties_list_xpath"],
            platform=data["platform"]
        )
        db.session.add(real_state)
        db.session.commit()
        return jsonify({"message": "Real State inserterd in Database"}), 200 
    return jsonify({"message": "Invalid Real State data"}), 400

# Scrape routes
# Route to request new scrap for the correspond real_state_id
@application.route('/api/scrap/add/<int:real_state_id>', methods=["POST"])
@login_required
def scrap_add(real_state_id):
    if real_state_id:
        real_state = RealState.query.get(real_state_id)
        # Save new request protocol
        new_protocol = str(uuid.uuid4())
        scrap = Scrap(date_time_initial=datetime.now(), real_state_id=real_state_id, protocol=new_protocol)
        db.session.add(scrap)
        db.session.commit()

        # Publish a message to the scraper-queue
        message_broker_send_message(f"Message test with the real_state: {real_state.name}")
        return jsonify({
            "message": "New scrap successfuly requested",
            "protocol": scrap.protocol,
            "date_time_initial": scrap.date_time_initial
            })
    return jsonify({"message": "Fail to request new scrap"}), 500


if __name__ == "__main__":
    application.run(debug=True)