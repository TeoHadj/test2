from sqlalchemy import select
from sqlalchemy.orm import Session

from database import (
    engine,
    Song,
    Artist,
    Genre,
    Song_Artist,
    Song_Genre,
)

def get_all_songs():
    with Session(engine) as session:
        return session.scalars(select(Song)).all()


def get_all_artists():
    with Session(engine) as session:
        return session.scalars(select(Artist)).all()


def get_all_genres():
    with Session(engine) as session:
        return session.scalars(select(Genre)).all()


def get_all_song_artists():
    with Session(engine) as session:
        return session.scalars(select(Song_Artist)).all()


def get_all_song_genres():
    with Session(engine) as session:
        return session.scalars(select(Song_Genre)).all()



def print_full_song_view():
    print("\n=== FULL SONG VIEW ===")
    with Session(engine) as session:
        stmt = (
            select(
                Song.name,
                Artist.name,
                Genre.name,
                Song_Artist.album
            )
            .join(Song_Artist, Song.song_id == Song_Artist.song_id)
            .join(Artist, Artist.artist_id == Song_Artist.artist_id)
            .join(Song_Genre, Song.song_id == Song_Genre.song_id)
            .join(Genre, Genre.genre_id == Song_Genre.genre_id)
        )

        for song, artist, genre, album in session.execute(stmt):
            print(
                f"Song='{song}', "
                f"Artist='{artist}', "
                f"Genre='{genre}', "
                f"Album='{album}'"
            )
