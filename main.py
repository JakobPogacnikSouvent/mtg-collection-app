import tkinter as tk
import requests
import sqlite3
from PIL import ImageTk, Image
from io import BytesIO
import sys

class Card():
	"""
	A class used to represent a card.
	
	...
	
	Attributes:
	----------
	name : str
		The name of the card. (Default None)

	price : str
		The price of the card. (Default None)

	image : ImageTk
		The card image saved as ImageTK. (Default None)
	
	"""

	def __init__(self, name=None, price=None, image=None):
		self.name = name
		self.price = price
		self.image = image


def create_connection(db_file):
	"""
	Creates connection to database file.
	Creates database file if it's missing.

	Parameters:
	----------
	db_file: str
		Path to database file in string.

	Returns:
	----------
	sqlite3 connection object.
	If error is raised returns None.

	"""

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except sqlite3.Error as e:
		#TkMessagebox
		print(e)

	return None

def create_table(conn, create_table_sql):
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except sqlite3.Error as e:
		print(e)

def query_all(conn):
	sql = """SELECT * FROM collection;"""

	cur = conn.cursor()
	cur.execute(sql)

	return cur.fetchall()


def sql_setup():
	DB = "testdb.db"

	sql_collection_table = """ CREATE TABLE IF NOT EXISTS collection (
									id integer PRIMARY KEY,
									name text NOT NULL,
									price text,
									image blob
								);"""

	conn = create_connection(DB)

	with conn:
		create_table(conn, sql_collection_table)
	conn.close()

def collectionWindow():
	"""
	Work in progress.
	Will be it's own class.
	"""
	top = tk.Toplevel()
	top.title("About this application...")

	msg = tk.Message(top, text="Coolection")
	msg.pack()

	# db = "testdb.db"
	# conn = create_connection(db)
	# for i in query_all(conn):
	# 	print(i[1])

	button = tk.Button(top, text="Dismiss", command=top.destroy)
	button.pack()

class CollectionWindow(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)

		self.parent = parent
			
		self.images = []

		self.canvas=tk.Canvas(self.parent, background="blue")
		self.canvas_frame=tk.Frame(self.canvas)

		self.scrollbar = tk.Scrollbar(self.parent,orient="vertical",command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollbar.set)

		self.canvas.grid(row=0, column=0)
		self.scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
		self.canvas.create_window((0,0),window=self.canvas_frame)

		self.canvas_frame.bind("<Configure>",self.myfunction)

		self.create_buttons()
		
		tk.Button(self.parent, text='Quit', command=self.parent.destroy).grid(row=1, column=0)

	def myfunction(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=event.width, height=100)


	def create_buttons(self):
		conn = create_connection("testdb.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM collection;")
		for row in cur:
			i, name, price, img = row
			if not img: continue
			if i > 5: break
			pic = ImageTk.PhotoImage(Image.open(BytesIO(img)))
			self.images.append(pic)
			tk.Button(self.canvas_frame, text=name, image=pic).grid()



class MainWindow(tk.Frame):
	
	#class variable ˇ samo enkrat, za vse classe
	DB = "testdb.db"
	
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		#super

		parent.title("Test")
		parent.bind("<Configure>", self.test)
		self.parent = parent

		"""
		try:
			self.conn = sqlite3 connection
		except sqlite3.Error:
			TkMessagebox
			#Display error

		"""

		self.currentCard = Card()

		self.searchTxt = tk.Entry(self.parent)
		self.searchTxt.grid(row=0, column=0,sticky=tk.W+tk.E+tk.N+tk.S)

		tk.Button(self.parent, text="Search", command=self.search_card).grid(row=0, column=1,sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text="Save to DB", command=self.push_to_collection).grid(row=1, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text='Quit', command=self.parent.destroy).grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

		tk.Button(self.parent, text='C', command=self.create_window).grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text='P', command=self.p).grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S)


	def search_card(self):
		""" """
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
		conn = create_connection(self.DB)

		sql = """INSERT INTO collection(name, price, image)
				 VALUES(?,?,?)"""

		cardData = (self.currentCard.name, self.currentCard.price, self.currentCardImageBytes)
		
		cur = conn.cursor()
		cur.execute(sql, cardData)
		conn.commit()

		print(cur.lastrowid)

	def test(self, tkConfigureEvent):
		print(tkConfigureEvent)
		print(type(tkConfigureEvent))

	def p(self):
		self.x.parent.destroy()

	def create_window(self):
		self.x = CollectionWindow(tk.Toplevel(self.parent))


if __name__ == '__main__':
	"""TODO:
	-save img to db on img click
	-relationship database za slike
	-save bulk data locally
	"""
	sql_setup()

	root = tk.Tk()
	MainWindow(root).grid()

	try:
		root.mainloop()
	except Exception as e:
		print(e)
		#print whole traceback
		#import traceback