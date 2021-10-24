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

class Organizer:
    """
    Instantiate a Organizer object.
    an Organizer will scan files  and exif metadata extracted and converted to json 
    to conform a table and export to different formats(excell, csv, json) 
    
    :param src_path: The path that will be scanned for images
    :type src_path: str
    
    :param dest_path: The path where the excell table willl be created
    :type dest_path: str

    :param extensions: A list of valid file extensions. Default [".jpg", ".jpeg"] the more common images format
    :type extensions: list

    :param keyword: A keyword to filter the files by its name. Default ""
    :type keyword: str
    """
    def __init__(self, src_path="", dest_path="", extensions = [".jpg", ".jpeg"], keyword= ""):
        if src_path == "":
            self.src_path = pathlib.Path().cwd()
        else: 
            self.src_path = pathlib.Path(src_path)

        if dest_path == "":
            self.dest_path = self.src_path
        else:
            self.dest_path = pathlib.Path(dest_path)

        self.extensions = extensions
        self.keyword = keyword
        self.df = pd.DataFrame()
   
    def get_files(self) ->list:
        sys.setrecursionlimit(5000)
        try:
            files = {p.resolve() for p in self.src_path.glob("**/*") if p.suffix.lower() in self.extensions and self.keyword.lower() in p.stem.lower()} 
            # sort files by name
            files = sorted(files)
            #print(f'{str(len(files))} files in {src_path} path tree with extensions {extensions}')
            sys.setrecursionlimit(1000)
            return files
        except(Exception) as error:
            print(error)
            sys.setrecursionlimit(1000)
            return []

    def get_exif_data(self, filename :str) -> dict:
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
    
    
    def get_exif_attribute(self, exif_data:dict, tag: str):
        return exif_data.get(tag)

    
    def read_files_exif_data(self, files:list):
        all_files_exif_metadata = []
        for file in files:
            
            # get exif metadata of the image
            exif_data = self.get_exif_data(file)
            
            #conform a tuple with the metadata of the file and add to the list of files
            all_files_exif_metadata.append((file.as_uri(), file.stat().st_size, file.name, file.parent.absolute(), time.ctime(file.stat().st_ctime),time.ctime(file.stat().st_mtime),
                exif_data.get("make"),exif_data.get("model"), exif_data.get("datetime_original"), exif_data.get("datetime_digitized")  ))
        
        return all_files_exif_metadata  
    
    
    def create_data_frame(self):
        columns = ["url","file_size","file_name", "parent", "datetime_created","datetime_modified","exif_metadata_make","exif_metadata_model","exif_metadata_datetime_original","exif_metadata_datetime_digitized"]
        self.df = pd.DataFrame.from_records(self.read_files_exif_data(self.get_files()), columns=columns)
        print(self.df.head())
        return 
    
    def save_excell_file(self, excell_filename:str):
        """
        :param excell_filename: A valid name of the excell file. If not gived it will use excell_file.xlsx as default value
        :type excell_filename: str 
        """
            
        excell_filename = pathlib.Path(self.dest_path) / excell_filename
        try:
            self.df.to_excel(excell_filename)
            print(f"{excell_filename} created")
            return True
        except(Exception) as error:
            print(error)
            return False
    
    def save_json_data(self, json_filename :str):
        sys.setrecursionlimit(5000)
        json_filename = pathlib.Path(self.dest_path) / json_filename
        try:
            self.df.to_json("data.json")
            print(f"{json_filename} created")
            sys.setrecursionlimit(1000)
            return True
        except(Exception) as error:
            print(error)
            sys.setrecursionlimit(1000)
            return False
