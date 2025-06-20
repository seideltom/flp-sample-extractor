import unittest
import tempfile
import shutil
from pathlib import Path
from src.flp_manager import FLPManager
from unittest.mock import patch, MagicMock
from src.flp_file import FLPFile

class TestFLPManagerBasicCases(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_flp_file(self, name, subfolder=None):
        dir_path = Path(self.test_dir)
        if subfolder:
            dir_path = dir_path / subfolder
            dir_path.mkdir(exist_ok=True)
        file_path = dir_path / name
        file_path.touch()
        return str(file_path.resolve())

    @patch("src.flp_manager.FLPFile")
    def test_single_new_flp_file(self, MockFLPFile):
        path = self.create_flp_file("single.flp")
        mock_flp = MagicMock()
        mock_flp.file_path = path
        MockFLPFile.return_value = mock_flp

        manager = FLPManager()
        valid, existing = manager.add_candidates([path])

        self.assertEqual([f.file_path for f in valid], [path])
        self.assertEqual(existing, [])

    @patch("src.flp_manager.FLPFile")
    def test_single_existing_flp_file(self, MockFLPFile):
        path = self.create_flp_file("existing.flp")
        mock_flp = MagicMock()
        mock_flp.file_path = path
        manager = FLPManager()
        manager.flp_objects[path] = mock_flp

        valid, existing = manager.add_candidates([path])

        self.assertEqual(valid, [])
        self.assertEqual([f.file_path for f in existing], [path])
        mock_flp.refresh_paths.assert_called_once()

    @patch("src.flp_manager.FLPFile")
    def test_folder_with_two_new_flps(self, MockFLPFile):
        f1 = self.create_flp_file("new1.flp", subfolder="folder")
        f2 = self.create_flp_file("new2.flp", subfolder="folder")
        folder_path = str(Path(f1).parent)

        mock1 = MagicMock()
        mock1.file_path = f1
        mock2 = MagicMock()
        mock2.file_path = f2

        MockFLPFile.side_effect = [mock1, mock2]

        manager = FLPManager()
        valid, existing = manager.add_candidates([folder_path])

        self.assertCountEqual([f.file_path for f in valid], [f1, f2])
        self.assertEqual(existing, [])

    @patch("src.flp_manager.FLPFile")
    def test_folder_with_new_and_existing_flp(self, MockFLPFile):
        f1 = self.create_flp_file("new.flp", subfolder="folder")
        f2 = self.create_flp_file("old.flp", subfolder="folder")
        folder_path = str(Path(f1).parent)

        # Setup: old.flp is already loaded
        mock_old = MagicMock()
        mock_old.file_path = f2

        mock_new = MagicMock()
        mock_new.file_path = f1

        MockFLPFile.side_effect = [mock_new]

        manager = FLPManager()
        manager.flp_objects[f2] = mock_old

        valid, existing = manager.add_candidates([folder_path])

        self.assertEqual([f.file_path for f in valid], [f1])
        self.assertEqual([f.file_path for f in existing], [f2])
        mock_old.refresh_paths.assert_called_once()

    @patch("src.flp_manager.FLPFile")
    def test_folder_with_two_existing_flps(self, MockFLPFile):
        f1 = self.create_flp_file("old1.flp", subfolder="folder")
        f2 = self.create_flp_file("old2.flp", subfolder="folder")
        folder_path = str(Path(f1).parent)

        mock1 = MagicMock()
        mock1.file_path = f1
        mock2 = MagicMock()
        mock2.file_path = f2

        manager = FLPManager()
        manager.flp_objects[f1] = mock1
        manager.flp_objects[f2] = mock2

        valid, existing = manager.add_candidates([folder_path])

        self.assertEqual(valid, [])
        self.assertCountEqual([f.file_path for f in existing], [f1, f2])
        mock1.refresh_paths.assert_called_once()
        mock2.refresh_paths.assert_called_once()


class TestFLPManagerExtremeCase(unittest.TestCase):
    def setUp(self):
        # Temporäres Testverzeichnis
        self.test_dir = tempfile.mkdtemp()

        # Structure
        # ├── new.flp
        # ├── notes.txt
        # └── samples/
        #     ├── new2.flp
        #     ├── old1.flp
        #     ├── readme.txt
        #     └── sub/
        #         ├── new3.flp
        #         └── old2.flp

        Path(self.test_dir, "new.flp").touch()
        Path(self.test_dir, "notes.txt").touch()

        samples_dir = Path(self.test_dir, "samples")
        samples_dir.mkdir()

        (samples_dir / "new2.flp").touch()
        (samples_dir / "old1.flp").touch()
        (samples_dir / "readme.txt").touch()

        sub_dir = samples_dir / "sub"
        sub_dir.mkdir()

        (sub_dir / "new3.flp").touch()
        (sub_dir / "old2.flp").touch()

        # Save paths for reuse
        self.paths = {
            "new1": str(Path(self.test_dir, "new.flp").resolve()),
            "old1": str((samples_dir / "old1.flp").resolve()),
            "old2": str((sub_dir / "old2.flp").resolve()),
            "new2": str((samples_dir / "new2.flp").resolve()),
            "new3": str((sub_dir / "new3.flp").resolve()),
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('src.flp_manager.FLPFile')
    def test_mixed_input(self, MockFLPFile):
        # Mock FLPFile object so we can check instances
        def mock_constructor(path):
            mock_instance = MagicMock(spec=FLPFile)
            mock_instance.file_path = path
            mock_instance.file_name = Path(path).name
            return mock_instance

        MockFLPFile.side_effect = mock_constructor

        manager = FLPManager()

        # prepare mock FLPFile objects for old files
        old1_obj = MockFLPFile(self.paths["old1"])
        old2_obj = MockFLPFile(self.paths["old2"])
        manager.flp_objects[self.paths["old1"]] = old1_obj
        manager.flp_objects[self.paths["old2"]] = old2_obj

        input_paths = [
            self.paths["new1"],
            str(Path(self.test_dir, "notes.txt")),
            str(Path(self.test_dir, "samples")),
        ]

        valid_flps, already_loaded_flps = manager.add_candidates(input_paths)

        valid_paths = sorted([f.file_path for f in valid_flps])
        existing_paths = sorted([f.file_path for f in already_loaded_flps])

        expected_valid = sorted([self.paths["new1"], self.paths["new2"], self.paths["new3"]])
        expected_existing = sorted([self.paths["old1"], self.paths["old2"]])

        self.assertEqual(valid_paths, expected_valid)
        self.assertEqual(existing_paths, expected_existing)








if __name__ == '__main__':
    unittest.main()
