CREATE TABLE users (
	id INTEGER PRIMARY KEY,
	name VARCHAR(32) UNIQUE,
	is_admin INTEGER
);

CREATE TABLE patterns (
	id INTEGER PRIMARY KEY,
	user_id INTEGER,
	pattern VARCHAR(64),
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE welcomes (
	id INTEGER PRIMARY KEY,
	user_id INTEGER,
	welcome VARCHAR(128),
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE seen (
	id INTEGER PRIMARY KEY,
	time TEXT,
	nick VARCHAR(32) UNIQUE,
	seen_reasons TEXT,
	args VARCHAR(64)
);
