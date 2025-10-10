from test import song_albums, song_release_dates, song_artists,song_duration,song_names

import sqlite3
connection = sqlite3.connect('song_database.db')
cursor = connection.cursor()
sqlite_select_query = """CREATE TABLE Artist(
ArtistID INTEGER PRIMARY KEY AUTOINCREMENT,
ArtistName TEXT) 

CREATE TABLE Song(
SongID INTEGER PRIMARY KEY AUTOINCREMENT,
Name TEXT,
Duration INTEGER,
ReleaseYear TEXT)


CREATE TABLE Artist_Song(
FOREIGN KEY(ArtistID) REFERENCES Artist (ArtistID),
FOREIGN KEY(SONGID) REFERENCES Song (SongID),
Album TEXT)

CREATE TABLE Genre(
GenreID INTEGER PRIMARY KEY AUTOINCREMENT,
Name TEXT)

CREATE TABLE Song_Genre(
FOREIGN KEY(SongID) REFERENCES Song (SongID)
FOREIGN KEY(GenreID) REFERENCES Genre (GenreID))"""
cursor.execute(sqlite_select_query)
records = cursor.fetchall()