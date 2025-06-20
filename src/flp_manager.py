from pathlib import Path
from src.flp_file import FLPFile
from src.sample import Sample

class FLPManager:
    def __init__(self):
        self.flp_objects = {}

    def add_candidates(self, paths):

        valid_flps = []
        already_existing_flps = []

        for p in paths:

            path = Path(p)

            if path.is_file() and path.suffix == '.flp':
                valid_path = str(path.resolve())

                if valid_path in self.flp_objects:
                    flp = self.flp_objects[valid_path]
                    flp.refresh_paths()
                    already_existing_flps.append(flp)
                    continue
                
                flp_object = FLPFile(valid_path)
                valid_flps.append(flp_object)
                self.flp_objects[valid_path] = flp_object

            elif path.is_dir():
                for flp_path in path.rglob('*.flp'):
                    valid_path = str(flp_path.resolve())

                    if valid_path in self.flp_objects:
                        flp = self.flp_objects[valid_path]
                        flp.refresh_paths()
                        already_existing_flps.append(flp)
                        continue

                    flp_object = FLPFile(valid_path)
                    valid_flps.append(flp_object)
                    self.flp_objects[valid_path] = flp_object


        return valid_flps, already_existing_flps