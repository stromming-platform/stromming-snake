from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from combiner.stream_handler import stream_handler

app = FastAPI()

class ApiTile(BaseModel):
    source: str
    x_pos: int
    y_pos: int
    audio: bool

class TileList(BaseModel):
    tiles: List[ApiTile] = []

@app.post("/tiles")
def create_tile(tiles: TileList):
    for _, x in tiles:
        for tile in x:
            stream_handler.add_tile(tile.source, tile.x_pos, tile.y_pos, tile.audio)
    stream_handler.create_tiled_stream()
    stream_handler.reset_tiles()
    return stream_handler.get_output_file()

