#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python package to organize images using the exif date data in a file system structure YYYY/MM/DD
the three fists methods come from https://github.com/Zenith00/utils
"""

from datetime import datetime, date
import time
from pathlib import Path
import pathlib
import sys
from typing import Optional
import pandas as pd
from collections import namedtuple
from exif import Image, DATETIME_STR_FORMAT

class Organizer:
    """
    Instantiate an Organizer object.
    an Organizer object will scan files  in a file system and organize collections and catalogs 
    of files using metadata available to conform a table and export to different formats(excell, csv, json) 
    
    :param src_path: The path that will be scanned for images
    :type src_path: str
    
    :param dest_path: The path where the excell table willl be created
    :type dest_path: str

    :param extensions: A list of valid file extensions. Default [".jpg", ".jpeg"] the more common images format
    :type extensions: list

    :param keyword: A keyword to filter the files by its name. Default ""
    :type keyword: str
    """
    def __init__(self, src_path="", dest_path="", extensions = [".jpg", ".jpeg", ".JPG", ".JPEG"], keyword= ""):
        if src_path == "":
            self.src_path = Path().cwd()
        else: 
            self.src_path = Path(src_path)

        if dest_path == "":
            self.dest_path = self.src_path
        else:
            self.dest_path = Path(dest_path)

        self.extensions = extensions
        self.keyword = keyword
        self.df = pd.DataFrame()
        self.ok = True

    def get_files(self, extensions = None, keyword = None) ->list:
        """
        returns the list of filenames in the folder tree that satisfies the extension and keyword filters

        :param extensions: A list of valid file extensions. Default [".jpg", ".jpeg"] the more common images format
        :type extensions: list

        :param keyword: A keyword to filter the files by its name. Default ""
        :type keyword: str

        """
        if extensions is None:
            extensions = self.extensions
        if keyword is None:
            keyword = self.keyword

        sys.setrecursionlimit(5000)
        try:
            files = {p.resolve() for p in self.src_path.rglob("*.*") if p.suffix.lower() in extensions and keyword.lower() in p.stem.lower()} 
            # sort files by name
            files = sorted(files)
            #print(f'{str(len(files))} files in {src_path} path tree with extensions {extensions}')
            sys.setrecursionlimit(1000)
            return files
        except(Exception) as error:
            print(error)
            sys.setrecursionlimit(1000)
            self.ok = False
            return []

    def get_all_files(self,pattern = "*.*"):
        """
        returns the list of all filenames in the folder tree that satisfies the parameter pattern

        :param pattern: A pattern to search files 
        :type pattern: str

        """
        return list(self.src_path.rglob(pattern))


    def get_exif_data(self, filename :str) -> dict:
        exif_data ={}
        try:
            with open(filename, "rb") as image_file:
                image = Image(image_file)
                try:
                    exif_data = image.get_all()
                    return exif_data
                except(Exception) as error:
                    print(f" {filename} return an image.get_all error: {error} ")
                    self.ok = False
                    try:
                        # get minimum metadata
                        exif_data = {"make":image.make,"model":image.model,"datetime":image.datetime,"datetime_original":image.datetime_original,
                        "datetime_digitized":image.datetime_digitized}
                        self.ok = True
                        return exif_data
                    except(Exception) as error:
                        print(error)
                        self.ok = False
                        return exif_data
        except(Exception) as error:
            print(f"{filename} error trying to open image: {error}")
            self.ok = False
            return exif_data
   
    def get_exif_attribute(self, exif_data:dict, tag: str):
        return exif_data.get(tag)

    def read_files_exif_data(self, files:list) ->list:
        all_files_exif_metadata = []
        for file in files:           
            # get exif metadata of the image
            exif_data = self.get_exif_data(file)
            make = exif_data.get("make")
            model = exif_data.get("model")
            datetime_original = exif_data.get("datetime_original")
            datetime_digitized = exif_data.get("datetime_digitized")

            #conform a tuple with selected fields of the  metadata of the file and add to the list of files
            all_files_exif_metadata.append((file.as_uri(), file.stat().st_size, file.name, file.parent.absolute(), time.ctime(file.stat().st_ctime),time.ctime(file.stat().st_mtime),
                make,model, datetime_original, datetime_digitized ))
        
        return all_files_exif_metadata  
    
    def create_data_frame(self,data =[]) -> pd.DataFrame:
        if data == []:
            data = self.read_files_exif_data(self.get_files())
        
        columns = ["url","file_size","file_name", "parent", "datetime_created","datetime_modified","exif_metadata_make","exif_metadata_model","exif_metadata_datetime_original","exif_metadata_datetime_digitized"]
        try:
            self.df = pd.DataFrame.from_records(data, columns=columns)

        except(Exception) as error:
            print(error)
            self.ok = False
            return self.df
        print(self.df.head())
        return self.df
    
    def create_data_table(self, data:list):
        table_rows =[]
        
        # Declaring namedtuple()
        columns = ["url","file_size","file_name", "parent", "datetime_created","datetime_modified","exif_metadata_make","exif_metadata_model","exif_metadata_datetime_original","exif_metadata_datetime_digitized"]
        Record = namedtuple('Record', columns)
        for record in data:
            table_rows.append(Record(record))
        return table_rows
    
    def save_excell_file(self, excell_filename:str) ->bool:
        """
        :param excell_filename: A valid name of the excell file. If not gived it will use excell_file.xlsx as default value
        :type excell_filename: str 
        
        """
           
        excell_filename = Path(self.dest_path) / excell_filename
        try:
            self.df.to_excel(excell_filename)
            print(f"{excell_filename} created")
            return True
        except(Exception) as error:
            print(error)
            return False
    
    def save_json_data(self, json_filename :str) -> bool:
        sys.setrecursionlimit(5000)
        json_filename = Path(self.dest_path) / json_filename
        try:
            self.df.to_json("data.json")
            print(f"{json_filename} created")
            sys.setrecursionlimit(1000)
            return True
        except(Exception) as error:
            print(error)
            sys.setrecursionlimit(1000)
            return False

class Collection():
    def __init__(self, name : str, path : str):
        self.path = pathlib.Path(path)

    def __getattr__(self, attr):
        return getattr(self.path, attr)
    
    def create_calendar_folder(self, dest_path:str, file_date: datetime):
        """
        creates a file folder in the structure YYYY/MM/DD
        if the folder does not exits

        :param dest_path: The path where the excell table willl be created
        :type dest_path: str

        """
        dest_path = Path(dest_path)
        year_path = Path(dest_path) / str(file_date.year)
        month_path = year_path / str(file_date.month)
        day_path = month_path / str(file_date.day)
        try:
            if not dest_path.exists():
                dest_path.mkdir(parents=True, exist_ok=True)
                print(dest_path)
            if not year_path.exists():
                year_path.mkdir(parents=True, exist_ok=True)
                print(year_path)
            if not month_path.exists():
                month_path.mkdir(parents=True, exist_ok=True)
                print(month_path)
            if not day_path.exists():
                day_path.mkdir(parents=True, exist_ok=True)
                print(day_path)
            return day_path
        except(Exception) as error:
            print(error)
            return None

    def create_alphabet_folder(self, dest_path: str, iso_language = "en") -> bool:
        dest_path = Path(dest_path)
        if iso_language == "es":
            alphabet = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
        elif iso_language == "en":
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        else:
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        # create the base destination directory
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                print(dest_path)
            except(Exception) as error:
                print(error)
                return False
        
        for letter in alphabet:
            letter_path = Path.joinpath(dest_path, letter)
            if not letter_path.exists():
                # create folder
                try:
                    letter_path.mkdir(parents=True, exist_ok=True)
                except(Exception) as error:
                    print(error)
                    return False
        return True