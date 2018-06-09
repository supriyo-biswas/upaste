#!/usr/bin/env python3

import os
import sqlite3
from pygments.formatters import HtmlFormatter

self_dir = os.path.dirname(os.path.realpath(__file__))

print("Setting up database...", end="")

db = sqlite3.connect(self_dir + "/data/db.sqlite")
db.execute("""
CREATE TABLE IF NOT EXISTS pastes (
	id CHAR(8) PRIMARY KEY,
	title TEXT,
	lang CHAR(30) NOT NULL,
	hash VARCHAR(64) NOT NULL,
	create_time INTEGER NOT NULL
)""")

db.execute("""
CREATE TABLE IF NOT EXISTS contents (
	hash CHAR(64) PRIMARY KEY,
	contents TEXT NOT NULL
)
""")

print("done")

print("Generating stylesheets...", end="")

with open(self_dir + "/static/_pygments.css", "w") as f:
	f.write(HtmlFormatter().get_style_defs('.highlight'))

print("done")