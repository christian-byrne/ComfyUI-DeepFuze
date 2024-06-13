import glob
import subprocess
import pytest

import deepfuze.globals
from deepfuze import process_manager
from deepfuze.filesystem import get_temp_directory_path, create_temp, clear_temp
from deepfuze.download import conditional_download
from deepfuze.ffmpeg import extract_frames, read_audio_buffer


@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
	process_manager.start()
	conditional_download('../../models/facefusion/examples',
	[
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.jpg',
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.mp3',
		'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-240p.mp4'
	])
	subprocess.run([ 'ffmpeg', '-i', '../../models/facefusion/examples/source.mp3', '../../models/facefusion/examples/source.wav' ])
	subprocess.run([ 'ffmpeg', '-i', '../../models/facefusion/examples/target-240p.mp4', '-vf', 'fps=25', '../../models/facefusion/examples/target-240p-25fps.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '../../models/facefusion/examples/target-240p.mp4', '-vf', 'fps=30', '../../models/facefusion/examples/target-240p-30fps.mp4' ])
	subprocess.run([ 'ffmpeg', '-i', '../../models/facefusion/examples/target-240p.mp4', '-vf', 'fps=60', '../../models/facefusion/examples/target-240p-60fps.mp4' ])


@pytest.fixture(scope = 'function', autouse = True)
def before_each() -> None:
	deepfuze.globals.trim_frame_start = None
	deepfuze.globals.trim_frame_end = None
	deepfuze.globals.temp_frame_format = 'jpg'


def test_extract_frames() -> None:
	target_paths =\
	[
		'../../models/facefusion/examples/target-240p-25fps.mp4',
		'../../models/facefusion/examples/target-240p-30fps.mp4',
		'../../models/facefusion/examples/target-240p-60fps.mp4'
	]

	for target_path in target_paths:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == 324

		clear_temp(target_path)


def test_extract_frames_with_trim_start() -> None:
	deepfuze.globals.trim_frame_start = 224
	data_provider =\
	[
		('../../models/facefusion/examples/target-240p-25fps.mp4', 55),
		('../../models/facefusion/examples/target-240p-30fps.mp4', 100),
		('../../models/facefusion/examples/target-240p-60fps.mp4', 212)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_extract_frames_with_trim_start_and_trim_end() -> None:
	deepfuze.globals.trim_frame_start = 124
	deepfuze.globals.trim_frame_end = 224
	data_provider =\
	[
		('../../models/facefusion/examples/target-240p-25fps.mp4', 120),
		('../../models/facefusion/examples/target-240p-30fps.mp4', 100),
		('../../models/facefusion/examples/target-240p-60fps.mp4', 50)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '452x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_extract_frames_with_trim_end() -> None:
	deepfuze.globals.trim_frame_end = 100
	data_provider =\
	[
		('../../models/facefusion/examples/target-240p-25fps.mp4', 120),
		('../../models/facefusion/examples/target-240p-30fps.mp4', 100),
		('../../models/facefusion/examples/target-240p-60fps.mp4', 50)
	]

	for target_path, frame_total in data_provider:
		temp_directory_path = get_temp_directory_path(target_path)
		create_temp(target_path)

		assert extract_frames(target_path, '426x240', 30.0) is True
		assert len(glob.glob1(temp_directory_path, '*.jpg')) == frame_total

		clear_temp(target_path)


def test_read_audio_buffer() -> None:
	assert isinstance(read_audio_buffer('../../models/facefusion/examples/source.mp3', 1, 1), bytes)
	assert isinstance(read_audio_buffer('../../models/facefusion/examples/source.wav', 1, 1), bytes)
	assert read_audio_buffer('../../models/facefusion/examples/invalid.mp3', 1, 1) is None
