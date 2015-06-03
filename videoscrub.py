from Tkinter import *
import tkFileDialog


import os
import csv
import subprocess as sp


class MainWindow:

    def __init__(self, master):

        self.root = master                  # main GUI context
        self.root.title("videoscrub")       # title of window
        self.root.geometry("600x400")       # size of GUI window
        self.main_frame = Frame(root)       # main frame into which all the Gui components will be placed
        self.main_frame.pack()              # pack() basically sets up/inserts the element (turns it on)


        self.video_filepath = None
        self.timestamp_filepath = None

        self.video_file = None
        self.video_filename = None
        
        self.audio_regions = []
        self.audio_frame_regions = None
        self.video_regions = []
        self.video_frame_regions = None
        
        self.load_video_button = Button(self.main_frame,
                                        text="Load Video",
                                        command=self.load_video)

        self.load_timestamps_button = Button(self.main_frame,
                                       text="Load Timestamps",
                                       command=self.load_timestamps)

        self.clear_button = Button(self.main_frame,
                                   text="Clear",
                                   command=self.clear)

        self.scrub_button = Button(self.main_frame,
                                   text="Scrub",
                                   command=self.scrub)

        self.video_loaded_label = Label(self.main_frame, text="video loaded", fg="blue")
        self.timestamps_loaded_label = Label(self.main_frame, text="timestamps loaded", fg="red")

        self.load_video_button.grid(row=1, column=1)
        self.load_timestamps_button.grid(row=1, column=3)
        self.scrub_button.grid(row=2, column=2)
        self.clear_button.grid(row=3, column=2)


    def load_video(self):
        self.video_file = tkFileDialog.askopenfilename()
        self.video_filename = os.path.split(self.video_file)[1]

        print "path split 0" + str(os.path.split(self.video_file)[0])
        self.video_loaded_label.grid(row=3, column=1)

    def load_timestamps(self):

        self.timestamp_filepath = tkFileDialog.askopenfilename()

        self.timestamps_loaded_label.grid(row=3, column=3)

    def clear(self):

        self.video_file = None
        self.timestamp_filepath = None

        if self.video_loaded_label:
            self.video_loaded_label.grid_remove()
        if self.timestamps_loaded_label:
            self.timestamps_loaded_label.grid_remove()

    def scrub(self):
        print self.timestamp_filepath
        with open(self.timestamp_filepath, "rU") as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                if row[0] == "audio":
                    self.audio_regions.append([int(row[1]), int(row[2])])
                elif row[0] == "video":
                    self.video_regions.append([int(row[1]), int(row[2])])

        print "audio regions: " + str(self.audio_regions)
        print "video regions: " + str(self.video_regions)

        self.audio_frame_regions = self.ms_to_frames(self.audio_regions, 25)

        if self.video_file and self.timestamp_filepath:
            self.scrub_audio()
            self.scrub_video()
        else:
            print "You need to load both the video and timestamps file before scrubbing"

    def scrub_audio(self):

        print "scrubbing audio regions...."

        temp_files = []

        out = 'temp/temp_audio1.mp4'

        temp_files.append(out)

        for index, region in enumerate(self.audio_frame_regions):

            if index == 0:
                command = ['ffmpeg',
                            '-i',
                            self.video_file,
                            '-af',
                            'volume=volume=\'if(gt(n,{})*lt(n,{}),0,1)\':eval=frame'.format(region[0], region[1]),
                            '-c:a', "aac",
                            '-strict', '-2',
                            out
                           ]

                pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
                pipe.communicate()  # blocks until the subprocess is complete
                print "command " + str(index) + ": " + str(command)

            elif index != len(self.audio_frame_regions) - 1:
                temp = 'temp/temp_audio{}.mp4'.format(index)
                out = 'temp/temp_audio{}.mp4'.format(index + 1)

                temp_files.append(out)

                command = ['ffmpeg',
                            '-i',
                            temp,
                            '-af',
                            'volume=volume=\'if(gt(n,{})*lt(n,{}),0,1)\':eval=frame'.format(region[0], region[1]),
                            '-c:a', "aac",
                            '-strict', '-2',
                            out
                           ]

                pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
                pipe.communicate()  # blocks until the subprocess is complete
                print "command " + str(index) + ": " + str(command)

            elif index == len(self.audio_frame_regions) - 1:
                temp = 'temp/temp_audio{}.mp4'.format(index)
                out = 'data/final_out.mp4'

                command = ['ffmpeg',
                            '-i',
                            temp,
                            '-af',
                            'volume=volume=\'if(gt(n,{})*lt(n,{}),0,1)\':eval=frame'.format(region[0], region[1]),
                            '-c:a', "aac",
                            '-strict', '-2',
                            out
                           ]


                pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
                pipe.communicate()  # blocks until the subprocess is complete
                print "command " + str(index) + ": " + str(command)

        for temp in temp_files:     # delete all the temporary/intermediate files
            os.remove(temp)


    def scrub_video(self):
        print "lorem ipsum"

    def ms_to_frames(self, timestamps, fps):
        """
        Converts a list of timestamps, originally in milliseconds,
        to their corresponding frame values, depending on the framerate
        of the video being edited. The input list should be a list of lists,
        for example:

                [[1000, 2200], [3000, 5500], [8000, 14000]]

        :param timestamps: list of millisecond onset/offsets
        :param fps: framerate of the video being edited
        :return: converted timestamps
        """
        results = []

        for region in timestamps:
            results.append([region[0]/1000*fps, region[1]/1000*fps])

        print "results: " + str(results)

        return results

if __name__ == "__main__":

    root = Tk()
    MainWindow(root)
    root.mainloop()
