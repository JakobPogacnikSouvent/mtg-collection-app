import json
import sqlite3
#import ast
import time
import requests
import urllib

def insert(data, conn):
	sql = """INSERT INTO Card(name, front_side_link, back_side_link)
			 VALUES(?,?,?)"""

	cur = conn.cursor()
	cur.execute(sql, data)

	return cur.lastrowid

def create_connection(db_file):
	#create db connection to sqlite3 db
	#creates db if missing

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)

	return None

def create_table(conn, create_table_sql):
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def mainSQL(conn):
	sql_collection_table = """ CREATE TABLE IF NOT EXISTS Card (
									id integer PRIMARY KEY,
									name text NOT NULL,
									front_side_link text NOT NULL,
									back_side_link text,
									front_image blob,
									back_image blob
								);"""

	with conn:
		create_table(conn, sql_collection_table)

if __name__ == "__main__":
	db = "minimal.db"
	conn = create_connection(db)
	
	mainSQL(conn)

	startTime = time.time()

	with open("scryfall-default-cards.json", 'r') as file:
		for line in file:
			cardData = json.loads(line.strip()[:-1])


			#EAFP
			try:
				data = (cardData['name'], cardData['image_uris']['small'], None)
			
			except KeyError:
				#On double faced cards
				data = (cardData['name'], cardData['card_faces'][0]['image_uris']['small'],cardData['card_faces'][1]['image_uris']['small'])
			
			r = insert(data, conn)

			if (r/10000).is_integer():
				print(f"----- {time.time()-startTime}")
			
	conn.commit()