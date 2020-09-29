from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/country_info'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    cities = db.relationship('City', backref='region', cascade="all, delete", order_by='City.name', lazy='joined')

    def __repr__(self):
        return f'{self.name}'


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)

    def __repr__(self):
        return f'{self.name}'


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'{self.name}'


@app.route('/hello')
def hello():
    return 'Hello, World!'


def token_required(f):
    @wraps(f)
    def wraper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(id=data['id']).first()
        except Exception as e:
            print(e)
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return wraper


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = Users.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            app.config['SECRET_KEY']
        )

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/region', methods=['GET'])
def get_all_regions():
    regions = Region.query.order_by(Region.name).all()

    output = []
    for reg in regions:
        reg_data = {
            'id': reg.id,
            'name': reg.name,
            'cities': list(map(str, reg.cities))
        }
        output.append(reg_data)

    return {'regions': output}


@app.route('/region/<region_id>', methods=['GET'])
def get_one_region(region_id):
    region = Region.query.get(region_id)
    if not region:
        return jsonify({'message': 'No region found!'})

    output = {'region': {
        'id': region.id,
        'name': region.name,
        'cities': list(map(str, region.cities))
    }}

    return jsonify(output)


@app.route('/region', methods=['POST'])
@token_required
def create_region(current_user):
    data = request.get_json()
    region = Region(name=data['name'])
    db.session.add(region)
    db.session.commit()

    return jsonify({'message': f"Region {data['name']} created!"})


@app.route('/region/<region_id>', methods=['PUT'])
@token_required
def update_region(current_user, region_id):
    region = Region.query.get(region_id)
    data = request.get_json()

    if not region:
        return jsonify({'message': 'No region found!'})

    region.name = data['name']
    db.session.commit()
    return jsonify({'message': f"Region {region.name} updated!"})


@app.route('/region/<id>', methods=['DELETE'])
@token_required
def delete_region(current_user, region_id):
    region = Region.query.get(region_id)
    if not region:
        return jsonify({'message': 'No region found!'})

    db.session.delete(region)
    db.session.commit()
    return jsonify({'message': f"Region {region.name} deleted!"})


@app.route('/city', methods=['GET'])
def get_all_cities():
    cities = City.query.order_by(City.name).all()

    output = []
    for ct in cities:
        city_data = {
            'id': ct.id,
            'name': ct.name,
            'region': Region.query.get(ct.region_id).name
        }
        output.append(city_data)

    return {'cities': output}


@app.route('/city/<city_id>', methods=['GET'])
def get_one_city(city_id):
    city = City.query.get(city_id)
    if not city:
        return jsonify({'message': 'No city found!'})

    output = {'city': {
        'id': city.id,
        'name': city.name,
        'region': city.region.name
    }}

    return jsonify(output)


@app.route('/city/region/<region_id>', methods=['GET'])
def get_city_by_region_name(region_id):
    cities = City.query.filter_by(region_id=region_id)

    if not cities:
        return jsonify({'message': 'No city found!'})

    output = {'cities': list(map(str, cities))}

    return jsonify(output)


@app.route('/city', methods=['POST'])
@token_required
def create_city(current_user):
    data = request.get_json()
    city = City(name=data['name'], region_id=data['region_id'])
    db.session.add(city)
    db.session.commit()

    return jsonify({'message': f"City {data['name']} created!"})


@app.route('/city/<id>', methods=['PUT'])
@token_required
def update_city(current_user, city_id):
    city = City.query.get(city_id)
    data = request.get_json()

    if not city:
        return jsonify({'message': 'No city found!'})

    city.name = data['name']
    city.region_id = data['region_id']
    db.session.commit()
    return jsonify({'message': f"City {city.name} updated!"})


@app.route('/city/<id>', methods=['DELETE'])
@token_required
def delete_city(current_user, city_id):
    city = City.query.get(city_id)
    if not city:
        return jsonify({'message': 'No city found!'})

    db.session.delete(city)
    db.session.commit()
    return jsonify({'message': f"Region {city.name} deleted!"})


if __name__ == '__main__':
    app.run(debug=True)
