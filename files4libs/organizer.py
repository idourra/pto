#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python package to organize images using the exif date data in a file system structure YYYY/MM/DD
the three fists methods come from https://github.com/Zenith00/utils
"""

from datetime import datetime, date
import time
import pathlib
import sys
from typing import Optional
import pandas as pd
from collections import namedtuple
from exif import Image, DATETIME_STR_FORMAT

class Organizer:
    """
    Instantiate an Organizer object.
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
    def __init__(self, src_path="", dest_path="", extensions = [".jpg", ".jpeg", ".JPG", ".JPEG"], keyword= ""):
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
        exif_data ={}
        try:
            with open(filename, "rb") as image_file:
                image = Image(image_file)
                try:
                    exif_data = image.get_all()
                    return exif_data
                except(Exception) as error:
                    print(f" {filename} return an image.get_all error: {error} ")
                    try:
                        # get minimum metadata
                        exif_data = {"make":image.make,"model":image.model,"datetime":image.datetime,"datetime_original":image.datetime_original,
                        "datetime_digitized":image.datetime_digitized}
                        return exif_data
                    except(Exception) as error:
                        print(error)
                        return exif_data
        except(Exception) as error:
            print(f"{filename} error trying to open image: {error}")
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
        self.df = pd.DataFrame.from_records(data, columns=columns)
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
           
        excell_filename = pathlib.Path(self.dest_path) / excell_filename
        try:
            self.df.to_excel(excell_filename)
            print(f"{excell_filename} created")
            return True
        except(Exception) as error:
            print(error)
            return False
    
    def save_json_data(self, json_filename :str) -> bool:
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

   