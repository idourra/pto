#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python package to organize images using the exif date data in a file system structure YYYY/MM/DD
the three fists methods come from https://github.com/Zenith00/utils
"""

from datetime import datetime
import errno
import os
import pathlib
import shutil
import sys
import numpy
from exif import Image

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

def extract_exif_date(filename)-> str:
    try:
        with open(filename, "rb") as image_file:
            image = Image(image_file)
            if image.has_exif:
                if image.datetime_original:
                    image_date_data = image.datetime_original[0:10]+" 00:00:00"
                elif image.datetime_digitized:
                    image_date_data = image.datetime_digitized[0:10]+" 00:00:00"
                else:
                    image_date_data = "0000:00:00 00:00:00"
                if "-" in image_date_data:
                    image_date_data = image_date_data.replace("-", ":")
                # if len(image_date_data) > 19:
                #     image_date_data = image_date_data[0:18]
                # if "T" in image_date_data.upper():
                #     image_date_data = image_date_data.replace("T", " ")
                # elif not " " in image_date_data:
                #     image_date_data = image_date_data[0:9] + " " + image_date_data[10:]

                return datetime.strptime(image_date_data, '%Y:%m:%d %H:%M:%S')
            else:
                print("does not contain any EXIF information.")
                return None
    except(Exception) as error:
        print(error)
        return None

def create_date_path(dest_path: str, file_date: str) -> str:

    year_path = os.path.join(dest_path, str(file_date.year))
    month_path = os.path.join(year_path, str(file_date.month))
    day_path = os.path.join(month_path, str(file_date.day))
    try:
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
            print(dest_path)
        if not os.path.exists(year_path):
            os.mkdir(year_path)
            print(year_path)
        if not os.path.exists(month_path):
            os.mkdir(month_path)
            print(month_path)
        if not os.path.exists(day_path):
            os.mkdir(day_path)
            print(day_path)

        return day_path
    except(Exception) as error:
        print(error)
        return None

def split_folder_to_subfolders(src_files: list,dest_path : str,number_of_files : int) -> bool:
   
    #calculate the number of folders to create in relation with the total of files
    if len(src_files) % number_of_files > 0:
        number_of_folders = int(len(src_files)/number_of_files) + 1
    else:
        number_of_folders = int(len(src_files)/number_of_files)

    print(f"number of files:{number_of_files}, number of folders {number_of_folders}")

    #split the list of file names in the number of folders projected
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
                print(file + " copied to " + new_path)
            except(Exception) as error:
                print(error)
                return False
    return True

def split_folder(dest_path: str, files: list, n: int) -> bool:
    #split a list of files into subfolders
    files =  sorted(files)
    try:
        print(dest_path)
        split_folder_to_subfolders(files,os.path.join(dest_path, "subfolder",n))
    except(Exception) as error:
        print(error)
        return False
    return True

def read_src_files(src_path: str,extensions: list) -> list:
    # returns a list with all files with the extension contained in the variable extensions
    try:
        files = {p.resolve() for p in pathlib.Path(src_path).glob("**/*") if p.suffix in extensions}
        #sort files by name
        files = sorted(files)
        print(f'{str(len(files))} files in the {src_path}')
        return files
    except(Exception) as error:
        print(error)
        return []

def put_files_in_calendar(src_path: str,dest_path: str, files: list) -> bool:
    #from a list of file names in a path, checks every image and using the exif metadata
    #copy the file to the file system in a structure representing a calendar
    #if the image file does not have a date, the image file is located in a none_exif_date folder
    # for eg. /2021/10/1/ etc
    none_dated_files = []
    for file in files:
        src_file_path = os.path.join(src_path, file)
        if os.path.isfile(src_file_path) and ".jpg" in src_file_path.lower():
            image_date = extract_exif_date(src_file_path)
            if image_date:
                file_path = create_date_path(dest_path, image_date)
                try:
                    shutil.copy2(src_file_path, file_path)
                    print(os.path.join(file_path,file))
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
                    print(os.path.join(file_path,file))
                except(Exception) as error:
                    print(error)
    return True







