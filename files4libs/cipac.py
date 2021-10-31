# -*- coding: utf-8 -*-
"""
Python package to create and manage card images public access catalogs
"""
from pathlib import Path


class Cabinet():
    pass

class Drawer():
    def __init__(self , id_drawer : str, catalog_src_path : str):
        """
        """
        # check that id_drawer is correct
        assert len(id_drawer) == 15, "id_card shoud have 15 characters eg. 'bnjmsculyfof001'"
        
        self.id =id_drawer
        
        #if condition returns False, AssertionError is raised:
        # id_card identifies it uniquelly in the context of a catalog 

        #take card basic data pattern, drawer and number

        # pattern name
        # the pattern name gives additional context information
        self.pattern = id_drawer[:12]

        #drawer position inside the catalog cabinet
        self.position = int(id_drawer[12:15])


        #drawer path 
        self.path =  Path(catalog_src_path) / self.id
    
        #drawer_path_uri
        self.path_uri = self.path.as_uri()
    
    @property
    def q_cards(self) -> int:
        # number of cards inside a drawer
        cards_path = Path(self.path) / "images"
        return len(list(cards_path.glob('*.jpg')))

class Card ( Drawer , Cabinet ):
    def __init__(self , id_card : str, catalog_src_path : str):
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
        
        #catalog source path
        self.catalog_src_path = catalog_src_path

        #if condition returns False, AssertionError is raised:
        # id_card identifies it uniquelly in the context of a catalog 

        #take card basic data pattern, drawer and number

        # pattern name
        # the pattern name gives additional context information
        self.pattern = id_card[:12]

        #drawer number
        self.drawer = int(id_card[12:15])

        #card position inside the drawer
        self.position = int(id_card[15:19])

        #card_image name
        self.image_name = self.id + ".jpg"
        self.image_name = Path(catalog_src_path) / self.image_name[:15] / "images" /self.image_name

        # card_image_ocr_text_filename
        self.image_ocr_text_filename = self.id + ".txt"
        self.image_ocr_text_filename = Path(catalog_src_path) / self.id[:15] / self.image_ocr_text_filename

    @property
    def ocr_text(self):
        try:
            with open(self.image_ocr_text_filename,"r", encoding="utf-8") as f:
                ocr_text = f.read()
                return ocr_text
        except(Exception) as error:
            print(error)
            return str(error)
