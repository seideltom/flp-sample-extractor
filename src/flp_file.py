import os
#import tkinter as tk
from src.sample import Sample
from src.file_utils import *

class FLPFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.text = convert_binary_file_to_text(file_path)
        self.existing_unique_paths = get_existing_unique_paths(self.text)
        self.samples = [Sample(path) for path in self.existing_unique_paths]


    def refresh_paths(self):

        # re-read the file to update the text
        self.text = convert_binary_file_to_text(self.file_path)

        # re-evaluate existing unique paths
        self.existing_unique_paths = get_existing_unique_paths(self.text)

        # remove samples that no longer exist
        self.samples = [sample for sample in self.samples if sample.path in self.existing_unique_paths]

        # add new samples with existing paths (probably useless but just in case)
        for path in self.existing_unique_paths:
            if path not in [s.path for s in self.samples]:
                self.samples.append(Sample(path))


    def extract_samples(self, destination_folder: str, callback=None):
        to_extract = [s for s in self.samples if os.path.exists(s.path) and s.extract]
        total = len(to_extract)
        extracted = 0

        for sample in to_extract:
            destination_path = get_unique_destination_path(destination_folder, sample.file_name)
            extracted += 1 # increment progress regardless of success

            try:
                with open(sample.path, 'rb') as src_file:
                    with open(destination_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())

            except Exception as e:
                print(f"Error while exporting {sample.path}: {e}")

            if callback:
                progress = float((extracted / total))
                callback(progress)

        return None

