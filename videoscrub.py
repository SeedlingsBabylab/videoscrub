import os
import csv
import sys
import subprocess as sp


video_path = None
mask_path = None
timestamp_path = None
output_path = None

audio_regions = []
audio_frame_regions = None
video_regions = []
video_frame_regions = None

def scrub():
    global audio_regions
    global video_regions
    global audio_frame_regions
    global video_frame_regions

    with open(timestamp_path, "rU") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row[0] == "audio":
                audio_regions.append([int(row[1]), int(row[2])])
            elif row[0] == "video":
                video_regions.append([int(row[1]), int(row[2])])

    print "audio regions: " + str(audio_regions)
    print "video regions: " + str(video_regions)

    audio_frame_regions = ms_to_s(audio_regions)
    video_frame_regions = ms_to_s(video_regions)



    if video_path and timestamp_path and mask_path:
        # make sure there are regions to mask
        if audio_frame_regions:
            scrub_audio()
        if video_frame_regions:
            scrub_video()
    else:
        print "You need to load the video, mask and timestamp files before scrubbing"

def scrub_audio():

    print "scrubbing audio regions...."

    if_statements = build_audio_comparison_commands()

    # if there's only audio regions, output to final path
    # rather than the temp folder.
    if not video_frame_regions:
        command = ['ffmpeg',
                '-i',
                video_path,
                '-af',
                'volume=\'if({},0,1)\':eval=frame'.format(if_statements),
                '-c:a', "aac",
                '-strict', '-2',
                output_path
                ]
    else:
        command = ['ffmpeg',
                    '-i',
                    video_path,
                    '-af',
                    'volume=\'if({},0,1)\':eval=frame'.format(if_statements),
                    '-c:a', "aac",
                    '-strict', '-2',
                    "temp/audio_scrub_output.mp4"
                    ]

    command_string = ""

    for element in command:
        command_string += " " + element

    print "command: " + command_string

    pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
    pipe.communicate()  # blocks until the subprocess is complete

    print "command: " + str(command)

def scrub_video():

    between_statements = ""

    for index, region in enumerate(video_frame_regions):
        statement = "between(t,{},{})".format(region[0],region[1])
        if index == len(video_frame_regions) - 1:
            between_statements += statement
        else:
            between_statements += statement + "+"

    if not audio_frame_regions:

        command = ['ffmpeg',
                '-i',
                video_path,   # we're using the original input because there's no previous audio step
                '-i',
                mask_path,
                '-filter_complex',
                '\"[0:v][1:v] overlay=0:0:enable=\'{}\'\"'.format(between_statements),
                '-pix_fmt',
                'yuv420p',
                '-c:a',
                'copy',
                output_path]
    else:
        command = ['ffmpeg',
                    '-i',
                    'temp/audio_scrub_output.mp4',   # we're using the output from the audio scrub
                    '-i',
                    mask_path,
                    '-filter_complex',
                    '\"[0:v][1:v] overlay=0:0:enable=\'{}\'\"'.format(between_statements),
                    '-pix_fmt',
                    'yuv420p',
                    '-c:a',
                    'copy',
                    output_path]

    command_string = ""

    for element in command:
        command_string += " " + element

    print "command: " + command_string

    pipe = sp.Popen(command_string, stdout=sp.PIPE, bufsize=10**8, shell=True)
    pipe.communicate()  # blocks until the subprocess is complete

    if not audio_frame_regions:
        return
    else:
        os.remove("temp/audio_scrub_output.mp4")

def build_audio_comparison_commands():
    """
    This takes the audio regions (in frame onset/offset format)
    and builds a compounded list of if statements that will be
    part of the command that is piped to ffmpeg. They will end
    up in the form:

        gt(t,a_onset)*lt(t,a_offset)+gt(t,b_onset)*lt(t,b_offset)+gt(t,c_onset)*lt(t,c_offset)

    :return: compounded if statement
    """
    if_statments = ""

    for index, region in enumerate(audio_frame_regions):

        statement = "gt(t,{})*lt(t,{})".format(region[0],
                                                region[1])
        if index == len(audio_frame_regions) - 1:
            if_statments += statement
        else:
            if_statments += statement + "+"

    print if_statments
    return if_statments

def ms_to_s(timestamps):
    """
    Converts a list of timestamps, originally in milliseconds,
    to their corresponding second values, The input list should
    be a list of lists, for example:

            [[1000, 2200], [3000, 5500], [8000, 14000]]

    :param timestamps: list of millisecond onset/offsets
    :return: converted timestamps
    """
    results = []

    for region in timestamps:
        results.append([region[0]/1000, region[1]/1000])

    print "results: " + str(results)

    return results

def print_usage():
    print "USAGE: \n"
    print "$ python videoscrub.py input_video.mp4 censor_regions.csv mask_file.png output.mp4"

if __name__ == "__main__":

    if len(sys.argv) < 5:
        print_usage()
        sys.exit(0)

    video_path = sys.argv[1]
    timestamp_path = sys.argv[2]
    mask_path = sys.argv[3]
    output_path = sys.argv[4]

    scrub()