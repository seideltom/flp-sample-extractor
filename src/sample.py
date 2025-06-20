import os

class Sample:
    def __init__(self, path):
        self.path = path
        self.file_name = os.path.basename(path)
        self.extract = False

    def toggle_extract(self):
        self.extract = not self.extract