import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import insert
from test import song_names, song_artists, song_duration, song_release_dates, song_albums, song_genres

# `orm.DeclarativeBase` does all the magic for us
# `orm.MappedAsDataclass` enables us to use class
# declarations in the style of `@dataclass`
db_song_artists = song_artists
db_song_genres = song_genres
for i in range(len(db_song_artists)):
    db_song_artists[i] = db_song_artists[i][0]
    db_song_genres[i] = db_song_genres[i][0]
set(db_song_artists)
set(db_song_genres)

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
        back_populates="songs",
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

engine = sqlalchemy.create_engine("sqlite+pysqlite:///pupils.sqlite", echo=False)

with (orm.Session(engine) as session):
    for i in range(len(song_names)):

        session.execute(
            insert(Song),
            [
                {"song_id": i+1, "name": song_names[i][0], "duration": song_duration[i], "release_year": song_release_dates[i]}]
        )

    for i in range(len(song_artists)):
        session.execute(
            insert(Artist),
            [
                {"artist_id": i+1, "name": song_artists[i]}]
        )
    for i in range(len(song_genres)):
        session.execute(
            insert(Genre),
            [
                {"genre_id": i+1, "name": song_genres[i]}
            ]
        )
