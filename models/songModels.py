from pydantic import BaseModel

class Song_metadata(BaseModel):
    name: str
    title: str
    sub_title: str
    bitrate: int
    commentaries: str
    main_artist: str
    collaborators: str
    album_artist: str
    album: str
    year: str
    track_number: str
    genre: str
    duration: int