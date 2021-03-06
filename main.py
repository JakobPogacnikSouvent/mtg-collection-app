import tkinter as tk
import requests
import sqlite3
from PIL import ImageTk, Image
from io import BytesIO
import sys
import time

class Card():
	"""
	A class used to represent a card.
	
	Attributes:
		-name : str
			The name of the card. (Default None)
		-price : str
			The price of the card. (Default None)
		-image : ImageTk
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
		-db_file: str
			Path to database file in string.

	Returns:
		-sqlite3 connection object.
		OR
		-None if error is raised.
	"""

	try:
		conn = sqlite3.connect(db_file)
		conn.execute("PRAGMA foreign_keys = 1")
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

def query_by_name(conn, name, table="Card"):
	#TODO: change from fstring to cur.execute
	sql = f"""SELECT * FROM {table} WHERE name=\'{name}\'"""
		
	cur = conn.cursor()
	
	print(sql)
	cur.execute(sql)

	return cur

def sql_setup():
	DB = "collection.db"

	sql_collection_table = """ CREATE TABLE IF NOT EXISTS Collection (
									internal_id integer PRIMARY KEY,
									card_data_id integer NOT NULL,
									foreign key (card_data_id)
										references Card (id)
								);"""

	conn = create_connection(DB)

	with conn:
		create_table(conn, sql_collection_table)
	conn.close()

class CollectionWindow(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)

		sql_setup()

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
		conn = create_connection("collection.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM Collection;")
		for row in cur:
			i, name, price, img = row
			if not img: continue
			pic = ImageTk.PhotoImage(Image.open(BytesIO(img)))
			self.images.append(pic)
			tk.Button(self.canvas_frame, text=name, image=pic).grid()



class MainWindow(tk.Frame):
	#TODO: deprecate self.currentCard (will only be saving relation)
	
	#class variable ˇ samo enkrat, za vse classe
	DB = "collection.db"

	def _create_connection(self):
		#Deprecated
		print("_create_connection method is deprecatedT")
		sql_setup()

		conn = create_connection(self.ALL_CARDS_DB)
		
		sql = """ ATTACH DATABASE (?) AS collection;"""

		cur = conn.cursor()

		cur.execute(sql, (self.DB,))

		test = cur.execute("""SELECT * FROM Collection;""")
		
		return conn
		print("Conn created")


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

		tk.Button(self.parent, text="Search SF", command=self.search_card_scryfall).grid(row=0, column=1,sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text="Save to DB", command=self.foo).grid(row=1, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text='Quit', command=self.parent.destroy).grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

		tk.Button(self.parent, text='C', command=self.create_window).grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
		tk.Button(self.parent, text='Search DB', command=self.search_card_local_db).grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S)

	def search_card_local_db(self):
		"""
		Searches card in local db and displays it as a button.

		Uses image bytes in db to display image. Will find and save image if not exists.
		
		Crashes if no card found.
		"""

		start = time.time()

		query = self.searchTxt.get()
		conn = create_connection(self.DB)

		results = query_by_name(conn, query)
		
		end = time.time()
		print(end-start)

		id_, name, front_image_link, back_image_link, front_image_bytes, back_image_bytes = results.fetchall()[0] #Returns list of all versions of card

		try:
			#TODO: multy faced cards
			self.currentCard.image = ImageTk.PhotoImage(Image.open(BytesIO(front_image_bytes)))

		except OSError:
			#TODO: multy faced cards

			start = time.time()
			front_image_bytes = requests.get(front_image_link).content
			end = time.time()
			print(f"Image download time: {end-start}")

			self.currentCard.image = ImageTk.PhotoImage(Image.open(BytesIO(front_image_bytes)))
			self.insert_image_bytes(id_, front_image_bytes, back_image_bytes)


		tk.Button(self.parent, image=self.currentCard.image, command=lambda:self.push_to_collection(id_)).grid(row=3, rowspan=2)

		#id, name, *rest = results.fetchall()[0]
		#tk.Button(self.parent, text=name, command=lambda:print(rest)).grid(row=3, rowspan=2)

	def insert_image_bytes(self, id_, front_image_bytes, back_image_bytes):
		conn = create_connection(self.DB)
		sql = """ UPDATE Card 
				  SET front_image=?, back_image=? where id is ?;"""

		cur = conn.cursor()
		cur.execute(sql,(front_image_bytes, back_image_bytes, id_))
		conn.commit()

	def search_card_scryfall(self):
		#TODO: deprecate
		start = time.time()

		query = self.searchTxt.get()
		searchedCard = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={query}").json()
		

		#crashes if card not found
		self.currentCard.name = searchedCard["name"]
		self.currentCard.price = searchedCard['prices']['eur']
		
		self.currentCardImageBytes = requests.get(searchedCard["image_uris"]["small"]).content
		self.currentCard.image = ImageTk.PhotoImage(Image.open(BytesIO(self.currentCardImageBytes)))
		
		end = time.time()
		print(end-start)

		tk.Button(self.parent, image=self.currentCard.image).grid(row=3, rowspan=2)

		tk.Label(self.parent, text=self.currentCard.name).grid(row=3, column=1)
		tk.Label(self.parent, text=f"{self.currentCard.price}\u20AC").grid(row=4, column=1)


	def push_to_collection(self, all_cards_id):
		print("HERE")
		print(all_cards_id)

		#TODO: collection will only be a "pointer"
		conn = create_connection(self.DB)

		sql = """INSERT INTO Collection(card_data_id)
				 VALUES(?)"""
		
		cur = conn.cursor()
		cur.execute(sql, (all_cards_id,))
		conn.commit()

		print(cur.lastrowid)

	def foo(self):
		print("bar")

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
	-!one to many relation
	-separate class for search function
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