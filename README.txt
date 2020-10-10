Тестовое задание для компании "Университет 20.35"

Последовательность запуска:
-python create_and_populate_db.py
-flask run

GET /login. Basic Auth (например admin:pas123). В ответе токен, который
передается в header x-access-token для POST, PUT, DELETE запросов.

GET /region - выборка по всем регионам
GET /region/<id> - просмотр одного региона
POST /region - добавление региона. Передать raw JSON {"name" : "Region name"}
PUT /region/<id> - изменить существующий регион. Передать raw JSON {"name" : "New region name"}
DELETE /region/<id> - удалить регион

GET /city - выборка по всем городам
GET /city/<id> - просмотр одного города
GET /city/region/<region_id> просмотр городов по региону
POST /city - добавление города. Передать raw JSON {"name" : "City name", "region_id": id}
PUT /city/<id> - изменение города. Передать raw JSON {"name" : "New city name", "region_id": id}
DELETE /city/<id> - удаление города
