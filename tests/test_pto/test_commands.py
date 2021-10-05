from datetime import datetime
import pytest

from pto import commands as cm

def test_read_src_files():
    """
    GIVEN read_src_files with valid parameters src_path and list of extentions
    WHEN the execute method is called
    THEN a list of file names is returned
    """
    files =  cm.read_src_files("./tests/",[".img",".IMG"])
    assert files is not None

def test_create_date_path():
    """
    GIVEN create_date_path with valid properties dest_path and file_date
    WHEN the execute method is called
    THEN a valid file system structure must be created in the destination folder year/month/day eg. 2000/1/23
    """
    assert type(cm.create_date_path("./",datetime(2020, 5, 17)))== str

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
    files = cm.read_src_files("/media/urra/M32GBNEGRA/20181029 Bellas Artes Cuenta Conmigo/",[".jpg",".JPG"])
    assert cm.put_files_in_calendar("/media/urra/M32GBNEGRA/20181029 Bellas Artes Cuenta Conmigo/","/media/urra/PELICULAS Y ENTRETENIMIENTO/jpg_salva_calendar",files) == True

def test_split_folder_to_subfolders():
    """
    GIVEN split_folder_to_subfolders  with valid values src_files: str,dest_path : str,number_of_files : int
    WHEN the execute method is called
    THEN the content of the src_folder is splitted into subfolders containing the number_of_files gived
    """    
    files = cm.read_src_files("/home/urra/tests/",[".jpg"])
    assert cm.split_folder_to_subfolders(files,"/home/urra/tests/",1)

def test_split_folder():
    files = cm.read_src_files("/home/urra/tests/",[".jpg",".JPG",".jpeg",".JPEG"])
    cm.split_folder("/home/urra/tests/", files, 1)