# FLP Sample Extractor by Tom Seidel
#
#
#
# Known Issues
# 1. The paths inside the FLP file are not always up to date, which can result in some files not being found. This can happen if 
#    the folder containing the samples has been moved or renamed frequently, so the paths might not be recognized correctly.
#    As a result, the program ignores these files. To fix this, you can open the FLP file in FL Studio, resave it, and then reload
#    it in the program. This will update the paths inside the FLP file and make them recognizable again.
# 2. Path search only works on Windows. For Unix/MacOS paths, the search becomes extremely slow, 
#    but it can be implemented easily by replacing the regex in file_utils.py with the commented-out pattern.
#    For testing purposes, there is also code available where the two commented-out paths simply need to be re-enabled.
# 3. Drag and Drop does not recognize shortcuts, only the original files. 
#    This is probably because the file type (".flp") is usually followed by a " - Shortcut" suffix.
# 4. Scrollbar design doesn't look great in some places, but cannot be disabled since laptops would otherwise be unable to scroll.
# 5. The FLPFile class also detects temporary files, which are not included in existing_paths. 
#    This is theoretically irrelevant but is mentioned here in case issues arise from it.


from src.gui import FLPSampleExtractor

if __name__ == "__main__":

    FLPSampleTracker = FLPSampleExtractor()
    FLPSampleTracker.mainloop()


