from datetime import datetime
import os
import pytest
from pathlib import Path

from files4libs import commands as c


def test_read_src_files():
    """
    GIVEN read_src_files with valid parameters src_path and list of extentions
    WHEN the execute method is called
    THEN a list of file names is returned
    """
    files = c.read_src_files("/home/urra/projects/pto/tests/data/dated_images/2017", [".jpg", ".JPG"],"201710")
    for file in files:
        assert "201710" in file.stem and file.suffix == ".jpg"


def test_create_date_path():
    """
    GIVEN create_date_path with valid properties dest_path and file_date
    WHEN the execute method is called
    THEN a valid file system structure must be created in the destination folder year/month/day eg. 2000/1/23
    """
    assert type(c.create_date_path("./", datetime(2020, 5, 17))) == str


def test_is_pathname_valid():
    """
    GIVEN is_pathname_path  with a valid pathname
    WHEN the execute method is called
    THEN True if pathname is valid else False
    """
    assert c.is_pathname_valid("/home/urra/") == True


def test_split_folder_to_subfolders():
    #split_folder_to_subfolders(src_folder: str, dest_path: str, file_ext : list, number_of_files: int) -> bool:
    """
    GIVEN split_folder_to_subfolders  with valid values src_files: str,dest_path : str,number_of_files : int
    WHEN the execute method is called
    THEN the content of the src_folder is splitted into subfolders containing the number_of_files gived
    """
    assert c.split_folder_to_subfolders(
        "/home/urra/projects/pto/tests/data/dated_images/2017/10/10/", "/home/urra/tests/folders/",[".jpg"], 10) == True


def test_create_alphabet_folder():
    assert c.create_alphabet_folder("/home/urra/tests/") == True

def test_get_exif_data():
    exif_data = c.get_exif_data("/home/urra//projects/pto/tests/data/i6.jpg")
    assert exif_data.get("model") == None and exif_data.get("make") == None and exif_data.get("l") == None

def test_get_exif_date():
    exif_date = c.get_exif_date("/home/urra/projects/pto/tests/data/dated_images/2017/10/10/20171010_202743.jpg")
    print(exif_date)
    assert type(exif_date) == datetime

def test_get_exif_model():
    model = c.get_exif_attribute("/home/urra/projects/pto/tests/data/E31006098.JPG","model")
    assert model == 'E3100'

def test_get_exif_maker():
    maker = c.get_exif_attribute("/home/urra/projects/pto/tests/data/E31006098.JPG","make")
    assert maker == 'NIKON'

def test_get_exif_maker():
    datetime = c.get_exif_attribute("/home/urra/projects/pto/tests/data/E31006098.JPG","datetime")
    assert datetime == '2006:09:24 13:09:05'


def test_fetch_exif_models():
    """
    GIVEN a source path to images files and 
    WHEN the execute method is called
    THEN return a list of images files names that contains that model in the exif metadata
    """
    cameras = []
    files = c.read_src_files("/home/urra/projects/pto/tests/data/dated_images/")
    for file in files:
        model = c.get_exif_attribute(file,"model")
        if not model in cameras:
            cameras.append(model)
            print(cameras)
    return

def test_fetch_exif_images_by_model():
    """
    GIVEN a source path to images files, extensions and a valid camera model
    WHEN the method is called
    THEN return a list of images files names that has such model in the exif metadata
    """
    files = c.fetch_images_by_camera_model("/home/urra/projects/pto/tests/data/dated_images/", [".jpg", ".JPG"],"iPhone 4")
    for file in files:
        assert c.is_exif_model(file,"iPhone 4") == True


# def test_create_data_table():
    
#     src_path = "/home/urra/projects/pto/tests/data/"
#     dest_path = src_path
#     filename="test_excell_file.xlsx"
#     g = c.ImageExifOrganizer(src_path,dest_path,"test_excell_file.xlsx")
#     assert g.src_path == Path(src_path) and g.dest_path == Path(dest_path) and g.excell_filename == filename 
#     assert g.save_excell_file(filename)
