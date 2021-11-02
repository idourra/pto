# -*- coding: utf-8 -*-
"""
Python package to create and manage card images public access catalogs
"""
from pathlib import Path
import requests
from urllib.parse import urlparse, urlunparse, urljoin
import webbrowser


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

    :param id_catalog: a string of 12 characters identifying the catalog eg. 'bnjmsculyfof'
    :type id_catalog: str

    :param catalog_url: the  URL where the catalog data is located 
                        eg.file:///home/urra/catalogos/bnjmsculyfof for a local catalog
                        htp://bnjm.sld.cu/bnjmsculyfof for a catalog in Internet
    :type catalog_path: str
    """
    def __init__(self , id_catalog : str, catalog_url : str):

        assert len(id_catalog) == 12, "id_catalog shoud have 12 characters eg. 'bnjmsculyfof'"

        self.id = id_catalog
        catalog_url = catalog_url.strip()
        if not catalog_url[:-1] ==  "/":
            self.catalog_url = catalog_url + "/"
        else:
            self.catalog_url = catalog_url 

        self.url = urlparse(catalog_url)
        self.data_url = urljoin(self.catalog_url, self.id + ".json")

        if self.url.netloc == "":
            self.local_path = Path(self.url.path)
            if self.local_path.exists():
                self.local = True
            else:
                self.local = False
        else:
            self.local = False
            self.local_path = None

    @property
    def data(self):
        if not self.local:
            try:
                r = requests.get(self.data_url)
                return(r.json())
            except(Exception) as error:
                print(error)
        else:
            pass

    def get_card(self, i, j):
        id_card = self.id + str(i).zfill(3) + str(j).zfill(4)
        card = Card(id_card,self.catalog_url)
        return card


class Drawer():
    #TODO tratar de manera integral el camino a partir del scheme
    def __init__(self , id_drawer : str, catalog_url : str):
        """
        """
        # check that id_drawer is correct
        assert len(id_drawer) == 15, "id_drawer shoud have 15 characters eg. 'bnjmsculyfof001'"
        
        self.id =id_drawer

        self.catalog = Catalog(self.id[:12], catalog_url)
        
        #if condition returns False, AssertionError is raised:
        # id_card identifies it uniquelly in the context of a catalog 

        #take card basic data pattern, drawer and number

        # pattern name
        # the pattern name gives additional context information
        self.pattern = id_drawer[:12]

        #drawer position inside the catalog cabinet
        self.position = int(id_drawer[12:15])

        #drawer path
        self.path = "/" + self.id[:12] + "/" + self.id + "/"

        self.url = urlparse(catalog_url)

        if self.url.netloc == "":
            self.local = True
            self.local_path = Path(self.url.path)
        else:
            self.local = False
            self.local_path = ""

    def url(self, scheme:str, net_loc: str, path :str):
        return get_url(scheme. netloc, path)
    
    #TODO check the use of url versus local files
    @property
    def q_cards(self) -> int:
        # number of cards inside a drawer

        #if data is local
        cards_path = Path(self.path) / "images"
        return len(list(cards_path.glob('*.jpg')))

    def card_id(self, card_position):
        assert card_position <= self.q_cards
        return self.id + str(card_position).zfill(4)
    
    def get_card(self, card_position: int):
        assert card_position <= self.q_cards
        card_id = self.id + str(card_position).zfill(4)
        return Card(card_id,".")
    
class Card ( Drawer , Catalog ):
    def __init__(self , id_card : str, catalog_url : str):
        """ 
        Instancia un objeto Card que contiene los datos que permiten manipular cada Card de un catalogo
        
            ubicada en una Drawer.
           iriCatalogo: que es el iri del fichero json con los datos del catalogo donde se encuentra la Card
            iriCatalogo tiene 11 digitos, y es una variable str
            Funciona como un codigo de 11 digitos:
                nombre de la institucion: 4 digitos.g bnjm
                sala en que esta la coleccion: 3 digitos  scu
                tipo de coleccion: 3 digitos e.g. lyf
                tipo de catalogo: 2 digitos e.g. of
                iriCatalogo = 'bnjmsculyfof'

        """



        # check that id_card is correct
        assert len(id_card) == 19, "id_card shoud have 19 characters eg. 'bnjmsculyfof0010001'"

        self.id =id_card
        self.catalog_url = catalog_url
        self.catalog = Catalog(self.id[:12],self.catalog_url)
     
        #catalog source path
        self.local_path = Path(self.drawer.local_path) / self.id

        #if condition returns False, AssertionError is raised:
        # id_card identifies it uniquelly in the context of a catalog 

        #take card basic data pattern, drawer and number

        # pattern name
        # the pattern name gives additional context information
        self.pattern = id_card[:12]

        #drawer number
        self.drawer = int(id_card[12:15])

        # catalog
        self.catalog_name = self.id[:12]
        # drawer
        self.drawer = Drawer(self.id[:15],self.catalog_url)


        #card position inside the drawer
        self.position = int(id_card[15:19])

        #card paths 
        self.image_path = "/" + self.id[:12] + "/" + self.id[:15] + "/images/" + self.id + ".jpg"
        self.ocr_path =  "/" + self.id[:12] + "/" + self.id[:15] + "/" + self.id + ".txt"

        #card image file name
        self.image_name = self.id + ".jpg"
        self.image_name = Path(self.catalog_url) /self.id[:12] / self.id[:15] / "images" / self.image_name

        # card_image_ocr_text_filename
        self.image_ocr_text_filename = self.id + ".txt"
        self.image_ocr_text_filename = Path(self.catalog_url) / self.id[:12] / self.id[:15] / self.image_ocr_text_filename

    @property
    def ocr_text(self):
        try:
            with open(self.image_ocr_text_filename,"r", encoding="utf-8") as f:
                ocr_text = f.read()
                return ocr_text
        except(Exception) as error:
            print(error)
            return str(error)

    def get_url(self, scheme: str, netloc : str, path: str):
        return urlunparse([scheme, netloc, path,"","",""])

    def get_remote(self, scheme: str, netloc : str, path: str):
        url = urlunparse([scheme, netloc,path,"","",""])
        try:
            r = requests.get(url)
            r.encoding = "utf-8"
            return r
        except(Exception) as error:
            print(error)
            return 

    def open_web(self):
        webbrowser.open (self.catalog_url )