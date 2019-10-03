import json
import sqlite3
#import ast
import time
import requests
import urllib

def insert(data, conn):
	sql = """INSERT INTO Card(name, front_image, back_image)
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
									front_image blob NOT NULL,
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
		for _ in range(1): 
			next(file)
			print('Skipped')
		for line in file:
			try:
				#Normally remove last char which is ,
				cardData = json.loads(line.strip()[:-1])

			except json.decoder.JSONDecodeError:
				#Triggered on last two lines
				
				try:
					#Second to last line does not have ,
					cardData = json.loads(line.strip())

				except json.decoder.JSONDecodeError:
					#Triggered on very last line
					break
			#EAFP
			try:
				front_image = requests.get(cardData['image_uris']['small']).content
				data = (cardData['name'], front_image, None)
			
			except KeyError:
				#On double faced cards
				front_image = requests.get(cardData['card_faces'][0]['image_uris']['small']).content
				back_image = requests.get(cardData['card_faces'][1]['image_uris']['small']).content
				data = (cardData['name'], front_image, back_image)
			
			r = insert(data, conn)
			conn.commit() #TODO: remove, commiting is slow

			if (r/1).is_integer():
				print(f"----- {time.time()-startTime}")
			
	#Commiting is slow. Only do it once.	
	conn.commit()