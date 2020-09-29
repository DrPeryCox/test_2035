import psycopg2
from app import db
from werkzeug.security import generate_password_hash

# create DB
connection = psycopg2.connect(
    database='postgres',
    user='postgres',
    password='postgres',
    host='localhost',
)
connection.autocommit = True
cur = connection.cursor()
cur.execute('CREATE DATABASE country_info;')
connection.close()

# create tables
db.create_all()

# populate tables
connection = psycopg2.connect(
    database='country_info',
    user='postgres',
    password='postgres',
    host='localhost',
)
cur = connection.cursor()

admin_pas = generate_password_hash('pas123', method='sha256')
user_pas = generate_password_hash('qwerty', method='sha256')

ins_users = f""" 
    INSERT INTO users (name, password) VALUES ('admin', '{admin_pas}');
    INSERT INTO users (name, password) VALUES ('user', '{user_pas}');
"""

ins_regions = """
    INSERT INTO region (id, name) VALUES (1, 'Moscow oblast');
    INSERT INTO region (id, name) VALUES (2, 'Vladimir oblast');
    INSERT INTO region (id, name) VALUES (3, 'Tver oblast');
"""

ins_cities = """
    INSERT INTO city (name, region_id) VALUES ('Moscow', 1);
    INSERT INTO city (name, region_id) VALUES ('Podolsk', 1);
    INSERT INTO city (name, region_id) VALUES ('Istra', 1);
    INSERT INTO city (name, region_id) VALUES ('Vladimir', 2);
    INSERT INTO city (name, region_id) VALUES ('Kirzhach', 2);
    INSERT INTO city (name, region_id) VALUES ('Alexandrov', 2);
    INSERT INTO city (name, region_id) VALUES ('Tver', 3);
    INSERT INTO city (name, region_id) VALUES ('Rzhev', 3);
"""

cur.execute(ins_users)
cur.execute(ins_regions)
cur.execute(ins_cities)
connection.commit()
connection.close()
