import ffmpeg
import os
# --------------- OLD CODE --------------------
# ----- HARDCODED, USE IF ALL ELSE FAILS ------

testVideo = "../../video/sample1.mp4"
sample1 = "../../video/sample1.mp4"

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
    # vid_two_thirds = ffmpeg.input(generate_scaled_video(testVideo, "tmp.mp4", width=(width/3)*2-50, height=height-200))
    # vid_mini_third1 = ffmpeg.input(generate_scaled_video(player1, "tmp1.mp4", width=width/3, height=height/2-100))
    # vid_mini_third2 = ffmpeg.input(generate_scaled_video(player2, "tmp2.mp4", width=width/3, height=height/2-100))
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
# ffmpeg_overlay()