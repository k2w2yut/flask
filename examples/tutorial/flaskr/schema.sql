-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE users (
  id BIGSERIAL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  CONSTRAINT users_pkey PRIMARY KEY (id)
)
WITH (
	OIDS=FALSE
) ;

CREATE TABLE posts (
  id BIGSERIAL,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  CONSTRAINT posts_user_pkey PRIMARY KEY (id),
  CONSTRAINT posts_user_fkey FOREIGN KEY (author_id) REFERENCES users(id)
)
WITH (
	OIDS=FALSE
) ;
