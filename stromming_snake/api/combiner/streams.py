import ffmpeg
import os
import uuid

# TODO: Data class?

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


def fix_odd(x, y) -> tuple((int, int)):
    if x % 2 == 1:
        x = x + 1
    if y % 2 == 1:
        y = y + 1
    return x, y


# Paths to test video files
testVideo = "../../video/mainbroadcast.mp4"
player1 = "../../video/player1.mp4"
player2 = "../../video/player2.mp4"
sample1 = "../../video/sample1.mp4"

# Test tiles
tile1 = Tile("../../video/sample1.mp4", 0, 0, False)
tile2 = Tile("../../video/sample1.mp4", 1, 0, False)
tile3 = Tile("../../video/sample1.mp4", 0, 1, False)
tile4 = Tile("../../video/sample1.mp4", 2, 0, False)

list_tiles_1 = [tile1, tile2, tile3]
list_tiles_2 = [tile1, tile2, tile4]

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
            self.base.output(self.output_file, t='30').overwrite_output().run()
        finally:
            # Clean up the temp files
            for tile in tiles:
                tile.delete_scaled_file()

    def generate_base(self, baseWidth, baseHeight):
        return ffmpeg.input(f'color=black:size={baseWidth}x{baseHeight}', f='lavfi')

    def create_scaled_file(self, tile):
        # Scales a video file based on the width and height input variables 
        # and outputs the specified resulting video file path. 
        new_path = str(uuid.uuid1()) + ".mp4"
        input_video = ffmpeg.input(tile.source)
        _ = (
            input_video
            .filter('scale', tile.width/self.div_factor_x, tile.height/self.div_factor_y)
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
        # base = base.overlay(tile.scaled_path, x=self.baseWidth/self.div_factor_x)
        # base = base.overlay(tile.scaled_path, x=self.baseWidth/self.div_factor_x)
        # base = base.overlay(tile.scaled_path, x=self.baseWidth/self.div_factor_x)
        # base = (
        #     base.overlay(vid_half)
        #     .overlay(vid_quarter, x=width/2)
        #     .overlay(vid_quarter, x=width/2, y=height/2)
        # )

# --------------- OLD CODE --------------------
# ----- HARDCODED, USE IF ALL ELSE FAILS ------

def generate_scaled_video(input_file_path, output_path, width, height):
    # Scales a video file based on the width and height input variables 
    # and outputs the specified resulting video file path. 
    input_video = ffmpeg.input(input_file_path)
    _ = (
        input_video
        .filter('scale', width, height)
        .output(output_path)
        .overwrite_output()
        .run()
    )
    return output_path

def get_video_dimensions(source) -> None:
    # Takes a video file location and returns the dimensions of the source file
    probe = ffmpeg.probe(source)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return fix_odd(width, height)

def ffmpeg_overlay():
    output_filename = "triple.mp4"
    # Get dimensions of video file
    width, height = get_video_dimensions(testVideo)
    # width, height = 0

    # Use dimensions to create an empty source to place overlays on
    base = ffmpeg.input(f'color=black:size={width}x{height}', f='lavfi')

    # Scale down original video to fit into source
    vid_two_thirds = ffmpeg.input(generate_scaled_video(testVideo, "tmp.mp4", width=(width/3)*2-50, height=height-200))
    vid_mini_third1 = ffmpeg.input(generate_scaled_video(player1, "tmp1.mp4", width=width/3, height=height/2-100))
    vid_mini_third2 = ffmpeg.input(generate_scaled_video(player2, "tmp2.mp4", width=width/3, height=height/2-100))
    vid_quarter = ffmpeg.input(generate_scaled_video(sample1, "tmp3.mp4", width=width/2, height=height/2))
    vid_half = ffmpeg.input(generate_scaled_video(sample1, "tmp4.mp4", width=width/2, height=height))

    # Create overlays
    base = (
        base.overlay(vid_half)
        .overlay(vid_quarter, x=width/2)
        .overlay(vid_quarter, x=width/2, y=height/2)
    )
    # base = (
    #     base.overlay(vid_two_thirds, x=20, y=100)
    #     .overlay(vid_mini_third1, x=(width/3)*2-20, y=75)
    #     .overlay(vid_mini_third2, x=(width/3)*2-20, y=height/2+25)
    # )
    # base = base.overlay(vid_quarter, x=width/2)
    # base = base.overlay(vid_quarter, x=width/2, y=height/2)
    # base = base.overlay(vid_half)
    # base = base.overlay(vid_half, x=width/2)

    # Generate the final result
    base.output(output_filename, t='30').overwrite_output().run()

    if os.path.exists("tmp.mp4"):
        os.remove("tmp.mp4")
        os.remove("tmp1.mp4")
        os.remove("tmp2.mp4")
        os.remove("tmp3.mp4")
        os.remove("tmp4.mp4")
    else:
        print("No files to delete") 

# Some weird json someone suggested
example_object = {
    "tiles": [
        {
            "video1": {
                "source": "../../video/player1.mp4",
                "width": 500,
                "height": 250,
                "position": [0, 0],
                "audio": False
            },
            "video2": {
                "source": "../../video/sample1.mp4",
                "width": 200,
                "height": 150,
                "position": [1, 0],
                "audio": True
            },
            "video3": {
                "source": "../../video/player2.mp4",
                "width": 200,
                "height": 150,
                "position": [0, 1],
                "audio": False
            }
        }
    ]
}

# sT = StreamTiler(list_tiles_1)
# ffmpeg_overlay()