import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import insert






class Base(orm.DeclarativeBase, orm.MappedAsDataclass):
    pass


class Artist(Base):
    __tablename__ = "artist"

    artist_id: orm.Mapped[int] = orm.mapped_column(
        init=False,
        primary_key=True,
        repr=False
    )
    name: orm.Mapped[str] = orm.mapped_column()

    songs: orm.Mapped[list['Song']] = orm.relationship(
        # This is the other half of the many-to-many
        # relationship declared in the `Pupil` class

        default_factory=list,
        secondary='song_artist',
        back_populates="artists",
        # This has to be the same attribute as declared
        # in the `Pupil` class

        repr=False
    )


class Song(Base):
    __tablename__ = "song"

    song_id: orm.Mapped[int] = orm.mapped_column(
        init=False,
        primary_key=True,
        repr=False
    )
    name: orm.Mapped[str] = orm.mapped_column()
    duration: orm.Mapped[int] = orm.mapped_column()
    release_year: orm.Mapped[str] = orm.mapped_column()
    spotify_id: orm.Mapped[str] = orm.mapped_column()

    genres: orm.Mapped[list['Genre']] = orm.relationship(
        # This is the other half of the many-to-many
        # relationship declared in the `Pupil` class

        default_factory=list,
        secondary='song_genre',
        back_populates="songs",
        # This has to be the same attribute as declared
        # in the `Pupil` class

        repr=False
    )

    artists: orm.Mapped[list['Artist']] = orm.relationship(
        # This is the other half of the many-to-many
        # relationship declared in the `Pupil` class

        default_factory=list,
        secondary='song_artist',
        back_populates="songs",
        # This has to be the same attribute as declared
        # in the `Pupil` class

        repr=False
    )

class Genre(Base):
    __tablename__ = "genre"

    genre_id: orm.Mapped[int] = orm.mapped_column(
        init=False,
        primary_key=True,
        repr=False
    )
    name: orm.Mapped[str] = orm.mapped_column()

    songs: orm.Mapped[list['Song']] = orm.relationship(
        # This is the other half of the many-to-many
        # relationship declared in the `Pupil` class

        default_factory=list,
        secondary='song_genre',
        back_populates="genres",
        # This has to be the same attribute as declared
        # in the `Pupil` class

        repr=False
    )


class Song_Genre(Base):
    __tablename__ = "song_genre"

    # This is the link table to facilitate the
    # many-to-many relationship. We don't need this to
    # be a class and can create the table at a lower
    # level in `sqlalchemy`, but this approach is sufficient.
    # There will be methods `PupilSubject.__init__` and
    # `PupilSubject.__repr__` but we don't need them.
    # If we are to use the class in any way then the fields
    # will need to have `init=False` added to them.

    song_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('song.song_id'),
        primary_key=True
    )
    genre_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('genre.genre_id'),
        primary_key=True
    )

class Song_Artist(Base):
    __tablename__ = "song_artist"

    # This is the link table to facilitate the
    # many-to-many relationship. We don't need this to
    # be a class and can create the table at a lower
    # level in `sqlalchemy`, but this approach is sufficient.
    # There will be methods `PupilSubject.__init__` and
    # `PupilSubject.__repr__` but we don't need them.
    # If we are to use the class in any way then the fields
    # will need to have `init=False` added to them.

    song_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('song.song_id'),
        primary_key=True
    )
    artist_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('artist.artist_id'),
        primary_key=True
    )
    album: orm.Mapped[str] = orm.mapped_column()

engine = sqlalchemy.create_engine("sqlite+pysqlite:///pupils.sqlite", echo=False)

Base.metadata.create_all(engine)

def reset_database():
    """
    DEV ONLY.
    Drops all tables and recreates them from ORM models.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def populate_database(song_names, song_artists, song_duration, song_release_dates, song_albums, song_genres, song_ids):
    db_song_artists = []
    db_song_genres = []
    song_artist_match = [[] for _ in range(len(song_names))]
    song_genre_match = [[] for _ in range(len(song_names))]


    for artists in song_artists:
        for artist in artists:
            if artist not in db_song_artists:
                db_song_artists.append(artist)

    for genres in song_genres:
        for genre in genres:
            if genre not in db_song_genres:
                db_song_genres.append(genre)

    for i in range(len(song_names)):
        for artist in song_artists[i]:
            song_artist_match[i].append(db_song_artists.index(artist) + 1)

    for i in range(len(song_names)):
        for genre in song_genres[i]:
            song_genre_match[i].append(db_song_genres.index(genre) + 1)

    # --- INSERT INTO DB ---
    with orm.Session(engine) as session:

        for i in range(len(song_names)):
            session.execute(
                insert(Song),
                {
                    "song_id": i + 1,
                    "name": song_names[i],
                    "duration": song_duration[i],
                    "release_year": song_release_dates[i],
                    "spotify_id": song_ids[i]
                },
            )

        for i, artist in enumerate(db_song_artists):
            session.execute(
                insert(Artist),
                {"artist_id": i + 1, "name": artist},
            )

        for i, genre in enumerate(db_song_genres):
            session.execute(
                insert(Genre),
                {"genre_id": i + 1, "name": genre},
            )

        for i in range(len(song_names)):
            for artist_id in song_artist_match[i]:
                session.execute(
                    insert(Song_Artist),
                    {
                        "song_id": i + 1,
                        "artist_id": artist_id,
                        "album": song_albums[i],
                    },
                )

        for i in range(len(song_names)):
            for genre_id in song_genre_match[i]:
                session.execute(
                    insert(Song_Genre),
                    {"song_id": i + 1, "genre_id": genre_id},
                )

        session.commit()