import subprocess as sp
import os
import sys


def print_usage():
    print "USAGE: \n"
    print "$ python videoscrub.py input_video_folder censor_regions_folder mask_file.png output_folder"


if __name__ == "__main__":

    if len(sys.argv) < 5:
        print_usage()
        sys.exit(0)

    video_folder_path = sys.argv[1]
    timestamp_folder_path = sys.argv[2]
    mask_path = sys.argv[3]
    output_folder_path = sys.argv[4]

    for timef in os.listdir(timestamp_folder_path):
        if "_personal_info.csv" not in timef:
            continue
        date = timef[0:5]
        for videof in os.listdir(video_folder_path):
            if "_video.mp4" not in videof:
                continue
            if videof[0:5] == date:
                outputf = date + "_video_scrubbed.mp4"
                outputf = os.path.join(output_folder_path, outputf)
                videof = os.path.join(video_folder_path, videof)
                timef = os.path.join(timestamp_folder_path, timef)
                sp.call(["python", "videoscrub.py",
                         videof, timef, mask_path, outputf])
