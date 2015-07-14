from Tkinter import *
import tkFileDialog

import os
import csv
import subprocess as sp


class MainWindow:

    def __init__(self, master):

        self.root = master                  # main GUI context
        self.root.title("videoscrub")       # title of window
        self.root.geometry("600x300")       # size of GUI window
        self.main_frame = Frame(root)       # main frame into which all the Gui components will be placed
        self.main_frame.pack()              # pack() basically sets up/inserts the element (turns it on)


        self.video_path = None
        self.mask_path = None
        self.timestamp_path = None
        self.output_path = None

        self.video_file = None
        self.video_filename = None
        
        self.audio_regions = []
        self.audio_frame_regions = None
        self.video_regions = []
        self.video_frame_regions = None
        
        self.load_video_button = Button(self.main_frame,
                                        text="Load Video",
                                        command=self.load_video)

        self.load_videomask_button = Button(self.main_frame,
                                            text="Load Mask",
                                            command=self.load_mask)

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
        self.mask_loaded_label = Label(self.main_frame, text="mask loaded", fg="black")
        self.timestamps_loaded_label = Label(self.main_frame, text="timestamps loaded", fg="red")

        self.load_video_button.grid(row=1, column=1)
        self.load_videomask_button.grid(row=1, column=4)
        self.load_timestamps_button.grid(row=1, column=3)
        self.scrub_button.grid(row=2, column=2)
        self.clear_button.grid(row=3, column=2)


    def load_video(self):
        self.video_file = tkFileDialog.askopenfilename()
        self.video_filename = os.path.split(self.video_file)[1]

        print "path split 0" + str(os.path.split(self.video_file)[0])
        self.video_loaded_label.grid(row=3, column=1)

    def load_mask(self):
        self.mask_path = tkFileDialog.askopenfilename()
        self.mask_loaded_label.grid(row=3, column=4)

    def load_timestamps(self):

        self.timestamp_path = tkFileDialog.askopenfilename()
        self.timestamps_loaded_label.grid(row=3, column=3)

    def clear(self):
        # currently, the "clear" button leaves the mask
        # filepath in place rather than clearing it, so you
        # can reuse it for the next video you want to process

        self.video_file = None
        self.timestamp_path = None


        if self.video_loaded_label:
            self.video_loaded_label.grid_remove()
        if self.timestamps_loaded_label:
            self.timestamps_loaded_label.grid_remove()

    def scrub(self):
        print self.timestamp_path

        self.output_path = tkFileDialog.asksaveasfilename()

        with open(self.timestamp_path, "rU") as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                if row[0] == "audio":
                    self.audio_regions.append([int(row[1]), int(row[2])])
                elif row[0] == "video":
                    self.video_regions.append([int(row[1]), int(row[2])])

        print "audio regions: " + str(self.audio_regions)
        print "video regions: " + str(self.video_regions)

        self.audio_frame_regions = self.ms_to_s(self.audio_regions)
        self.video_frame_regions = self.ms_to_s(self.video_regions)

        if self.video_file and self.timestamp_path and self.mask_path:
            if self.audio_frame_regions:
                self.scrub_audio()
            if self.video_frame_regions:
                self.scrub_video()
        else:
            print "You need to load the video, mask and timestamp files before scrubbing"

    def scrub_audio(self):

        print "scrubbing audio regions...."

        if_statements = self.build_audio_comparison_commands()


        # if there's only audio regions, output to final path
        # rather than the temp folder.
        if not self.video_frame_regions:
            command = ['ffmpeg',
                   '-i',
                   self.video_file,
                   '-af',
                   'volume=\'if({},0,1)\':eval=frame'.format(if_statements),
                   '-c:a', "aac",
                   '-strict', '-2',
                   self.output_path
                   ]
        else:
            command = ['ffmpeg',
                       '-i',
                       self.video_file,
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

    def scrub_video(self):

        between_statements = ""

        for index, region in enumerate(self.video_frame_regions):
            statement = "between(t,{},{})".format(region[0],region[1])
            if index == len(self.video_frame_regions) - 1:
                between_statements += statement
            else:
                between_statements += statement + "+"

        if not self.audio_frame_regions:
            command = ['ffmpeg',
                       '-i',
                       self.video_file,   # using original video
                       '-i',
                       self.mask_path,
                       '-filter_complex',
                       '\"[0:v][1:v] overlay=0:0:enable=\'{}\'\"'.format(between_statements),
                       '-pix_fmt',
                       'yuv420p',
                       '-c:a',
                       'copy',
                       self.output_path]
        else:
            command = ['ffmpeg',
                       '-i',
                       "temp/audio_scrub_output.mp4",   # we're using the output from the audio scrub
                       '-i',
                       self.mask_path,
                       '-filter_complex',
                       '\"[0:v][1:v] overlay=0:0:enable=\'{}\'\"'.format(between_statements),
                       '-pix_fmt',
                       'yuv420p',
                       '-c:a',
                       'copy',
                       self.output_path]

        command_string = ""

        for element in command:
            command_string += " " + element

        print "command: " + command_string

        pipe = sp.Popen(command_string, stdout=sp.PIPE, bufsize=10**8, shell=True)
        pipe.communicate()  # blocks until the subprocess is complete

        if not self.audio_frame_regions:
            return
        else:
            os.remove("temp/audio_scrub_output.mp4")

    def build_audio_comparison_commands(self):
        """
        This takes the audio regions (in frame onset/offset format)
        and builds a compounded list of if statements that will be
        part of the command that is piped to ffmpeg. They will end
        up in the form:

            gt(t,a_onset)*lt(t,a_offset)+gt(t,b_onset)*lt(t,b_offset)+gt(t,c_onset)*lt(t,c_offset)

        :return: compounded if statement
        """
        if_statments = ""

        for index, region in enumerate(self.audio_frame_regions):

            statement = "gt(t,{})*lt(t,{})".format(region[0],
                                                   region[1])
            if index == len(self.audio_frame_regions) - 1:
                if_statments += statement
            else:
                if_statments += statement + "+"

        print if_statments
        return if_statments


    def ms_to_s(self, timestamps):
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

if __name__ == "__main__":

    root = Tk()
    MainWindow(root)
    root.mainloop()
