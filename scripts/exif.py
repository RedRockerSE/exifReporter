import subprocess
import os
import json

class ExifTool(object):

    # sentinel = "{ready}\n"
    sentinel = "{ready}\r\n"

    def __init__(self, executable="bin/exiftool.exe"):
        self.executable = executable

    def __enter__(self):
        # self.process = subprocess.Popen(
        #     [self.executable, "-stay_open", "True",  "-@", "-"],
        #     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.process = subprocess.Popen(
         [self.executable, "-stay_open", "True",  "-@", "-"],
         universal_newlines=True,
         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def  __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.sentinel):
            # output += os.read(fd, 4096)
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.sentinel)]

    def get_metadata(self, *filenames):
        return json.loads(self.execute("-G", "-j", "-n", *filenames))