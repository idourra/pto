# -*- coding: utf-8 -*-
"""
Python package to create and manage card images public access catalogs
"""
from pathlib import Path
from typing import Text
import requests
from urllib.parse import urlparse, urlunparse, urljoin
import webbrowser
import validators
import json
import random

class Catalog():
    """
    A Card Images Public Access Catalog (cipac) following a standarized file system structure
    for data and for naming the folders and files.
    The patter for the global name is iiiissscccgg
    iiii - 4 digits for institutions identification
    sss  - 3 digits for department identification
    ccc  - 3 digits for collection identification
    gg   - 2 digits for catalog type identification
  
    :param catalog_url: the  URL of a cipac catalog without final / eg. http://bnjm.sld.cu/bnjmsculyfof
    :type catalog_path: str
    """
    def __init__(self, catalog_url: str):
        
        # check that the catalog_url is correct
        assert validators.url(catalog_url) == True, "not valid url"

        # a tuple of url components eg.:
        # (scheme='http', netloc='bnjm.sld.cu', path='/bnjmsculyfof', params='', query='', fragment='')
        self._url = urlparse(catalog_url)

        assert  not self.url.path == "", "you must enter a valid cipac catalog name. It must be 12 characters long eg. bnjmsculyfof"

        # id of the catalog following the cipac name convention
        self.id = self.url.path[1:]
        assert len(self.id) == 12, "Not a valid cipac catalog name. It must be for example bnjmsculyfof"

        # cipac data is a json file that is associated with a cipac catalog and is a json file
        # with the same name of the catalog and extension .json eg bnjmsculyfof.json
        self._data = self.data

        # the quantity of drawers of the catalog
        self._q_drawers = self.q_drawers

        self.error = "None"

    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, new_url):
        if validators.url(new_url) == True:
            self._url = urlparse(new_url)
            self._id = self.url.path[1:]

        else:
            print ("Please enter a valid url")

    # @property
    # def id(self):
    #     return self._id

    @property
    def data(self):
        try:
            r = requests.get(urljoin(self.url.geturl() + "/",self.id+".json"))
            if r.ok:
                return(r.json())
            else:
                return None
        except(Exception) as error:
            print(error)
            return None

    @property
    def q_cards(self):
        # number of cards
        count = 0
        for row in self.data:
            count += int(row[3])
        return count

    @property
    def q_drawers(self):
        #number of drawers
        return len(self.data)
   
    def card_getter(self, i:int, j:int):
        #get a Card object with its attributes and methods
        assert i > 0 and i<= self.q_drawers, f"drawer number must be among 1 and {self.q_drawers} values"
        assert j >0 and j <= int(self.data[i-1][3]), f"card must be among 1 and {self.data[i-1][3]} values"
        card = Card(self.url.geturl(), i, j)
        return card

    def get_random_card_name(self):
        # genera un nombre de ficha aleatoria dentro del conjunto de fichas del catalogo
        # a nivel de cada gaveta o de el catalogo completo
        # si la variable total es verdadera se mueve en la totalidad
        # si es falsa solo dentro de una gaveta
        # TODO

        i = random.randint(1, self.q_drawers)
        q = int(self.data[i-1][3])
        j = random.randint(1, q)
        return (self.id + str(i).zfill(3) + str(j).zfill(4))

    @property
    def drawers_menu(self):
        # devuelve una lista que contiene las cadenas HTML
        # con el menu de gavetas usando bootstrap para su presentacion
        drawers_menu = {}
        for i, cadenai, cadenaf, q in self.data:
            drawers_menu[cadenai+"-"+cadenaf] = self.id + \
                str(i).zfill(3) + "0001"
        return drawers_menu

    @property
    def alphabet_menu(self):
        abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
               'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        alphabet_menu = {}
        for letter in abc:
            alphabet_menu[letter] = []
            drawer_list = list(self.drawers_menu.keys())
            for keywords in drawer_list:
                if letter.upper() in keywords[0].upper():
                    drawer_tags = list(
                        {keywords: self.drawers_menu[keywords]}.keys())[0]
                    drawer_id = list(
                        {keywords: self.drawers_menu[keywords]}.values())[0]
                    alphabet_menu[letter].append([drawer_tags, drawer_id])
        return alphabet_menu


    def any_card_name(self, i=int, j=int):

        #get  drawer name
        card_name = self.any_drawer_name(i)
        i = int(card_name[12:])
      
        # add card name
        if j > 0 and j <= int(self.data[i-1][3]):
            card_name += str(j).zfill(4)
        elif j<=0:
            card_name += str(1).zfill(4)
        else:
            card_name += str(int(self.data[i-1][3])).zfill(4)
        
        return card_name

    def any_drawer_name(self, i=int):
        #conform drawer name
        drawer_name = ""
        if i > 0 and i <= self.q_drawers:
            # valid drawer_number
            drawer_name += self.id + str(i).zfill(3)
        elif i == 0:
            # 0 invalid drawer number uses  drawer number 1
            drawer_name += self.id + str(1).zfill(3)
            i = 1
        else:
            # not valid drawer number, uses the max drawer number
            drawer_name += self.id + str(len(self.data)).zfill(3)
            i = len(self.data)
        return drawer_name

    def any_card_url(self, i, j):
        return self.url.geturl() + "/" + self.any_drawer_name(i) + "/" + self.any_card_name(i,j)

    def create_structure(self, dest_path=None, q_drawers=None) -> bool:
        """
        creates a cipac folder structure whith q_drawers folders

        :param dest_path: The path where the excell table willl be created
        :type dest_path: str

        :param q_drawers: The number of drawers of the cabinet
        :type q_drawers: int

        :param drawer_tags: a dict **{drawer_number:int, drawer_tag:str}
        :type drawer_tags: list(str)
        """
        dest_path = Path().cwd() if self.local_path is None else Path(self.local_path)
        q_drawers = 0 if q_drawers is None else q_drawers

        # create a folder for the catalog
        self.create_catalog_folder(dest_path)

        # create a folder for every drawer
        for i in range(q_drawers):
            drawer_path = Path.joinpath(dest_path, self.id + str(i+1).zfill(3))
            self.create_catalog_folder(drawer_path)
            self.create_catalog_folder(Path.joinpath(drawer_path, "images/"))

        return True

    def create_catalog_folder(self, dest_path):
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                print(dest_path)
                return True
            except(Exception) as error:
                print(error)
                return False
        return True

class Drawer():
    def __init__(self, catalog_url: str, drawer_number=1):
        """
        """
        # check that the catalog_url is correct
        assert validators.url(catalog_url) == True, "not valid url"

        # instantiate the Catalog object
        self.catalog = Catalog(catalog_url)

        assert drawer_number>0 and drawer_number<= self.catalog.q_drawers, f"drawer number must be among 1 and {self.catalog.q_drawers}"
        # drawer id
        self.id = self.catalog.id + str(drawer_number).zfill(3)

        self.position = drawer_number

        self.url = urlparse(self.catalog.url.geturl() + "/" + self.id)

        self.q_cards = int(self.catalog.data[self.position-1][3])

    @property
    def coordinates(self):
        #previous, next, quarter,eighth, three_eighths, half, five_eighths, three_quarters, seven_eighths
        actual = self.position
        if actual < self.q_cards:
            next = self.position + 1
        else:
            next = self.position
        if actual > 1:
            previous = actual - 1
        else:
            previous = actual
        return {"actual": actual,
                "previous": previous,
                "next": next,
                "first": 1,
                "last_drawer": self.catalog.q_drawers,
                "last_card": self.q_cards,
                "quarter": int(self.q_cards // 4),
                "eighth": int(self.q_cards // 8),
                "three_eighths": int(self.q_cards*3 // 8),
                "half": int(self.q_cards // 2),
                "five_eighths": int(self.q_cards*5 // 8),
                "three_quarters": int(self.q_cards*3 // 4),
                "seven_eighths": int(self.q_cards*7 // 8)}


class Card ():
    def __init__(self, catalog_url: str, drawer_number=1, card_number=1):
        """
        A cipac digital respresentarion of a library card


        :param catalog_url: the url of the file system catalog data  eg. "http://bnjm.sld.cu/bnjmsculyfof"
        :type catalog_url: str

        :param drawer_number: the number of the drawer where the card is located
        :type drawer_number: int

        :param card_number: the position of the card in the drawer
        :type card_number: int

        """
        # check that the catalog_url is correct
        assert validators.url(catalog_url) == True, "not valid url"

        # instantiate the catalog object
        self.catalog = Catalog(catalog_url)

        # instantiate the drawer
        self.drawer = Drawer(self.catalog.url.geturl(), drawer_number)

        # check that it is a valid card number
        assert card_number <= self.drawer.q_cards and card_number >= 0, "the card with position  {drawer_number} is out of range, the drawer has {self.drawer.q_cards} cards"

        # generate de card id
        self.id = self.drawer.id + str(card_number).zfill(4)

        # card position inside the drawer
        self.position = card_number

        # other card attributes

        self.error = "None"

        # card image_name
        self.image_name = self.id + ".jpg"

        # card_image_ocr
        self.ocr_image_name = self.id + ".txt"

        self.url = urlparse(self.drawer.url.geturl() + "/" + self.id)
        self.url_image = urlparse(self.drawer.url.geturl() + "/images/" + self.image_name)
        self.url_ocr = urlparse(self.drawer.url.geturl() + "/" + self.ocr_image_name)
        self.url_api = urlparse("../cards/" + self.id)
        # card json data
        # self.json_data = json.dumps({self.id: {"id": self.id,
        #                             "image_url": self.url_image.geturl(),
        #                                        "ocr_text_url": self.url_ocr.geturl(),
        #                                        "drawer": self.drawer.position,
        #                                        "position": self.position},
        #                              "ocr_text": self.ocr_text})

    @property
    def ocr_text(self):
        if self.url.scheme == "file":
            try:
                with open(self.ocr_image_name, "r", encoding="utf-8") as f:
                    ocr_text = f.read()
                    return ocr_text
            except(Exception) as error:
                print(error)
                self.error = str(error)
                return str(error)
        else:
            try:
                r = self.get_remote(".txt")
                return r.text
            except(Exception) as error:
                print(error)
                self.error = str(error)

                return ""

    @property
    def image_content(self):
        try:
            r = self.get_remote(".jpg")
            return r.content
        except(Exception) as error:
            print(error)
            self.error = str(error)
            return

    def get_remote(self, suffix: str):
        """
        get remote data for the card from a valid cipac catalog

        :param suffix: .jpg or .txt extension
        :type: str
        """
        assert suffix in [".jpg", ".txt"], "suffix must be .jpg or .txt"
        if suffix == ".jpg":
            url = self.url_image.geturl()
        elif suffix == ".txt":
            url = self.url_ocr.geturl()
        try:
            r = requests.get(url)
            r.encoding = "utf-8"
            return r
        except(Exception) as error:
            print(error)
            self.error = str(error)

            return

    def open_web(self,netloc:str):
        url = urljoin(netloc,self.url_api.path)
        webbrowser.open(url)

    # TODO
    # @property
    # def json(self):
    #     {self.id:{"id":self.id,
    #     "image_url":self.url_image,
    #     "ocr_text_url":self.url_ocr,
    #     "drawer":self.drawer.position,
    #     "position":self.position},
    #     "ocr_text": self.ocr_text,
    #     "image_content":self.image_content}

    @property
    def coordinates(self):
        #previous, next, quarter,eighth, three_eighths, half, five_eighths, three_quarters, seven_eighths
        if self.position == 1:
            previous = 1
        else:
            previous = self.position - 1
        if self.position >= self.drawer.q_cards:
            next = self.drawer.q_cards
        else:
            next = self.position + 1
        card_coordinates = self.drawer.coordinates
        card_coordinates["actual"] = self.position
        card_coordinates["previous"] = previous
        card_coordinates["next"] = next
        return card_coordinates

    def save_image(self) -> bool:
        imagename = self.id + ".jpg"
        filename = Path(self.local_path) / "images" / imagename
        try:
            with open(filename, "wb") as fout:
                fout.write(self.image_content)
                return True
        except(Exception) as error:
            print(error)
            self.error = str(error)
            return False

    def save_ocr(self) -> bool:
        imagename = self.id + ".txt"
        filename = Path(self.local_path) / imagename
        try:
            with open(filename, "w", encoding="utf-8") as fout:
                fout.write(self.ocr_text)
                return True
        except(Exception) as error:
            print(error)
            self.error = str(error)
            return False

    @property
    def url_coordinates(self):
        # generates a dictionary with urls of the coordinates of the card
        url_coordinates = {}
        for coordinate in self.coordinates.keys():
            url_coordinates[coordinate] = self.drawer.url.geturl(
            ) + self.drawer.id + str(self.coordinates.get(coordinate)).zfill(4)
        return url_coordinates

    @property
    def coordinate_ids(self):
        # generates a dictionary with card names of the coordinates
        coordinate_ids = {}
        for coordinate in self.coordinates.keys():
            coordinate_ids[coordinate] = self.drawer.id + \
                str(self.coordinates.get(coordinate)).zfill(4)
        return coordinate_ids
