#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python package to organize images using the exif date data in a file system structure YYYY/MM/DD
the three fists methods come from https://github.com/Zenith00/utils
"""

from datetime import datetime
import errno
import os
import time
import pathlib
import shutil
import sys
import json
import numpy
import pandas as pd
from exif import Image, DATETIME_STR_FORMAT

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123


def is_pathname_valid(pathname: str) -> bool:
    '''
    'True' if the passed pathname is a valid pathname for the current OS;
    'False' otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., 'C:\')
        # if any. Since Windows prohibits path components from containing ':'
        # characters, failing to strip this ':'-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


def is_path_creatable(pathname: str) -> bool:
    '''
    'True' if the current user has sufficient permissions to create the passed
    pathname; 'False' otherwise.
    '''
    # Parent directory of the passed path. If empty, we substitute the current
    # working directory (CWD) instead.
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)


def is_path_exists_or_creatable(pathname: str) -> bool:
    '''
    'True' if the passed pathname is a valid pathname for the current OS _and_
    either currently exists or is hypothetically creatable; 'False' otherwise.

    This function is guaranteed to _never_ raise exceptions.
    '''
    try:
        # To prevent "os" module calls from raising undesirable exceptions on
        # invalid pathnames, is_pathname_valid() is explicitly called first.
        return is_pathname_valid(pathname) and (
            os.path.exists(pathname) or is_path_creatable(pathname))
    # Report failure on non-fatal filesystem complaints (e.g., connection
    # timeouts, permissions issues) implying this path to be inaccessible. All
    # other exceptions are unrelated fatal issues and should not be caught here.
    except OSError:
        return False

def read_src_files(src_path: str, extensions = [".jpg",".jpeg"], keyword = "") -> list:
    # returns a list with all files with the extension contained in the variable extensions
    sys.setrecursionlimit(4000)
    try:
        files = {p.resolve() for p in pathlib.Path(src_path).glob("**/*") if p.suffix.lower() in extensions and keyword.lower() in p.stem.lower()} 
        # sort files by name
        files = sorted(files)
        #print(f'{str(len(files))} files in {src_path} path tree with extensions {extensions}')
        sys.setrecursionlimit(1000)
        return files
    except(Exception) as error:
        print(error)
        sys.setrecursionlimit(1000)
        return []

def create_date_path(dest_path: str, file_date: str) -> str:

    year_path = os.path.join(dest_path, str(file_date.year))
    month_path = os.path.join(year_path, str(file_date.month))
    day_path = os.path.join(month_path, str(file_date.day))
    try:
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
            print(dest_path)
        if not os.path.exists(year_path):
            os.makedirs(year_path)
            print(year_path)
        if not os.path.exists(month_path):
            os.makedirs(month_path)
            print(month_path)
        if not os.path.exists(day_path):
            os.makedirs(day_path)
            print(day_path)
        return day_path
    except(Exception) as error:
        print(error)
        return None

def create_alphabet_folder(dest_path: str, iso_language = "en") -> bool:
    if iso_language == "es":
        alphabet = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
    elif iso_language == "en":
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    else:
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    # create the base destination directory
    if not os.path.exists(dest_path):
        try:
            os.makedirs(dest_path)
        except(Exception) as error:
            print(error)
            return False
    
    for letter in alphabet:
        if not os.path.exists(os.path.join(dest_path, letter)):
            # create folder
            try:
                os.makedirs(os.path.join(dest_path, letter))
            except(Exception) as error:
                print(error)
                return False
    return True

def split_folder_to_subfolders(src_folder: str, dest_path: str, file_exts : list, number_of_files: int) -> bool:
    try:
        src_files = read_src_files(src_folder,file_exts)
    except(Exception) as error:
        print(error)
        return False
    src_files = sorted(src_files)
    # calculate the number of folders to create in relation with the total of files
    if len(src_files) % number_of_files > 0:
        number_of_folders = int(len(src_files)/number_of_files) + 1
    else:
        number_of_folders = int(len(src_files)/number_of_files)

    print(
        f"number of files:{number_of_files}, number of folders {number_of_folders}")

    # split the list of file names in the number of folders projected
    virtual_folders = numpy.array_split(src_files, number_of_folders)

    # create the folders in the file system and populate every folder with files gived the number_of_files per folder
    for count, virtual_folder in enumerate(virtual_folders):
        new_path = os.path.join(dest_path, str(
            count).zfill(len(str(number_of_folders))))
        if not os.path.isdir(new_path):
            try:
                os.makedirs(new_path)
                print(new_path)
            except(Exception) as error:
                print(error)
                return False
            print(new_path + " created")
        else:
            print(new_path + " exists")
        for file in virtual_folder:
            try:
                shutil.copy(file, new_path)
                print(f'{file} copied to {new_path}')
            except(Exception) as error:
                print(error)
                return False
    return True
        
def cronofiles(paths: list, dest_path: str, extensions = [".jpg",".jpeg"]) ->bool:
    # creates a cronological copy of the images in the file system of type YYY/MM/DD
    # from a list of files names checks every image and using the exif metadata
    # copy the file to the file system in a structure representing a calendar
    # if the image file does not have a date, the image file is located in a none_exif_date folder
    for src_path in paths:
        try:
            files = read_src_files(src_path,extensions)
        except(Exception) as error:
            print(error)
            return False
        non_dated_files = []
        for file in files:
            image_date = get_exif_attribute(file,"date")
            if image_date:
                try:
                    shutil.copy2(file, create_date_path(dest_path, image_date))
                except(Exception) as error:
                    print(error)
            else:
                non_dated_files.append(file)
                ndf_path = pathlib.Path(dest_path / "non_dated_files")
                try:
                    ndf_path.mkdir(parents= True, exist_ok=True )
                except(Exception) as error:
                    print(error)
                try:
                    shutil.copy2(file, ndf_path)
                except(Exception) as error:
                    print(error)    
        
    return True
      

    # from a list of file names in a path, checks every image and using the exif metadata
    # copy the file to the file system in a structure representing a calendar
    # if the image file does not have a date, the image file is located in a none_exif_date folder
    # for eg. /2021/10/1/ etc
    none_dated_files = []
    for file in files:
        #src_file_path = os.path.join(src_path, file)
        src_file_path = pathlib.Path(src_path, file)
        if os.path.isfile(src_file_path) and ".jpg" in src_file_path.lower():
            image_date = get_exif_date(src_file_path)
            if image_date:
                file_path = create_date_path(dest_path, image_date)
                try:
                    shutil.copy2(src_file_path, file_path)
                    print(os.path.join(file_path, file))
                except(Exception) as error:
                    print(error)
            else:
                print("none image date data")
                none_dated_files.append(file)
                file_path = os.path.join(dest_path, "none_exif_date")
                if not os.path.isdir(file_path):
                    try:
                        os.makedirs(file_path)
                    except(Exception) as error:
                        print(error)
                try:
                    shutil.copy2(src_file_path, file_path)
                    print(os.path.join(file_path, file))
                except(Exception) as error:
                    print(error)
    return True

def move_files_to_dest(src_path: str, dest_path:str, extensions = [".jpg",".jpeg"], keyword = "") -> bool:
    files = read_src_files(src_path, extensions, keyword)
    dest_path = pathlib.Path(dest_path)
    try:
        pathlib.Path(dest_path).mkdir(parents=True,exist_ok=True)
        for file in files:
            try:
                shutil.move(file,dest_path)
            except(Exception) as error:
                print(error)     
    except(Exception) as error:
        print(error)
        return

def get_exif_date(filename) -> str:
    try:
        with open(filename, "rb") as image_file:
            image = Image(image_file)
            if image.has_exif:
                if image.datetime_original:
                    image_date_data = image.datetime_original
                elif image.datetime_digitized:
                    image_date_data = image.datetime_digitized
                elif image.datetime:
                    image_date_data = image.datetime
                else:
                    image_date_data = "0000:00:00 00:00:00"
                if "-" in image_date_data:
                    image_date_data = image_date_data.replace("-", ":")

                return datetime.strptime(image_date_data, '%Y:%m:%d %H:%M:%S')
            else:
                print("does not contain any EXIF information.")
                return None
    except(Exception) as error:
        print(error)
        return None

def fetch_images_by_camera_model(src_path: str, extensions: list, model:str)->list:
    # fetch a list of filenames with the model name or a keyword in the exif model metadata
    #checks every image in source path tree
    try:
        filesnames = read_src_files(src_path,extensions)
    except(Exception) as error:
        print(error)
        filesnames = []
    images_names = []
    try:
        print(f'processing all images in the path ...')
        for index, file in enumerate(filesnames):
            if is_exif_model(file,model):
                images_names.append(file)
                print(f'{index} image  {file} taken with camera model {model}')
    except(Exception) as error:
        print(error)
    finally:
        print(f'{len(images_names)} images taken with camera model {model}')
    return images_names

def is_exif_model(filename:str, model:str) -> bool:
    try:
        with open(filename, "rb") as image_file:
            image = Image(image_file)
            try:
                if image.has_exif and model.lower() in image.model.lower():
                    print(image.model)
                    return True
            except(Exception) as error:
                print(f"{image.name} {error}")
                return False
    except(Exception) as error:
        print(error)
        return False

def get_exif_data(filename :str) -> dict:
    try:
        with open(filename, "rb") as image_file:
            image = Image(image_file)
            try:
                return image.get_all()
            except(Exception) as error:
                print(error)
                return {}
    except(Exception) as error:
        print(error)
        return {}

def get_exif_attribute(filename:str,tag:str) -> str:
    try:
        with open(filename, "rb") as image_file:
            image = Image(image_file)
            try:
                if image.has_exif and image.get(tag):
                    return image.get(tag)
            except(Exception) as error:
                print(error)
                return None
    except(Exception) as error:
        print(error)
        return None

