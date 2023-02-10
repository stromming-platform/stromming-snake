from .streams import StreamTiler, Tile

class StreamHandler():
    tiles = []
    sT: StreamTiler

    def __init__(self) -> None:
        pass

    def add_tile(self, source, x_pos, y_pos, audio):
        self.tiles.append(Tile(source, x_pos, y_pos, audio))

    def create_tiled_stream(self):
        self.sT = StreamTiler(self.tiles)

    def get_output_file(self):
        return self.sT.output_file 
    
    def reset_tiles(self):
        self.tiles = []

stream_handler = StreamHandler()