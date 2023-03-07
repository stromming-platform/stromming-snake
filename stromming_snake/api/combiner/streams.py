import ffmpeg
import os
import uuid

from .helpers import fix_odd

# Create one object per tile?
class Tile():
    source = ""
    scaled_path = ""
    width = 0
    height = 0
    x_pos = 0
    y_pos = 0
    audio = False

    def __init__(self, source, x_pos, y_pos, audio) -> None:
         self.source = source
         self.x_pos = x_pos
         self.y_pos = y_pos
         self.audio = audio
         self.width, self.height = self.get_video_dimensions()
    
    def get_video_dimensions(self) -> None:
        # Takes a video file location and returns the dimensions of the source file
        probe = ffmpeg.probe(self.source)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        return fix_odd(width, height)
    
    def set_scaled_path(self, path):
        self.scaled_path = path

    def delete_scaled_file(self):
        if os.path.exists(self.scaled_path):
            os.remove(self.scaled_path)


class StreamTiler():
    div_factor_x = 0
    div_factor_y = 0
    baseHeight = 0
    baseWidth = 0
    base: any
    output_file = ""

    def __init__(self, tiles):
        # Set div factors to know how to divide tiles
        # and set the base canvas dimensions
        for tile in tiles:
            self.baseHeight = max(self.baseHeight, tile.height)
            self.baseWidth = max(self.baseWidth, tile.width)
            self.div_factor_x = max(self.div_factor_x, tile.x_pos)
            self.div_factor_y = max(self.div_factor_y, tile.y_pos)
        self.div_factor_x += 1
        self.div_factor_y += 1

        try:
            # Create an empty canvas for tiles
            self.base = self.generate_base(self.baseWidth, self.baseHeight)

            for tile in tiles:
                self.create_scaled_file(tile)

            for tile in tiles:
                self.create_overlay(tile)

            self.output_file = str(uuid.uuid1())+".mp4"
            self.base.output(self.output_file, t='15').overwrite_output().run()
        finally:
            # Clean up the temp files
            for tile in tiles:
                tile.delete_scaled_file()

    def delete_output_file(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            self.output_file = ""

    def generate_base(self, baseWidth, baseHeight):
        return ffmpeg.input(f'color=black:size={baseWidth}x{baseHeight}', f='lavfi')

    def create_scaled_file(self, tile):
        # Scales a video file based on the width and height input variables 
        # and outputs the specified resulting video file path. 
        new_path = str(uuid.uuid1()) + ".mp4"
        input_video = ffmpeg.input(tile.source)
        new_width, new_height = fix_odd(tile.width/self.div_factor_x, tile.height/self.div_factor_y)
        _ = (
            input_video
            .filter('scale', new_width, new_height)
            .output(new_path)
            .overwrite_output()
            .run()
        )
        tile.set_scaled_path(new_path)
        
    def create_overlay(self, tile):
        if tile.x_pos == 0 and tile.y_pos == 0:
            self.base = self.base.overlay(ffmpeg.input(tile.scaled_path))
        if tile.x_pos == 1 and tile.y_pos == 0:
            self.base = self.base.overlay(ffmpeg.input(tile.scaled_path), x=self.baseWidth/self.div_factor_x)
        if tile.x_pos == 0 and tile.y_pos == 1:
            self.base = self.base.overlay(ffmpeg.input(tile.scaled_path), y=self.baseHeight/self.div_factor_y)
        if tile.x_pos == 1 and tile.y_pos == 1:
            self.base = self.base.overlay(ffmpeg.input(tile.scaled_path), x=self.baseWidth/self.div_factor_x, y=self.baseHeight/self.div_factor_y)

# Test tiles
# tile1 = Tile("../../video/sample1.mp4", 0, 0, False)
# tile2 = Tile("../../video/sample1.mp4", 1, 0, False)
# tile3 = Tile("../../video/sample1.mp4", 0, 1, False)
# tile4 = Tile("../../video/sample1.mp4", 2, 0, False)

# list_tiles_1 = [tile1, tile2, tile3]
# list_tiles_2 = [tile1, tile2, tile4]

# sT = StreamTiler(list_tiles_1)