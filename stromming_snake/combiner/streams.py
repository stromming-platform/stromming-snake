import ffmpeg

filename = "../../video/sample1.mp4"

def ffmpeg_hflip():
    input = ffmpeg.input(filename)
    video = input.video.vflip()
    out = ffmpeg.output(video, 'out.mp4')
    out.run()


def get_video_dimensions(file):
    probe = ffmpeg.probe(file)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return width, height


def generate_scaled_video(output_path, width=-1, height=-1):
    input_video = ffmpeg.input(filename)
    _ = (
        input_video
        .filter('scale', x=width, y=height)
        .output(output_path)
        .overwrite_output()
        .run()
    )
    return output_path


def ffmpeg_overlay():
    # Get dimensions of video file
    width, height = get_video_dimensions(filename)

    # Use dimensions to create an empty source to place overlays on
    base = ffmpeg.input(f'nullsrc=size={width}x{height}', f='lavfi')

    # Scale down original video to fit into source
    vid_quarter = ffmpeg.input(generate_scaled_video("quarter.mp4", width=width/2, height=height/2))
    vid_half = ffmpeg.input(generate_scaled_video("half.mp4", width=width/2))

    # Create overlays
    base = (
        base.overlay(vid_half)
        .overlay(vid_quarter, x=width/2)
        .overlay(vid_quarter, x=width/2, y=height/2)
    )
    # base = base.overlay(vid_quarter, x=width/2)
    # base = base.overlay(vid_quarter, x=width/2, y=height/2)

    # Generate the final result
    base.output('combined.mp4').run()

ffmpeg_overlay()