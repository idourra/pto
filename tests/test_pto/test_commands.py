from datetime import datetime
import os
import pytest

from pto import commands as cm


def test_read_src_files():
    """
    GIVEN read_src_files with valid parameters src_path and list of extentions
    WHEN the execute method is called
    THEN a list of file names is returned
    """
    files = cm.read_src_files("/home/urra/tests/data/", [".img", ".IMG"],"2017")
    assert type(files) == list 


def test_create_date_path():
    """
    GIVEN create_date_path with valid properties dest_path and file_date
    WHEN the execute method is called
    THEN a valid file system structure must be created in the destination folder year/month/day eg. 2000/1/23
    """
    assert type(cm.create_date_path("./", datetime(2020, 5, 17))) == str


def test_is_pathname_valid():
    """
    GIVEN is_pathname_path  with a valid pathname
    WHEN the execute method is called
    THEN True if pathname is valid else False
    """
    assert cm.is_pathname_valid("/home/urra") == True


def test_put_files_in_calendar():
    """
    GIVEN put_files_in_calendar  with valid values src_path: str,dest_path: str, files: list
    WHEN the execute method is called
    THEN return none_dated_files, init_time, end_time
    """
    files = cm.read_src_files(
        "/home/urra/projects/pto/tests/data/dated_images/", [".jpg", ".JPG"])
    assert cm.put_files_in_calendar("/home/urra/projects/pto/tests/data/dated_images/",
                                    "/home/urra/tests/folders/calendar/", files) == True


def test_split_folder_to_subfolders():
    #split_folder_to_subfolders(src_folder: str, dest_path: str, file_ext : list, number_of_files: int) -> bool:
    """
    GIVEN split_folder_to_subfolders  with valid values src_files: str,dest_path : str,number_of_files : int
    WHEN the execute method is called
    THEN the content of the src_folder is splitted into subfolders containing the number_of_files gived
    """
    assert cm.split_folder_to_subfolders(
        "/home/urra/projects/pto/tests/data/dated_images/2017/10/10/", "/home/urra/tests/folders/",[".jpg"], 10) == True


def test_create_alphabet_folder():
    assert cm.create_alphabet_folder("/home/urra/tests/") == True

def test_extract_exif_date():
    exif_date = cm.extract_exif_date("/home/urra/projects/pto/tests/data/dated_images/2017/10/10/20171010_202743.jpg")
    print(exif_date)
    assert type(exif_date) == datetime

def test_extract_exif_make_model():
    exif_data = cm.extract_exif_data('/home/urra/Pictures/jpg_camaras_salva/nikon_e3100_amalio/E31006115.JPG')
    make_model = cm.extract_exif_make_model(exif_data)
    assert make_model == 'NIKON-E3100'
