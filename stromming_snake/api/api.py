from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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
    curr_video_file = stream_handler.get_output_file()
    return curr_video_file

@app.get("/video")
async def video_endpoint():
    try:
        video_file = stream_handler.get_output_file()
        def iterfile():
            with open(video_file, mode="rb") as file_like:
                yield from file_like
        return StreamingResponse(iterfile(), media_type="video/mp4")
    except AttributeError as e:
        raise HTTPException(status_code=404, detail="Tiles not generated")