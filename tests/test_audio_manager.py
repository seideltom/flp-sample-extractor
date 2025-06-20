import unittest
from unittest.mock import patch, MagicMock
import pygame
from src.audio_manager import AudioManager

class TestAudioManager(unittest.TestCase):

    @patch('pygame.mixer.Sound')
    @patch('os.path.exists', return_value=True)
    def test_play_audio_loads_and_plays_new_audio(self, mock_exists, mock_sound):
        mock_channel = MagicMock()
        mock_sound_instance = MagicMock()
        mock_sound_instance.play.return_value = mock_channel
        mock_sound.return_value = mock_sound_instance

        manager = AudioManager()
        manager.play_audio("test.wav")

        mock_exists.assert_called_once_with("test.wav")
        mock_sound.assert_called_once_with("test.wav")
        mock_sound_instance.play.assert_called_once()
        self.assertEqual(manager.current_audio_path, "test.wav")
        self.assertEqual(manager.channel, mock_channel)

    @patch('pygame.mixer.Sound')
    @patch('os.path.exists', return_value=False)
    def test_play_audio_file_does_not_exist(self, mock_exists, mock_sound):
        manager = AudioManager()
        manager.play_audio("missing.wav")

        mock_exists.assert_called_once_with("missing.wav")
        mock_sound.assert_not_called()
        self.assertIsNone(manager.audio)
        self.assertIsNone(manager.channel)

    @patch('pygame.mixer.Sound', side_effect=pygame.error("load failed"))
    @patch('os.path.exists', return_value=True)
    def test_load_audio_failure(self, mock_exists, mock_sound):
        manager = AudioManager()
        manager.load_audio("corrupt.wav")

        mock_sound.assert_called_once_with("corrupt.wav")
        self.assertIsNone(manager.audio)
        self.assertIsNone(manager.channel)
        self.assertIsNone(manager.current_audio_path)

    def test_stop_audio_when_channel_is_busy(self):
        manager = AudioManager()
        mock_channel = MagicMock()
        mock_channel.get_busy.return_value = True
        manager.channel = mock_channel

        manager.stop_audio()
        mock_channel.get_busy.assert_called_once()
        mock_channel.stop.assert_called_once()

    def test_stop_audio_when_channel_is_not_busy(self):
        manager = AudioManager()
        mock_channel = MagicMock()
        mock_channel.get_busy.return_value = False
        manager.channel = mock_channel

        manager.stop_audio()
        mock_channel.get_busy.assert_called_once()
        mock_channel.stop.assert_not_called()

    def test_stop_audio_when_channel_is_none(self):
        manager = AudioManager()
        manager.channel = None
        # should not raise an error
        manager.stop_audio()


if __name__ == '__main__':
    unittest.main()
