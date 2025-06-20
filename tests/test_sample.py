import unittest
import os
from src.sample import Sample

class TestSample(unittest.TestCase):

    def test_initialization_sets_attributes(self):
        sample = Sample("/some/path/to/audiofile.wav")
        self.assertEqual(sample.path, "/some/path/to/audiofile.wav")
        self.assertEqual(sample.file_name, "audiofile.wav")
        self.assertFalse(sample.extract)

    def test_toggle_extract_switches_state_true(self):
        sample = Sample("test.wav")
        self.assertFalse(sample.extract)
        sample.toggle_extract()
        self.assertTrue(sample.extract)

    def test_toggle_extract_switches_state_back_to_false(self):
        sample = Sample("test.wav")
        sample.toggle_extract()  # True
        sample.toggle_extract()  # False
        self.assertFalse(sample.extract)

    def test_file_name_extraction_with_different_paths(self):
        # Windows-style path
        windows_sample = Sample("C:\\Users\\Test\\sound.mp3")
        self.assertEqual(windows_sample.file_name, "sound.mp3")

        # Unix-style path
        unix_sample = Sample("/home/user/sound.mp3")
        self.assertEqual(unix_sample.file_name, "sound.mp3")



if __name__ == '__main__':
    unittest.main()