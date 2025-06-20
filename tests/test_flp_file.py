import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from src.flp_file import FLPFile


class TestFLPFile(unittest.TestCase):

    @patch('src.flp_file.Sample')
    @patch('src.flp_file.get_existing_unique_paths', return_value=["/some/path/sample1.wav", "/some/path/sample2.wav"])
    @patch('src.flp_file.convert_binary_file_to_text', return_value="dummy text")
    def test_init_populates_fields_correctly(self, mock_convert, mock_get_paths, mock_sample):
        flp = FLPFile("test.flp")

        mock_convert.assert_called_once_with("test.flp")
        mock_get_paths.assert_called_once_with("dummy text")
        self.assertEqual(flp.file_path, "test.flp")
        self.assertEqual(flp.file_name, "test.flp")
        self.assertEqual(flp.text, "dummy text")
        self.assertEqual(flp.existing_unique_paths, ["/some/path/sample1.wav", "/some/path/sample2.wav"])
        self.assertEqual(len(flp.samples), 2)
        mock_sample.assert_any_call("/some/path/sample1.wav")
        mock_sample.assert_any_call("/some/path/sample2.wav")

    @patch('src.flp_file.Sample')
    @patch('src.flp_file.get_existing_unique_paths', return_value=["path1", "path2"])
    @patch('src.flp_file.convert_binary_file_to_text', side_effect=["original text", "refreshed text"])
    def test_refresh_paths(self, mock_convert, mock_get_paths, mock_sample):

        s1 = MagicMock(path="path1")
        s2 = MagicMock(path="obsolete_path")
        mock_sample.side_effect = [s1, s2, MagicMock(path="path2")]

        flp = FLPFile("test.flp")
        flp.samples = [s1, s2]

        flp.refresh_paths()

        self.assertEqual(flp.text, "refreshed text")
        self.assertEqual(set(s.path for s in flp.samples), {"path1", "path2"})

    @patch('src.flp_file.open', new_callable=mock_open, read_data=b"data")
    @patch('src.flp_file.get_unique_destination_path')
    @patch('os.path.exists', return_value=True)
    @patch('src.flp_file.convert_binary_file_to_text', return_value="")
    @patch('src.flp_file.get_existing_unique_paths', return_value=[])
    def test_extract_samples_with_callback_and_successful_copy(
        self, mock_paths, mock_text, mock_exists, mock_get_dest, mock_file):

        mock_get_dest.side_effect = lambda folder, name: f"{folder}/{name}"
        sample1 = MagicMock(path="sample1.wav", file_name="sample1.wav", extract=True)
        sample2 = MagicMock(path="sample2.wav", file_name="sample2.wav", extract=True)

        flp = FLPFile("dummy.flp")
        flp.samples = [sample1, sample2]

        callback = MagicMock()

        flp.extract_samples("dest_folder", callback)

        # filters for progress calls which are float values
        progress_calls = [c for c in callback.mock_calls if c.args and isinstance(c.args[0], float)]
        self.assertEqual(callback.call_count, 2)

        expected_calls = [
            call("sample1.wav", 'rb'),
            call().__enter__().read(),
            call("dest_folder/sample1.wav", 'wb'),
            call().__enter__().write(b"data"),
        ]
        mock_file.assert_any_call("sample1.wav", 'rb')
        mock_file.assert_any_call("dest_folder/sample1.wav", 'wb')

    @patch('src.flp_file.open', new_callable=mock_open, read_data=b"data")
    @patch('src.flp_file.get_unique_destination_path')
    @patch('os.path.exists')
    @patch('src.flp_file.convert_binary_file_to_text', return_value="")
    @patch('src.flp_file.get_existing_unique_paths', return_value=[])
    def test_extract_samples_skips_non_extract_or_missing_paths(
        self, mock_paths, mock_text, mock_exists, mock_get_dest, mock_file):

        mock_exists.side_effect = lambda path: path == "sample1.wav"

        sample1 = MagicMock(path="sample1.wav", file_name="sample1.wav", extract=True)
        sample2 = MagicMock(path="sample2.wav", file_name="sample2.wav", extract=False)  # extract == False
        sample3 = MagicMock(path="missing.wav", file_name="missing.wav", extract=True)   # doesn't exist

        flp = FLPFile("dummy.flp")
        flp.samples = [sample1, sample2, sample3]

        flp.extract_samples("folder")

        mock_get_dest.assert_called_once_with("folder", "sample1.wav")
        self.assertEqual(mock_file.call_count, 2)  # one for reading, one for writing


if __name__ == "__main__":
    unittest.main()