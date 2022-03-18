import io
import os
from .package import Package


class FileSplitter(io.StringIO):
    def __init__(self, filespec=None, max_file_size=Package.MAX_DATA_SIZE, *args, **kwargs):
        self.max_file_size = max_file_size
        self.filespec = filespec
        self.files = []
        self.currentfile = None
        self.header = None
        self.counter = 0
        self.cycle_file()

    def cycle_file(self):
        if self.currentfile:
            self.currentfile.close()
        self.counter = 0
        fname = '{}_split{}'.format(self.filespec, len(self.files))
        self.currentfile = open(fname, 'w', encoding='utf-8')
        self.files.append(fname)
        if self.header:
            self.counter += self.currentfile.write('{}\n'.format(self.header))


    def file_list(self):
        self.currentfile.close()
        # Check for an empty dump
        if len(self.header) + 1 == self.counter:
            os.remove(self.files[-1])
            self.files = self.files[:-1]
        # If we only have one file, remove the suffix
        if len(self.files) == 1:
            filename = self.files.pop()
            new_filename = filename.replace('_split0', '')
            os.rename(filename, new_filename)
            self.files.append(new_filename)
        return self.files

    def write(self, s):
        if not self.header:
            self.header = s[: s.index('\n')]
        self.counter += self.currentfile.write(s)
        if self.counter >= self.max_file_size:
            self.cycle_file()
