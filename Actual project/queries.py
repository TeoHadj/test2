from sqlalchemy import select, func
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
        return session.scalars(select(Artist.name)).all()


def get_all_genres():
    with Session(engine) as session:
        return session.scalars(select(Genre.name)).all()


def get_all_song_artists():
    with Session(engine) as session:
        return session.scalars(select(Song_Artist)).all()


def get_all_song_genres():
    with Session(engine) as session:
        return session.scalars(select(Song_Genre)).all()

def get_all_spotify_ids():
    with Session(engine) as session:
        return session.scalars(select(Song.spotify_id)).all()

def get_song_with_genre(genre_list:list):
    genre_match = []
    with Session(engine) as session:
        stmt = (
            select(
                Song.name,
                Song.spotify_id,
                Artist.name,
                Song_Artist.album

            )
            .join(Song_Artist, Song.song_id == Song_Artist.song_id)
            .join(Artist, Artist.artist_id == Song_Artist.artist_id)
            .join(Song_Genre, Song.song_id == Song_Genre.song_id)
            .join(Genre, Genre.genre_id == Song_Genre.genre_id)
            .where(Genre.name.in_(genre_list))
            .group_by(Song.song_id, Song.name, Song.spotify_id, Artist.name, Song_Artist.album)
            .having(func.count(func.distinct(Genre.genre_id))== len(genre_list))

        )
    for song, spotifyID, artist, album in session.execute(stmt):

        genre_match.append([
            f"{song} - {artist} ({album})", f"spotify:track:{spotifyID}"]

        )
    return genre_match

def get_song_with_artist(artist_list: list):
    artist_match = []
    with Session(engine) as session:
        stmt = (
            select(
                Song.name,
                Song.spotify_id,
                Song_Artist.album

            )
            .join(Song_Artist, Song.song_id == Song_Artist.song_id)
            .join(Artist, Artist.artist_id == Song_Artist.artist_id)
            .where(Artist.name.in_(artist_list))
            .group_by(Song.song_id, Song.name, Song.spotify_id, Song_Artist.album)
            .having(func.count(func.distinct(Artist.artist_id)) == len(artist_list))

        )
    for song, spotifyID, album in session.execute(stmt):
        artist_match.append([
            f"{song} - ({album})", f"spotify:track:{spotifyID}"]

        )
    return artist_match

def get_song_with_year(year):
    year_match = []
    with Session(engine) as session:
        stmt = (
            select(Song.name, Song.spotify_id, Artist.name, Song_Artist.album)
            .join(Song_Artist, Song.song_id == Song_Artist.song_id)
            .join(Artist, Artist.artist_id == Song_Artist.artist_id)
            .where(func.substr(Song.release_year, 1, 4) == year)
            .group_by(Song.song_id, Song.name, Song.spotify_id, Song_Artist.album)
        )

    for song, spotifyID, artist, album in session.execute(stmt):
        year_match.append([
            f"{song} - {artist} ({album})", f"spotify:track:{spotifyID}"]

        )
    return year_match


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

def genre_count(session, genre):

    stmt = (
        select(func.count(func.distinct(Song_Genre.song_id)))
        .join(Genre, Song_Genre.genre_id == Genre.genre_id)
        .where(Genre.name == genre)
    )
    return session.scalar(stmt)

def artist_count(session, artist):

    stmt = (
        select(func.count(func.distinct(Song_Artist.song_id)))
        .join(Artist, Song_Artist.artist_id == Artist.artist_id)
        .where(Artist.name == artist)
    )
    return session.scalar(stmt)

def genre_count_with_artist_name(session, genre, name):

    stmt = (
        select(func.count(func.distinct(Song_Genre.song_id)))
        .join(Genre, Song_Genre.genre_id == Genre.genre_id)
        .join(Song_Artist, Song_Artist.song_id == Song_Genre.song_id)
        .join(Artist, Artist.artist_id == Song_Artist.artist_id)
        .where(Genre.name == genre)
        .where(Artist.name == name)
    )

    return session.scalar(stmt)



#print(genre_count_with_artist_name("pop", "Maroon 5"))
#print(get_song_with_genre(["uk r&b"]))
#print(get_song_with_artist(["Travis Scott", "SZA"]))
#print(get_song_with_year("2008"))
#
# with Session(engine) as session:
#     print(artist_count(session, "2Pac"))
#     print(genre_count(session, "blues"))