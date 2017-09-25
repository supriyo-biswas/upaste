import os
import sqlite3

db = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/data/db.sqlite")
db.execute("""
CREATE TABLE pastes (
	id CHAR(8) PRIMARY KEY,
	title TEXT,
	content TEXT NOT NULL,
	create_time INTEGER NOT NULL
)""")

print("Database has been set up.")
