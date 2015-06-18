#videoscrub

This script functions as a censor for our video files. It takes a csv file containing timestamps as input. This file is generated by the personalinfo.rb script found in our [datavyu scripts](https://github.com/SeedlingsBabylab/datavyu_scripts) repository. This program depends on [FFmpeg](https://www.ffmpeg.org/). Videoscrub expects the ffmpeg executable to be on your system PATH.


There are two versions of this script. One is a command line utility (videoscrub.py) and the other has a GUI (videoscrub-gui.py). They both have the same functionality. The good thing about the command line version is that it can be called from other processes programmatically.

###usage

#####for GUI

 1. Load video with "Load Video"
 1. Load video mask file with "Load Mask"
 1. Load timestamps with "Load Timestamps"
 1. Click "Scrub"
  * This will ask for a path to save to. Make sure to include the file extension (.mp4)

#####for CLI

The script must be called with 4 arguments:

1. input video
1. masking timestamps csv
1. video mask file
1. output file (remember to include .mp4 extension)


####region timstamps

personalinfo.rb, the script that generates the subregion timestamps csv, expects Datavyu personal info comments to be formatted as such:

%com: personal info [audio]: social security number

%com: personal info [video]: butt

The csv output will be of the form:

audio/video,onset_ms,offset_ms

for example:

audio,2000,3000  
audio,5000,7000  
audio,9000,13000  
video,1000,4000  
video,8000,12000


####video masking file

The script overlays a pure black image file onto the video stream to censor it. This file should be selected to correspond to the size of the video being masked. The black640x368.png file corresponds to the sample video (input.mp4) which is also found in the repository (data directory). Our own videos are 1280x720. When using our own recordings you need to select the black1280x720.png file found in the data directory.
