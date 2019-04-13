import tkinter as tk
import requests
import sqlite3
from sqlite3 import Error
from PIL import ImageTk, Image
from io import BytesIO
import sys

class Card():
	def __init__(self, name=None, price=None, image=None):
		self.name = name
		self.price = price
		self.image = image


def create_connection(db_file):
	#create db connection to sqlite3 db
	#creates db if missing

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
	#finally:
		#conn.close()

	return None

def create_table(conn, create_table_sql):
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def push_to_collection():
	global currentCard

	db = "testdb.db"
	conn = create_connection(db)

	sql = """INSERT INTO collection(name, price, image)
			 VALUES(?,?,?)"""

	a = (currentCard.name, currentCard.price, currentCard.image)
	
	cur = conn.cursor()
	cur.execute(sql, a)
	conn.commit()

	print(cur.lastrowid)
	return cur.lastrowid

def query_first(conn):
	sql = """SELECT * FROM collection WHERE id=1;"""

	cur = conn.cursor()
	cur.execute(sql)

	return cur.fetchall()


def mainSQL():
	db = "testdb.db"

	sql_collection_table = """ CREATE TABLE IF NOT EXISTS collection (
									id integer PRIMARY KEY,
									name text NOT NULL,
									price text,
									image blob
								);"""

	conn = create_connection(db)

	with conn:
		create_table(conn, sql_collection_table)
	conn.close()

		# with open("c16-143-burgeoning.jpg", 'rb') as image:
		# 	f = image.read()
		# 	im = bytes(f)
		
		# 	card = ('Burgeoning', '5', im)
		# 	push_to_collection(conn, card)

		# for i in query_first(conn): 
		# 	print(type(i[3]))
		# 	print(type(BytesIO(i[3])))

		# 	#for some reason rabim buffer ˇ
		# 	#!!ask slak
		# 	im = Image.open(BytesIO(i[3]))
		# 	#im.show()

def test():
	print("Test")

def searchCard():
	card = requests.get("https://api.scryfall.com/cards/named?fuzzy={}".format(searchTxt.get())).json()
	
	#crashes if card not found
	global currentCard
	currentCard.name = card["name"]
	currentCard.price = card['prices']['eur']
	currentCard.image = requests.get(card["image_uris"]["small"]).content

	i = ImageTk.PhotoImage(Image.open(BytesIO(currentCard.image)))

	global imgRefs
	imgRefs.append(i)

	tk.Button(root, image=i).grid(row=2, rowspan=2)

	tk.Label(root, text=currentCard.name).grid(row=2, column=1)
	tk.Label(root, text="{}\u20AC".format(currentCard.price)).grid(row=3, column=1)

if __name__ == '__main__':
	"""TODO:
	-save img to db on img click
	"""
	currentCard = Card("Burgeoning", "5.28")

	mainSQL()
	imgRefs = []


	root = tk.Tk()
	root.title("Amazing app")

	searchTxt = tk.Entry(root)
	searchTxt.grid(row=0, column=0,sticky=tk.W+tk.E+tk.N+tk.S)

	tk.Button(root, text="Search", command=searchCard).grid(row=0, column=1,sticky=tk.W+tk.E+tk.N+tk.S)
	tk.Button(root, text="Tester", command=push_to_collection).grid(row=1, sticky=tk.W+tk.E+tk.N+tk.S)
	tk.Button(root, text='Quit', command=root.destroy).grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

	# i = ImageTk.PhotoImage(Image.open("t.jpg"))
	
	# cardButton = tk.Button(root, image=i)
	# cardButton.grid(row=2, columnspan=2)

	root.mainloop()