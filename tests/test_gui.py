import unittest
from unittest.mock import patch, MagicMock
from src.gui import FLPSampleExtractor
import tkinter as tk

class TestFLPSampleExtractor(unittest.TestCase):
    @patch.object(FLPSampleExtractor, 'load_icons')  # blocks load_icons from being called
    def setUp(self, mock_load_icons):
        self.app = FLPSampleExtractor()

        self.app.destination_area_entry = MagicMock()
        self.app.destination_area_entry.delete = MagicMock()
        self.app.destination_area_entry.insert = MagicMock()

    @patch('customtkinter.filedialog.askdirectory')
    def test_add_destination_folder_valid_path(self, mock_askdirectory):
        mock_askdirectory.return_value = "/fake/path"

        self.app.add_destination_folder()

        self.app.destination_area_entry.delete.assert_called_once_with(0, "end")
        self.app.destination_area_entry.insert.assert_called_once_with(0, "/fake/path")
        self.assertEqual(self.app.destination_folder, "/fake/path")

    @patch('customtkinter.filedialog.askdirectory')
    def test_add_destination_folder_cancelled(self, mock_askdirectory):
        mock_askdirectory.return_value = ""

        self.app.add_destination_folder()

        self.app.destination_area_entry.delete.assert_not_called()
        self.app.destination_area_entry.insert.assert_not_called()
        self.assertIsNone(self.app.destination_folder)

