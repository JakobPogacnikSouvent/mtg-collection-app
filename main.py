import tkinter as tk
import requests
import sqlite3
from sqlite3 import Error
from PIL import ImageTk, Image
from io import BytesIO
import sys

class Card():
	"""
	Simple class to keep card data in one place

	name = name of the card; string
	price = price of the card; string
	image = card image; ImageTk 
	"""

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

def query_all(conn):
	sql = """SELECT * FROM collection;"""

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

def collectionWindow():
	top = tk.Toplevel()
	top.title("About this application...")

	msg = tk.Message(top, text="Coolection")
	msg.pack()

	db = "testdb.db"
	conn = create_connection(db)
	for i in query_all(conn):
		print(i[1])

	button = tk.Button(top, text="Dismiss", command=top.destroy)
	button.pack()

class MainWindow(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		
		self.parent = parent
		parent.title = "Amazing app"

		self.db = "testdb.db"

		self.test = 'Test'

		self.currentCard = Card()

		self.searchTxt = tk.Entry(root)
		self.searchTxt.grid(row=0, column=0,sticky=tk.W+tk.E+tk.N+tk.S)

		tk.Button(root, text="Search", command=self.searchCard).grid(row=0, column=1,sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(root, text="Save to DB", command=self.push_to_collection).grid(row=1, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(root, text='Quit', command=root.destroy).grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

		tk.Button(root, text='C', command=self.c).grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(root, text='P', command=self.p).grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def searchCard(self):
		query = self.searchTxt.get()
		searchedCard = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={query}").json()
	
		#crashes if card not found
		self.currentCard.name = searchedCard["name"]
		self.currentCard.price = searchedCard['prices']['eur']
		
		self.currentCardImageBytes = requests.get(searchedCard["image_uris"]["small"]).content
		self.currentCard.image = ImageTk.PhotoImage(Image.open(BytesIO(self.currentCardImageBytes)))

		tk.Button(self.parent, image=self.currentCard.image).grid(row=3, rowspan=2)

		tk.Label(self.parent, text=self.currentCard.name).grid(row=3, column=1)
		tk.Label(self.parent, text=f"{self.currentCard.price}\u20AC").grid(row=4, column=1)

	def push_to_collection(self):
		conn = create_connection(self.db)

		sql = """INSERT INTO collection(name, price, image)
				 VALUES(?,?,?)"""

		a = (self.currentCard.name, self.currentCard.price, self.currentCardImageBytes)
		
		cur = conn.cursor()
		cur.execute(sql, a)
		conn.commit()

		print(cur.lastrowid)

	def c(self):
		self.test = "Changed"

	def p(self):
		print(sys.getsizeof(self.currentCardImageBytes))
		print(sys.getsizeof(self.currentCard.image))

		print(self.test)


if __name__ == '__main__':
	"""TODO:
	-save img to db on img click
	-relationship database za slike
	-save bulk data locally
	"""
	currentCard = Card("Burgeoning", "5.28")

	mainSQL()
	imgRefs = []


	root = tk.Tk()
	MainWindow(root).grid()
	root.mainloop()