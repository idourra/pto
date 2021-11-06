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


def get_url(scheme: str, netloc : str, path: str):
    """
    From RFC 1808, Section 2.1, every URL should follow a specific format:
    https://www.rfc-editor.org/rfc/rfc1808.html#section-2.1
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>

    scheme: The protocol name, usually http/https
    netloc: Contains the network location - which includes the domain itself (and subdomain if present), the port number, along with an optional credentials in form of username:password. Together it may take form of username:password@domain.com:80.
    path: Contains information on how the specified resource needs to be accessed.
    params: Element which adds fine tuning to path. (optional)
    query: Another element adding fine grained access to the path in consideration. (optional)
    fragment: Contains bits of information of the resource being accessed within the path. (optional)

    Lets take a very simple example to understand the above clearly:

    http://bnjm.sld.cu/bnjmsculyfof/bnjmsculyfof001/bnjmsculyfof0010001

    In the above example:

    https is the scheme (first element of a URL)
    bnjm.sld.cu is the netloc (sits between the scheme and path)
    /bnjmsculyfof/bnjmsculyfof001/bnjmsculyfof0010001
    is the path (between the netloc and params)
    meow is the param (sits between path and query)
    breed=siberian is the query (between the fragment and params)
    pawsize is the fragment (last element of a URL)

    """

    return urlunparse([scheme, netloc, path,"","",""])

class Catalog():
    """
    catalog tiene 11 digitos, y es una variable str
            Funciona como un codigo de 11 digitos:
                nombre de la institucion: 4 digitos.g bnjm
                sala en que esta la coleccion: 3 digitos  scu
                tipo de coleccion: 3 digitos e.g. lyf
                tipo de catalogo: 2 digitos e.g. of
                iriCatalogo = 'bnjmsculyfof'

    :param id_catalog: a string of 12 characters identifying the catalog eg. 'bnjmsculyfof'
    :type id_catalog: str

    :param catalog_url: the  URL where the catalog data is located
                        eg.file:///home/urra/catalogos/bnjmsculyfof for a local catalog
                        htp://bnjm.sld.cu/bnjmsculyfof for a catalog in Internet
    :type catalog_path: str
    """
    def __init__(self , id_catalog : str, catalog_url : str, catalog_local_path = None):

        assert len(id_catalog) == 12, "id_catalog shoud have 12 characters eg. 'bnjmsculyfof'"

        self.local = False

        #id of the catalog following the cipac name convention
        self.id = id_catalog

        self.error = "None"


        catalog_url = catalog_url.strip()
        if not catalog_url[:-1] ==  "/":
            self.catalog_url = catalog_url + "/"
        else:
            self.catalog_url = catalog_url
        self.url = urlparse(catalog_url)

        #url where the json file with catalog structure is available
        self.data_url = urljoin(self.catalog_url, self.id + ".json")

        # catalog local_path where a copy of the cipac will be created
        self.local_path = Path().cwd() if catalog_local_path is None else Path(catalog_local_path)

        #number of drawers
        self.q_drawers = len(self.data)

        # number of cards
        count = 0
        for row in self.data:
            count += int(row[3])
        self.q_cards = count

    @property
    def data(self):
        try:
            r = requests.get(self.data_url)
            return(r.json())
        except(Exception) as error:
            print(error)

    def get_card(self, i, j):
        id_card = self.id + str(i).zfill(3) + str(j).zfill(4)
        card = Card(id_card,self.url.geturl(),self.local_path)
        return card

    def get_random_card(self):
        # genera un nombre de ficha aleatoria dentro del conjunto de fichas del catalogo
        # a nivel de cada gaveta o de el catalogo completo
        # si la variable total es verdadera se mueve en la totalidad
        # si es falsa solo dentro de una gaveta
        #TODO

        i = random.randint ( 1 , self.q_drawers )
        q = int(self.data[i-1][3])
        j = random.randint ( 1 , q )
        return (self.id + str ( i ).zfill ( 3 ) + str ( j ).zfill ( 4 ))

    def create_structure(self, dest_path = None, q_drawers = None)-> bool:
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

        #create a folder for the catalog
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

    @property
    def menu(self):
        # devuelve una lista que contiene las cadenas HTML
        # con el menu de gavetas usando bootstrap para su presentacion

        menuGaveta = [ ]

        cadenanumeros = ""
        cadena = ""

        for i , cadenai , cadenaf , q in self.data:
            enlaceacgi = "../cgi-bin/item.py?idficha=" + \
                         self.id + str ( i ).zfill ( 3 ) + "0001"
            if cadenai == cadenaf:
                menuGaveta.append ( '<li><a href="' + enlaceacgi +
                                    '" alt="' + str ( i ).zfill ( 3 ) + "0001" + '"> ' + cadenai + ' </a></li>' )
            else:
                menuGaveta.append ( '<li><a href="' + enlaceacgi + '" alt="' +
                                    str ( i ).zfill ( 3 ) + "0001" + '"> ' + cadenai + "-" + cadenaf + ' </a></li>' )
        abc = [ 'A' , 'B' , 'C' , 'D' , 'E' , 'F' , 'G' , 'H' , 'I' , 'J' , 'K' , 'L' , 'M' ,
                'N' , 'Ñ' , 'O' , 'P' , 'Q' , 'R' , 'S' , 'T' , 'U' , 'V' , 'W' , 'X' , 'Y' , 'Z' ]

        for letra in abc:
            cadena += ' <div class="btn-group btn-group-sm" ><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"> ' + \
                      letra + '</button> <ul class="dropdown-menu" role="menu">'
            for linea in menuGaveta:
                if "> " + letra in linea or "-" + letra in linea:
                    cadena += linea

            cadena += '</ul></div>'
        cadena += '</div>'

        return menuGaveta

    def any_card_name(self,i= int, j= int):
        card_name = ""
        if i >0 and i<= self.q_drawers:
            card_name += self.id + str(i).zfill(3)
            if  j > 0 and j <= int(self.data[i-1][3]):
                card_name += str(j).zfill(4)
            else:
                card_name += str(1).zfill(4)
        else:
            card_name += self.id + str(1).zfill(3)
            if  j > 0 and j <= int(self.data[1][3]):
                card_name += str(j).zfill(4)
            else:
                card_name += str(1).zfill(4)
        return card_name

    def any_drawer_name(self,i= int):
        if i >0 and i<= self.q_drawers:
            return self.id + str(i).zfill(3)
        else:
            return self.id + str(1).zfill(3)

    def any_card_url(self,i,j):
        return self.url.geturl() + self.any_drawer_name()
class Drawer(Catalog):
    #TODO tratar de manera integral el camino a partir del scheme
    def __init__(self , id_drawer : str, catalog_url : str):
        """
        """
        # check that id_drawer is correct
        assert len(id_drawer) == 15, "id_drawer shoud have 15 characters eg. 'bnjmsculyfof001'"

        self.id =id_drawer

        self.catalog = Catalog(self.id[:12], catalog_url)

        self.error = "None"


        #drawer position inside the catalog cabinet
        self.position = int(id_drawer[12:15])

        #drawer url
        self.url = urlparse(urljoin(self.catalog.url.geturl(), "/" + self.id[:12] + "/" + self.id + "/"))

        #drawer local_path
        self.local_path = Path(self.catalog.local_path) / self.id

        #q_cards in drawer
        self.q_cards = int(self.catalog.data[self.position-1][3])

    #TODO check the use of url versus local files

    def card_id(self, card_position):
        assert card_position <= self.q_cards
        return self.id + str(card_position).zfill(4)

    def get_card(self, card_position: int):
        assert card_position <= self.q_cards
        card_id = self.id + str(card_position).zfill(4)
        return Card(card_id,".")

    @property
    def coordinates(self):
        #previous, next, quarter,eighth, three_eighths, half, five_eighths, three_quarters, seven_eighths
        actual = self.position
        if actual < self.q_cards:
            next = self.position +1
        else:
            next = self.position
        if actual>1:
            previous = actual -1
        else:
            previous = actual
        return  {"actual":actual,
                "previous":previous,
                "next" : next,
                "first":1,
                "last_drawer":self.catalog.q_drawers,
                "last_card": self.q_cards,
                "quarter" : int(self.q_cards / 4),
                "eighth" : int(self.q_cards / 8),
                "three_eighths" : int(self.q_cards*3 / 8),
                "half" : int(self.q_cards / 2),
                "five_eighths" : int(self.q_cards*5 / 8),
                "three_quarters" : int(self.q_cards*3 / 4),
                "seven_eighths" : int(self.q_cards*7 / 8)}

class Card ( Drawer ):
    def __init__(self ,card_id : str, catalog_url : str, catalog_local_path :str):
        """
        A cipac digital respresentarion of a library card

        :param card_id: the cipac compatible card identification eg. "bnjmsculyfof0010001"
        :type card_id: str

        :param catalog_url: the url of the file system catalog data  eg. "http://bnjm.sld.cu/bnjmsculyfof"
        :type catalog_url: str


        """

        # check that card_id is correct
        assert len(card_id) == 19, "card_id must have 19 characters eg. 'bnjmsculyfof0010001' and follow th cipac convention for naming"


        # check that the catalog_url is correct
        assert validators.url(catalog_url) == True, "not valid url"


        #card attributes

        # card id
        self.id =card_id

        self.error = "None"

        #card image_name
        self.image_name = "/" + self.id[:12] + "/" + self.id[:15] + "/images/" + self.id + ".jpg"

        #card_image_ocr
        self.ocr_image_name =  "/" + self.id[:12] + "/" + self.id[:15] + "/" + self.id + ".txt"


        # card catalog data and methods
        self.catalog = Catalog(card_id[:12],catalog_url, catalog_local_path)

        #drawer catalog data and methods
        self.drawer = Drawer(card_id[:15],catalog_url)

        # catalog local_path where a copy of the cipac will be created
        self.local_path = Path().cwd() / self.catalog.id / self.drawer.id  if catalog_local_path is None else Path(catalog_local_path) / self.drawer.id

        #card position inside the drawer
        self.position = int(card_id[15:19])
        assert self.position <= self.drawer.q_cards and self.position>=0, f"the card {self.id} with position  {self.id[-4:]} is out of range, the drawer has {self.drawer.q_cards} cards"

        #TODO valorar ajustar la posicion de la ficha al maximo de fichas en la gaveta cuando esta es superior al rango
        #a los efectos de la localizacion de las fichas



        # if j > int ( self.g.qFichas ):
        #     self.j = int ( self.g.qFichas )
        # else:
        #     self.j = j
        # card url
        self.url = self.drawer.url
        self.url_image = urlparse(urljoin(self.drawer.url.geturl(), "images/" + self.id + ".jpg"))
        self.url_ocr = urlparse(urljoin(self.drawer.url.geturl(),  self.id + ".txt"))
        # url of the card in the cipac webapp
        self.url_api = urlparse(urlunparse([self.url.scheme,self.url.netloc,'/cgi-bin/item.py',"","idficha="+self.id,""]))

        # card json data
        self.json_data = json.dumps({self.id:{"id":self.id,
                                    "image_url":self.url_image.geturl(),
                                    "ocr_text_url":self.url_ocr.geturl(),
                                    "drawer":self.drawer.position,
                                    "position":self.position},
                                    "ocr_text": self.ocr_text})


    @property
    def ocr_text(self):
        if self.url.scheme == "file":
            try:
                with open(self.ocr_image_name,"r", encoding="utf-8") as f:
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
        if self.url.scheme == "file":
            try:
                with open(self.image_name,"r", encoding="utf-8") as f:
                    image_content = f.read()
                    return image_content
            except(Exception) as error:
                print(error)
                return str(error)
        else:
            try:
                r = self.get_remote(".jpg")
                return r.content
            except(Exception) as error:
                print(error)
                self.error = str(error)

                return ""

    def get_remote(self,suffix:str):
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

    def open_web(self):
        webbrowser.open (self.url_api.geturl() )

    def json(self):
        {self.id:{"id":self.id,
        "image_url":self.url_image,
        "ocr_text_url":self.url_ocr,
        "drawer":self.drawer.position,
        "position":self.position},
        "ocr_text": self.ocr,
        "image_content":self.image_content}

    @property
    def coordinates(self):
        #previous, next, quarter,eighth, three_eighths, half, five_eighths, three_quarters, seven_eighths
        if self.position == 1:
            previous = 1
        else:
            previous = self.position -1
        if self.position >= self.drawer.q_cards:
            next = self.drawer.q_cards
        else:
            next = self.position +1
        card_coordinates = self.drawer.coordinates
        card_coordinates["actual"] =self.position
        card_coordinates["previous"] = previous
        card_coordinates["next"] = next
        return  card_coordinates

    def save_image(self) ->bool:
        imagename = self.id + ".jpg"
        filename = Path(self.local_path) /"images" / imagename
        try:
            with open(filename,"wb") as fout:
                fout.write(self.image_content)
                return True
        except(Exception) as error:
            print(error)
            self.error = str(error)
            return False
    def save_ocr(self) ->bool:
        imagename = self.id + ".txt"
        filename = Path(self.local_path) / imagename
        try:
            with open(filename,"w",encoding="utf-8") as fout:
                fout.write(self.ocr_text)
                return True
        except(Exception) as error:
            print(error)
            self.error = str(error)
            return False



