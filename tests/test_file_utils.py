import unittest
import os
from unittest.mock import mock_open, patch
from src.file_utils import convert_binary_file_to_text
from src.file_utils import get_existing_unique_paths
from src.file_utils import get_unique_destination_path


class TestConvertBinaryFileToText(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'\x00\x01\x02This is some text\x00with binary\x10data\x00')
    def test_realistic_binary(self, mock_file):
        file_path = 'dummy.bin'
        expected_text = '\x01\x02This is some textwith binary\x10data'
        result = convert_binary_file_to_text(file_path)
        self.assertEqual(result, expected_text)

    @patch('builtins.open', side_effect=Exception("File not found"))
    def test_error_handling(self, mock_file):
        file_path = 'not_exist.bin'
        expected_text = ''
        result = convert_binary_file_to_text(file_path)
        self.assertEqual(result, expected_text)


class TestGetExistingUniquePaths(unittest.TestCase):

    @patch('os.path.exists')
    def test_with_noise_and_various_paths(self, mock_exists):
        text = (
            "\x01\x02Some random text\x00\x01"
            "C:\\Music\\song1.mp3\x00\x01\x02"
            "random\x01junk\x02between\x00paths\x01"
            "/home/user/music/song2.wav\x01\x00\x02"
            "more\x01noise\x02"
            "C:\\Music\\song1.mp3"
            "/Users/test/music/song3.ogg"
            "/Users/test/m\x02usic/song3.ogg"
            "E:\\{Music\\_song2, 3.wav"
            "\x00\x01end of text\x02"
        )
        existing = {
            "C:\\Music\\song1.mp3",
            "E:\\{Music\\_song2, 3.wav",
            #"/home/user/music/song2.wav",
            #"/Users/test/music/song3.ogg"
        }
        mock_exists.side_effect = lambda p: p in existing

        result = get_existing_unique_paths(text)
        expected = list(existing)
        self.assertCountEqual(result, expected)

    @patch('os.path.exists')
    def test_empty_text(self, mock_exists):
        text = ""
        result = get_existing_unique_paths(text)
        self.assertEqual(result, [])

    @patch('os.path.exists')
    def test_no_valid_paths(self, mock_exists):
        text = "This is just some random text without any valid paths."
        result = get_existing_unique_paths(text)
        self.assertEqual(result, [])


class TestGetUniqueDestinationPath(unittest.TestCase):

    @patch('os.path.exists')
    def test_path_without_conflict(self, mock_exists):
        folder = "C:\\Users\\test\\output"
        filename = "song.mp3"

        mock_exists.return_value = False

        result = get_unique_destination_path(folder, filename)
        expected = os.path.join(folder, filename)
        self.assertEqual(result, expected)

    @patch('os.path.exists')
    def test_windows_path_conflict(self, mock_exists):
        folder = "C:\\Users\\test\\output"
        filename = "song.mp3"

        existing_files = {
            os.path.join(folder, "song.mp3"),
            os.path.join(folder, "song (1).mp3"),
        }

        mock_exists.side_effect = lambda p: p in existing_files

        result = get_unique_destination_path(folder, filename)
        expected = os.path.join(folder, "song (2).mp3")
        self.assertEqual(result, expected)

    @patch('os.path.exists')
    def test_unix_path_conflict(self, mock_exists):
        folder = "/Users/test/output"
        filename = "song.mp3"

        existing_files = {
            os.path.join(folder, "song.mp3"),
            os.path.join(folder, "song (1).mp3"),
        }

        mock_exists.side_effect = lambda p: p in existing_files

        result = get_unique_destination_path(folder, filename)
        expected = os.path.join(folder, "song (2).mp3")
        self.assertEqual(result, expected)

    @patch('os.path.exists')
    def test_multiple_dots_in_filename(self, mock_exists):
        folder = "C:\\Output"
        filename = "my.file.name.txt"

        existing_files = {
            os.path.join(folder, "my.file.name.txt"),
            os.path.join(folder, "my.file.name (1).txt"),
        }

        mock_exists.side_effect = lambda p: p in existing_files

        result = get_unique_destination_path(folder, filename)
        expected = os.path.join(folder, "my.file.name (2).txt")
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()