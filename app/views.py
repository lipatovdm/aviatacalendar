from app import app
from pymongo import MongoClient
from bson import BSON
from bson import json_util
import pprint
import json
import datetime
import time
from flask import jsonify, request, render_template, Response
from bson.son import SON

client = MongoClient('aviata.kz', 27017)
db = client.air
air_search = db['search_stat']

@app.route('/fetch_results')
def fetch_dest_results():
	city_from = request.args['city_from']
	city_to = request.args['city_to']

	date_from = datetime.datetime.today() - datetime.timedelta(days=5)
	date_to = datetime.datetime.today() - datetime.timedelta(days=0)
	f_date_from = datetime.datetime.today() + datetime.timedelta(days=0)
	f_date_to = datetime.datetime.today() + datetime.timedelta(days=90)
	flight_type = "oneway"
	cabin_class = "Economy"

	pipeline = [
	{"$match": {
		# "domestic": is_domestic,
		"created": {"$gte": date_from, "$lte": date_to},
		"flight_type" : flight_type,
		"cabin_class": cabin_class,
		"routes": [city_from, city_to],
		"flight_dates": {"$gte": f_date_from, "$lte": f_date_to},
		"adults": 1,
		}},
	{"$project": {
			"_id": "$flight_dates",
			"cheapest_price": "$cheapest.price",
			"created" : "$created"
	}},
	{"$group":{
			"_id": "$_id",
			"min_price": {"$min": "$cheapest_price"},
			'created': {"$first": "$created"}
	}}]

	mongo_response = air_search.aggregate(pipeline)
	result = []

	for item in mongo_response:
		item["flight_date"] = item["_id"][0].strftime("%d.%m.%Y")
		result.append(item)
	
	return jsonify(result)

@app.route('/fetch_results_map')
def fetch_dest_results_map():
	city_from = request.args['city_from']
	flight_type = request.args['flight_type']

	date_from = datetime.datetime.today() - datetime.timedelta(days=5)
	date_to = datetime.datetime.today() - datetime.timedelta(days=0)
	f_date_from = datetime.datetime.today() + datetime.timedelta(days=0)
	f_date_to = datetime.datetime.today() + datetime.timedelta(days=90)
	# flight_type = "oneway"
	cabin_class = "Economy"

	pipeline = [
	{"$match": {
		"created": {"$gte": date_from, "$lte": date_to},
		"flight_type" : flight_type,
		"cabin_class": cabin_class,
		"flight_dates": {"$gte": f_date_from, "$lte": f_date_to},
		"adults": 1,
		}},
	{"$project": {
			"_id": "$flight_dates",
			"city_name": "$routes_repr",
			"routes": "$routes",
			"date_from": "$flight_dates",
			"cheapest_price": "$cheapest.price",
			"created" : "$created"
	}},
	{"$group":{
			"_id": "$_id",
			"routes": {"$first": "$routes"},
			"city_name": {"$first": "$city_name"},
			"min_price": {"$min": "$cheapest_price"},
			'created': {"$first": "$created"}
	}}]

	mongo_response = air_search.aggregate(pipeline)
	result = []
	
	if flight_type == 'oneway':
		for item in mongo_response:
			if item['routes'][0][0] == city_from:
				item["flight_date_from"] = item["_id"][0].strftime("%d.%m.%Y")
				item['city_name'] = item['city_name'][0][0]
				result.append(item)

	return jsonify(result)