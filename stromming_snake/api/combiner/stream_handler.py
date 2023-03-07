from .streams import StreamTiler, Tile

class StreamHandler():
    tiles = []
    sT: StreamTiler
    sources = []

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

    def remove_output_file(self):
        self.sT.delete_output_file()

stream_handler = StreamHandler()