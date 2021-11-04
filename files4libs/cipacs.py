#!C:/Program Files/python36/python.exe
# -*- coding: utf-8 -*-

# se activa cuando corre en windows
# !C:/python35/python.exe

"""
# Biblioteca de clases para el desarrollo de CIPACs
# Card Image Public Access Catalogs
# Catalogo Publico de imagenes de fichas de catalogos

# Version 20160711
# Version para windows y linux
# Esta version trabaja con jinja2

"""


import json
import os
import urllib.parse
import urllib.request
import urllib.error
import random
import cgitb
import tkinter
import requests
import webbrowser
import html
import time
# import pyqrcode

cgitb.enable ( display=1 , logdir="/log" )
##cgitb.enable(display=1, logdir="/var/www/html/log")

# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

__author__ = 'Pedro Urra'
__version__ = '0.1'
__license__ = 'UH'


class Cipac:
    configPath = "conf/cipacconfig.json"

    def __init__(self , iriBase=None):

        if not iriBase:
            self.iriBase = "http://localhost:81/"
        else:
            self.iriBase = iriBase + "/"
        try:
            r = requests.get ( self.iriBase + "conf/cipacconfig.json" )
            if r.ok:
                self.config = r.json ()
                self.ok = True
        except IOError as err:
            self.config = {}
            self.ok = False
            self.error = err


class Catalogo ( Cipac ):
    """
        :param iriCatalogo:iri con el camino al fichero json con la estructura del catalogo
    """

    def __init__(self , iriCatalogo , params=None):

        self.iriCatalogo = iriCatalogo
        self.iri = urllib.parse.urlsplit ( self.iriCatalogo )
        self.iriBase = self.iri.scheme + "://" + self.iri.netloc + "/"
        self.idCatalogo = self.iriCatalogo[ -17:-5 ]
        self.error = ""
        self.data = self.Data
        self.dicData = self.DicData
        self.dctype = "CatalogueOrIndex"
        try:
            r = requests.get ( urllib.parse.urljoin (
                self.iriBase , "conf/cipacconfig.json" ) )
            if r.ok:
                self.config = r.json ()
                self.ok = True
                r.close ()
        except IOError as err:
            self.config = {}
            self.ok = False
            self.error = err

        self.template = self.TemplateAssociated
        self.params = {"q": "*:*" ,
                       "wt": "json" ,
                       "start": 0 ,
                       "rows": 10 ,
                       "sort": "id asc" ,
                       "collection": self.idCatalogo}

        if len ( self.data ) > 0:
            self.qFichas = self.QFichas
            self.qGavetas = len ( self.data )
            self.pathCatalogo = self.iriBase + self.idCatalogo + "/"
            self.firstGaveta = int ( self.data[ 0 ][ 0 ] )
            self.lastGaveta = int ( self.data[ len ( self.data ) - 1 ][ 0 ] )
            self.siglaI = self.idCatalogo[ 0:4 ]
            self.siglaSala = self.idCatalogo[ 4:7 ]
            self.tipoColeccion = self.idCatalogo[ 7:10 ]
            self.tipoCatalogo = self.idCatalogo[ 10:2 ]
            self.ok = True
            self.api_key = ""

        else:
            self.qFichas = 0
            self.qGavetas = 0
            self.iri = urllib.parse.urlsplit ( self.iriCatalogo )
            self.iriBase = self.iri.scheme + "://" + self.iri.netloc + "/"
            self.pathCatalogo = self.iriBase + self.idCatalogo + "/"
            self.firstGaveta = 0
            self.lastGaveta = 0
            self.siglaI = ""
            self.siglaSala = ""
            self.tipoColeccion = ""
            self.tipoCatalogo = ""
            self.ok = False
            self.api_key = ""

        self.annotationCollection = json.dumps ( {"@context": "http://www.w3.org/ns/anno.jsonld" ,
                                                  "id": self.iriCatalogo ,
                                                  "type": "AnnotationCollection" ,
                                                  "label": self.config[ "idInstituciones" ][ self.siglaI ] + "." +
                                                           self.config[ "idCatalogos" ][ self.idCatalogo ] ,
                                                  "creator": self.config[ "idInstituciones" ][ self.siglaI ] ,
                                                  "total": self.qFichas ,
                                                  "first": self.pathCatalogo + self.idCatalogo + str (
                                                      self.firstGaveta ).zfill ( 3 ) ,
                                                  "last": self.pathCatalogo + self.idCatalogo + str (
                                                      self.lastGaveta ).zfill ( 3 )
                                                  }
                                                 )

    @property
    def Data(self):
        try:
            r = requests.get ( self.iriCatalogo )
            if r.ok:
                r.encoding = "utf-8"
                data = r.json ()
            else:
                self.error = r.status_code
                data = [ ]
            r.close ()
        except IOError as err:
            self.error = err
            data = [ ]
        return (data)

    @property
    def DicData(self):
        dicData = {}
        for i , cadenai , cadenaf , qfichas in self.data:
            dicData[ i ] = [ cadenai , cadenaf , qfichas ]
        return (dicData)

    @property
    def QFichas(self):
        qFichas = 0
        if len ( self.data ) == 0:
            return (qFichas)
        else:
            for i in self.data:
                qFichas += int ( i[ 3 ] )
            return (qFichas)

    @property
    def TemplateAssociated(self):
        try:
            r = requests.get ( urllib.parse.urljoin (
                self.iriBase , "templates/cipac.html" ) )
            if r.ok:
                r.encoding = "utf-8"
                template = r.text
                r.close ()
                return (template)
        except IOError as err:
            template = ""
            self.error = err
            return (None)

    def GetFicha(self , i , j):
        f = Ficha ( self.iriCatalogo , i , j )
        return (f)

    def OpenWebCatalog(self):
        webbrowser.open (
            self.iriBase + "cgi-bin/item.py?idficha=" + self.idCatalogo + "00100001" )

    def OpenWebFicha(self , i , j):
        f = Ficha ( self.iriCatalogo , i , j )
        webbrowser.open ( self.iriBase + "cgi-bin/item.py?idficha=" + f.idficha )

    def ListadoFichasCatalogo(self , inicio=0 , salto=1 , nombrefichero=""):
        try:
            with open ( nombrefichero , "w" , encoding="utf-8" ) as fout:

                for i in range ( self.qGavetas ):
                    g = Gaveta ( self.iriCatalogo , i + 1 )
                    g.ListadoFichasGaveta ( inicio , salto , str (
                        i + 1 ).zfill ( 3 ) + nombrefichero )
                return (True)
        except IOError as err:
            return (err)

    def ListadoCompleto(self):
        """
        Genera un listado por el orden de las gavetas de todas las fichas
        """
        for i in range ( self.qGavetas ):
            print ( self.idCatalogo + str ( i + 1 ).zfill ( 3 ) )
            g = Gaveta ( self.iriCatalogo , i )
            print ( g )
            for j in range ( g.qFichas ):
                f = g.GetFicha ( j )
                print ( f.ocr )

    @property
    def IndiceGavetasHtml(self):
        # genera una barra de navegacion de un catalogo en forma de lista no ordenada que usa las clases de bootstrap

        cadenaletras = ""
        cadenanumeros = ""

        for i , cadenai , cadenaf , q in self.data:
            cadgav = i.zfill ( 3 )
            enlaceacgi = "item.py?idficha=" + self.idCatalogo + \
                         i.zfill ( 3 ) + "0001" + "&api_key=" + self.api_key
            if cadenai == cadenaf:
                cadenaletras = cadenaletras + '<li><a href="./' + enlaceacgi + \
                               '" alt="' + cadgav + '"> ' + cadenai + ' </a></li>'

            else:
                cadenaletras = cadenaletras + '<li><a href="./' + enlaceacgi + \
                               '" alt="' + cadgav + '"> ' + cadenai + "-" + cadenaf + ' </a></li>'

        return ('<ul class="pagination pagination-lg pagination-centered">' + cadenaletras + "</ul>")

    def Dump(self , wc=False):
        # para todas las gavetas

        for fila in self.data:

            try:
                fichero = self.iriBase + self.idCatalogo + "/" + self.idCatalogo + \
                          fila[ 0 ].zfill ( 3 ) + "/" + self.idCatalogo + \
                          fila[ 0 ].zfill ( 3 ) + ".jsonld"
                with open ( fichero , "w" , encoding="utf-8" ) as fout:
                    # para todas las fichas de cada gaveta
                    for j in range ( int ( fila[ 3 ] ) ):

                        f = self.GetFicha ( int ( fila[ 0 ] ) , j + 1 )
                        if f.ok:

                            if wc and "worldcat.org" in f.ocr:
                                fout.write ( f.registroJson + "\n" )
                                # print(f.registroJson)

                                fout.write ( f.RegistroWorldcat + "\n" )

                    # print(f.RegistroWorldcat)
                    # else:
                    # print(f.registroJson)
                    ##                                print("No hay registro Worldcat enlazado")

                    return (True)

            except IOError as err:
                raise ValueError ( 'Error al abrir fichero %s' % fichero )
                return (False)


class Gaveta ( Catalogo ):
    def __init__(self , iriCatalogo , i=int () , params=None):
        ##        super().__init__( iriCatalogo =  iriCatalogo, params=params)

        self.iriCatalogo = iriCatalogo
        self.C = Catalogo ( self.iriCatalogo )
        self.data = self.C.data
        self.dicData = self.C.dicData

        if i >= self.C.firstGaveta and i <= self.C.lastGaveta:
            self.i = i
        elif i > self.C.lastGaveta:
            self.i = self.C.lastGaveta
        else:
            self.i = self.C.firstGaveta

        if len ( self.data ) > 0:
            self.noGaveta = str ( self.i )
            self.cadenai = self.dicData[ self.noGaveta ][ 0 ]
            self.cadenaf = self.dicData[ self.noGaveta ][ 1 ]
            self.qFichas = int ( self.dicData[ self.noGaveta ][ 2 ] )
            self.idGaveta = self.C.idCatalogo + self.noGaveta.zfill ( 3 )
            self.pathGaveta = self.C.pathCatalogo + self.idGaveta + "/"
            self.pathImagenesGaveta = self.pathGaveta + "images/"
            self.gavetai = self.C.firstGaveta
            self.gavetaf = self.C.lastGaveta
            self.gavetas = self.i + 1  # # gaveta siguiente
            self.gavetaa = self.i - 1  # # gaveta anterior
            if self.gavetas > self.gavetaf:
                self.gavetas = self.gavetaf
            if self.gavetaa < self.gavetai:
                self.gavetaa = self.gavetai
            self.ok = True
        else:
            self.noGaveta = ""
            self.noGavetaOriginal = ""
            self.cadenai = ""
            self.cadenaf = ""
            self.qFichas = 0

            self.idGaveta = ""
            self.pathGaveta = self.C.pathCatalogo + self.idGaveta + "/"
            self.pathImagenesGaveta = self.pathGaveta + "images/"
            self.gavetai = 0
            self.gavetaf = 0
            self.gavetas = 0
            self.gavetaa = 0
            if self.gavetas > self.gavetaf:
                self.gavetas = 0
            if self.gavetaa < self.gavetai:
                self.gavetaa = 0
            self.ok = False

    def GetFicha(self , j):
        f = Ficha ( self.iriCatalogo , self.i , j )
        return (f)

    def ListadoFichasGaveta(self , inicio=0 , salto=1 , nombrefichero=""):

        try:
            with open ( nombrefichero , "w" , encoding="utf-8" ) as fout:
                print ( "Inicio de la gaveta:" + str ( self.i ) , file=fout )
                for j in range ( inicio , int ( self.qFichas ) , salto ):
                    r = requests.get ( self.pathGaveta +
                                       self.idGaveta + str ( j + 1 ).zfill ( 4 ) + ".txt" )

                    r.encoding = "utf-8"
                    print ( j + 1 , "/" , self.qFichas , file=fout )
                    print ( r.text.strip () , file=fout )
                    print ( " " , file=fout )
                    t = r.text.replace ( "\r\n" , " " )
                    while "  " in t:
                        t = t.replace ( "  " , " " )
                    print ( j + 1 , "/" , self.qFichas , "(" + str ( self.i ) + ")" )
                    print ( t )
                    print ( "...".center ( 70 ) )
                print ( "Fin de la gaveta:" + str ( self.i ) , file=fout )
                return (True)
        except IOError as err:
            return (False)


class MenuGavetas ():
    def __init__(self , iriBase , idCatalogo):
        self.iriBase = iriBase
        self.idCatalogo = idCatalogo
        self.error = ""
        self.menuGavetas = [ ]

        try:
            r = requests.get ( self.iriBase + "/" +
                               self.idCatalogo + "/" + self.idCatalogo + ".json" )
            if r.ok:
                r.encoding = "utf-8"
                self.modeloCatalogo = r.json ()
                r.close
        except IOError as err:
            self.modeloCatalogo = [ ]
            self.error = err
        for gaveta in self.modeloCatalogo:
            self.menuGavetas.append ( self.iriBase + "/cgi-bin/item.py?idicha=" +
                                      self.idCatalogo + str ( gaveta[ 0 ] ).zfill ( 3 ) + "0001" )
        return


class Ficha ( Gaveta , Catalogo ):
    def __init__(self , iriCatalogo , i=int () , j=int () , api_key=None):
        """ Construye un objeto ficha que contiene los datos que permiten manipular cada ficha de un catalogo
            ubicada en una gaveta.
           iriCatalogo: que es el iri del fichero json con los datos del catalogo donde se encuentra la ficha
            iriCatalogo tiene 11 digitos, y es una variable str
            Funciona como un codigo de 11 digitos:
                nombre de la institucion: 4 digitos.g bnjm
                sala en que esta la coleccion: 3 digitos  scu
                tipo de coleccion: 3 digitos e.g. lyf
                tipo de catalogo: 2 digitos e.g. of
                iriCatalogo = 'bnjmsculyfof'

        """
        ## Manejo de excepciones
        ##        if len(iriCatalogo) != 11:
        ##            raise Exception('El iiri del catalogo debe ser de 11 digitos')

        if api_key == None:
            self.api_key = ""
        else:
            self.api_key = api_key

        # Propiedades de la clase Ficha

        # Se ubica en una gaveta
        self.g = Gaveta ( iriCatalogo , i )
        self.i = int ( self.g.i )

        # Forma parte de un catalogo que tiene una identificacion y una cantidad de gavetas
        self.iriCatalogo = iriCatalogo
        self.idCatalogo = self.g.C.idCatalogo
        self.siglaI = self.idCatalogo[ 0:4 ]
        self.config = self.g.C.config
        self.titleInstitution = self.config[ "idInstituciones" ][ self.siglaI ]
        self.template = self.g.C.template
        self.registroJson = ""
        self.anotacionInventario = "Anotacion de inventario"

        # Se ubica dentro de un catalogo que tiene unos datos de estructura del mismo
        self.lista = self.g.data

        # Tiene una posicion que está en el rango de la cantidad de fichas que tiene esa gaveta
        if j > int ( self.g.qFichas ):
            self.j = int ( self.g.qFichas )
        else:
            self.j = j

        self.error = ""

        # Tiene un nombre que la identifica de manera unica en el catalogo
        self.idficha = self.g.C.idCatalogo + \
                       str ( self.i ).zfill ( 3 ) + str ( self.j ).zfill ( 4 )

        self.iriFicha = self.g.C.iriBase + "cgi-bin/item.py?idficha=" + \
                        self.idCatalogo + str ( self.i ).zfill ( 3 ) + str ( self.j ).zfill ( 4 )
        # self.qrCode = pyqrcode.create ( self.iriFicha )

        # Tiene un fichero de texto asosiado con el contenido de la ficha codificado en utf-8 y cuyo nombre es
        self.iriTextoFicha = self.g.pathGaveta + self.idficha + ".txt"

        # Tiene un fichero que representa la imagen digital de la ficha capturada a partir del original de la ficha y cuyo nombre es
        self.iriImagenFicha = self.g.C.iriBase + self.idCatalogo + "/" + self.idCatalogo + \
                              str ( self.i ).zfill ( 3 ) + "/images/" + self.idCatalogo + \
                              str ( self.i ).zfill ( 3 ) + str ( self.j ).zfill ( 4 ) + ".jpg"
        # http://localhost:8182/iiif/2/{identifier}/full/full/0/default.jpg

        ##        self.iriImagenIiif = "http://localhost:8182/iiif/2/"  +  'images%2Frembrandt' + str(self.j).zfill(3) + '.jpg' + "/info.json"

        self.iriImagenIiif = "http://localhost:8182/iiif/2/" + self.idCatalogo + '%2F' + self.idCatalogo + \
                             str ( self.i ).zfill ( 3 ) + '%2Fimages%2F' + self.idCatalogo + \
                             str ( self.i ).zfill ( 3 ) + str ( self.j ).zfill ( 4 ) + ".jpg" + "/info.json"
        self.extension = "jpg"
        self.ocr = ""

        # Describe una cosa del mundo real que puede ser un Libro o un Folleto que integra la coleccion que anota

        # Tiene un texto que representa la anotacion de la instancia de la obra que describe
        # self.ocr
        try:
            r = requests.get ( self.iriTextoFicha )
            if r.ok:
                r.encoding = "utf-8"
                self.ocr = r.text
                self.ok = True
            r.close
        except IOError as err:
            self.ocr = "No se pudo acceder al texto de la ficha"
            self.ok = False
            self.error = err

        # try:
        #     with open(self.iriTextoFicha.replace(self.g.C.iriBase,"../"),"r", encoding="utf-8") as fin:
        #         self.ocr = self.CleanText(fin.read().strip())

        #     fin.close()
        # except IOError as err:
        #     self.error = err
        #     self.ocr = str(err)
        #     if "Errno 2" in self.ocr:
        #         self.ocr = "Pendiente de digitalizar texto"

        # Tiene una identificacion unida dentro del catalogo

        # Tiene una fecha de incorporacion al catalogo digital

        # Tiene una institucion responsable del mantenimiento del catálogo

        # Identificacion en VIAF de la institucion responsable por la catalogacion
        self.iriAgent = "http://viaf.org/viaf/169775455/"

        # Determinar el URL al que apunta la ficha en Worldcat.org

        if "http://www.worldcat.org/oclc/".upper () in self.ocr.upper ():
            self.iriTarget = self.ocr[ self.ocr.find (
                "http://www.worldcat.org/oclc/" ):self.ocr.find ( "http://www.worldcat.org/oclc/" ) + 37 ]
            if self.iriTarget.endswith ( '"' ) or self.iriTarget.endswith ( "'" ):
                self.iriTarget = self.iriTarget[ 0:len ( self.iriTarget ) - 1 ]
            self.iriTarget = self.iriTarget + ".jsonld"
        elif "http://worldcat.org/entity/work/id/".upper () in self.ocr.upper ():
            self.iriTarget = self.ocr[ self.ocr.find (
                "http://worldcat.org/entity/work/id/" ):self.ocr.find ( "http://worldcat.org/entity/work/id/" ) + 44 ]
            if self.iriTarget.endswith ( '"' ) or self.iriTarget.endswith ( "'" ):
                self.iriTarget = self.iriTarget[ 0:len ( self.iriTarget ) - 1 ]
            self.iriTarget = self.iriTarget + ".jsonld"
        elif "http://experiment.worldcat.org/oclc/".upper () in self.ocr.upper ():
            self.iriTarget = self.ocr[ self.ocr.find (
                "http://experiment.worldcat.org/oclc/" ):self.ocr.find ( "http://experiment.worldcat.org/oclc/" ) + 45 ]
            if self.iriTarget.endswith ( '"' ) or self.iriTarget.endswith ( "'" ):
                self.iriTarget = self.iriTarget[ 0:len ( self.iriTarget ) - 1 ]
            self.iriTarget = self.iriTarget + ".jsonld"

        else:
            # self.iriTarget = "self.g.C.iriBase + "cgi-bin/item.py?idficha=" + self.idficha"
            self.iriTarget = ""

        if len ( self.lista ) > 0:

            # Tiene un grupo de datos de contexto relacionados con el catalogo

            self.gavetai = self.g.C.firstGaveta
            self.gavetaf = self.g.C.lastGaveta
            self.gavetas = self.i + 1  # # gaveta siguiente
            self.gavetaa = self.i - 1  # # gaveta anterior

            if self.gavetas > self.gavetaf:
                self.gavetas = self.gavetaf
            if self.gavetaa < self.gavetai:
                self.gavetaa = self.gavetai

            self.pathGaveta = self.g.C.iriBase + self.idCatalogo + \
                              "/" + self.idCatalogo + str ( self.i ).zfill ( 3 )
            self.pathImagenesGaveta = self.g.C.iriBase + self.idCatalogo + "/" + self.idCatalogo + str (
                self.i ).zfill (
                3 ) + "/" + "images"

            self.anchoficha = "520"
            self.altoficha = "320"

            # Cadena inicial y final de la gaveta donde se ubica la ficha heredados de la gaveta
            self.cadenai = self.g.cadenai
            self.cadenaf = self.g.cadenaf

            # Cantidad de fichas de la gaveta donde se unica la ficha heredada de la gaveta
            self.q = self.g.qFichas

            self.gaveta = str ( self.i ).zfill ( 3 )
            self.nombre = str ( self.j ).zfill ( 4 )
            self.inicial = str ( 1 ).zfill ( 4 )
            self.nombreficha = self.idCatalogo + self.gaveta + self.nombre
            self.nombreimagen = self.idCatalogo + \
                                self.gaveta + self.nombre + "." + self.extension
            self.nombrehtml = self.idCatalogo + self.gaveta + self.nombre + ".html"
            self.qgavetas = len ( self.lista )

            # Recoge la informacion almaceada en ficheros de texto de la ficha
            # OCR revisado almacenado en ficheros .txt
            # OCR en bruto almacenado en ficheros .ocr
            # Tripes n3 almacenados en ficheros del tipo .nt
            # Texto tecleado almacenado en fichero sin extension y con el nombre de la ficha

            context = {"@base": self.g.C.iriBase ,
                       "@vocab": "http://bibframe.org/vocab/" ,
                       "bf": "http://bibframe.org/vocab/"
                       }

            # self.registroJson = json.dumps({"@context": context,
            #                                 "@graph":[
            #                                 {"@id": self.g.C.iriBase + "cgi-bin/item.py?idficha=" + self.idficha,
            #                                 "@type":["bf:Annotation","bf:HeldItem"],
            #                                 "bf:annotationAssertedBy":{"@id":self.iriAgent},
            #                                 "bf:annotationBody": {"@id":self.iriTextoFicha},
            #                                 "bf:summary" : {"@value":self.ocr.strip()},
            #                                 "accessCondition":["Acceso local@es", "Local Access@en"],
            #                                 "heldBy": {"@id":self.iriAgent},
            #                                 "holdingFor":{"@id":self.iriTarget},
            #                                 "bf:annotates": {"@id":self.iriTarget}
            #                                  }
            #                                 ]
            #                                 })

            self.registroJson = json.dumps ( {
                "@context": "http://www.w3.org/ns/anno.jsonld" ,
                "id": self.g.C.iriBase + "cgi-bin/fichas.py?idficha=" + self.idficha ,
                "type": "Annotation" ,
                "motivation": "describing" ,
                "creator": {
                    "id": self.iriAgent ,
                    "type": "Organization"
                } ,
                "body": {
                    "id": self.iriTextoFicha ,
                    "type": "TextualBody" ,
                    "value": self.ocr.strip () ,
                    "format": "text/html"
                } ,
                "target": {
                    "id": self.iriImagenFicha ,
                    "type": "Image" ,
                    "format": "image/jpeg"
                }
            } )

            # Asignacion de las variables de contexto

            if self.j == 1:
                self.anterior = str ( self.j ).zfill ( 4 )
            else:
                self.anterior = str ( self.j - 1 ).zfill ( 4 )

            if self.q != 0:
                self.final = str ( self.q ).zfill ( 4 )
                if self.j < self.q:
                    self.siguiente = str ( self.j + 1 ).zfill ( 4 )
                else:
                    self.siguiente = str ( self.j ).zfill ( 4 )

                self.mitad = str ( self.q / 2 ).zfill ( 4 )
                self.cuarto = str ( self.q / 4 ).zfill ( 4 )
                self.trescuartos = str ( self.q * 3 / 4 ).zfill ( 4 )
                self.octavo = str ( self.q / 8 ).zfill ( 4 )
                self.tresoctavos = str ( self.q * 3 / 4 ).zfill ( 4 )

            else:
                self.q = self.j
                self.siguiente = self.nombre
                self.mitad = self.nombre
                self.cuarto = self.nombre
                self.trescuartos = self.nombre
            self.ok = True
        else:
            self.ok = False

    def __str__(self):

        return "Texto de la Ficha: {}".format ( self.ocr )

    def LeeFichero(self , iri):
        try:
            with requests.get ( iri ) as fin:
                data = fin.content
                return (data)
        except IOError as err:
            print ( 'File error: ' + str ( err ) )
            return ('File error: ' + str ( err ))

    def SalvaRegistro(self , registro , extension):
        try:
            # el directorio de trabajo es ../cgi-bin
            # al dar ../ me posiciono en el raiz del espacio web y de ahi me muevo

            ##            nombrefichero = self.pathGaveta + "/" + self.idficha + "." + extension
            nombrefichero = "../" + self.idCatalogo + "/" + self.idCatalogo + \
                            str ( self.i ).zfill ( 3 ) + "/" + self.idficha + "." + extension

            with open ( nombrefichero , "w" , encoding="utf-8" ) as fout:
                print ( registro , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def Idficha(self , i , j):
        return (self.idCatalogo + str ( i ).zfill ( 3 ) + str ( j ).zfill ( 4 ))

    def CreateLog(self , registro):
        cad = ""
        for clave in time.localtime ():
            cad += str ( clave )
        nombrefichero = "../" + self.idCatalogo + "/" + self.idCatalogo + \
                        str ( self.i ).zfill ( 3 ) + "/" + self.idficha + ".log"
        # context= {"oa": "http://www.w3.org/ns/anno.jsonld",
        # "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        # "dcterms" : "http://purl.org/dc/terms/",
        # "@base" : "http://www.bnjm.sld.cu/"}
        anotacion = json.dumps ( {"@context": {"oa": "http://www.w3.org/ns/anno.jsonld" ,
                                               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
                                               "dcterms": "http://purl.org/dc/terms/" ,
                                               "@base": "http://www.bnjm.sld.cu/"} ,
                                  "@id": urllib.parse.urljoin ( "http://www.bnjm.sld.cu/" ,
                                                                nombrefichero + "#" + cad ) ,
                                  "@type": "oa:Annotation" ,
                                  "dcterms:created": time.asctime () ,
                                  "oa:motivatedBy": "http://www.w3.org/ns/anno.jsonld:editing" ,
                                  "dcterms:creator": "iricreador" ,
                                  "oa:hasBody": registro ,
                                  "oa:hasTarget": self.iriFicha
                                  } )

        ##        anotacion = json.dumps(jsonld.compact(anotacion, context))

        ##        cad =""
        # for clave in time.localtime():
        ##            cad += str(clave)

        try:
            with open ( nombrefichero , "a" , encoding="utf-8" ) as fout:
                print ( anotacion , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    @property
    def RegistroWorldcat(self):
        registroWorldcat = {}
        if not self.iriTarget == "":
            try:
                # with requests.get(iriTarget) as fin:
                fin = requests.get ( self.iriTarget , timeout=10 )
                if fin.ok:
                    registroWorldcat = fin.json ()
                fin.close ()
                return (json.dumps ( registroWorldcat ))
            except IOError as err:
                registroWorldcat = 'File error: ' + str ( err )
                return (json.dumps ( registroWorldcat ))
        else:
            return (json.dumps ( registroWorldcat ))

    @property
    def Barracatalogocgi2(self):
        # genera una barra de navegacion de un catalogo en forma de lista no ordenada que usa las clases de bootstrap

        cadenaletras = ""
        cadenanumeros = ""

        for i , cadenai , cadenaf , q in self.lista:
            cadgav = str ( self.i ).zfill ( 3 )
            enlaceacgi = "item.py?idficha=" + self.Idficha ( i , 1 )
            if cadenai == cadenaf:
                cadenaletras = cadenaletras + '<li><a href="./' + enlaceacgi + \
                               '" alt="' + cadgav + '"> ' + cadenai + ' </a></li>'

            else:
                cadenaletras = cadenaletras + '<li><a href="./' + enlaceacgi + \
                               '" alt="' + cadgav + '"> ' + cadenai + "-" + cadenaf + ' </a></li>'

        return (
                '<div style="height: 0.933333px;" aria-expanded="false" class="navbar-collapse collapse" id="bs-example-navbar-collapse-1"><div class="collapse navbar-collapse" id="barraGavetasColapsada" role="navigation">' + '<div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">' + '<ul class="pagination  pagination-centered">' + cadenaletras + "</ul></div></div></div>")
        # return ('<div class="collapse navbar-collapse" id="barraGavetasColapsada">' +  cadenaletras + "</div>" )

    @property
    def Barracatalogocgi3(self):
        # devuelve una lista que contiene las cadenas HTML
        # con el menu de gavetas usando bottstrap para su presentacion

        menuGaveta = [ ]

        cadenanumeros = ""
        cadena = ""

        for i , cadenai , cadenaf , q in self.lista:
            cadgav = str ( self.i ).zfill ( 3 )
            enlaceacgi = "../cgi-bin/item.py?idficha=" + \
                         self.Idficha ( i , 1 ) + '&api_key=' + self.api_key
            if cadenai == cadenaf:
                menuGaveta.append ( '<li><a href="' + enlaceacgi +
                                    '" alt="' + cadgav + '"> ' + cadenai + ' </a></li>' )
            else:
                menuGaveta.append ( '<li><a href="' + enlaceacgi + '" alt="' +
                                    cadgav + '"> ' + cadenai + "-" + cadenaf + ' </a></li>' )
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

        return (cadena)

    @property
    def Barracatalogocgi4(self):
        # devuelve una lista que contiene las cadenas HTML con el menu de gavetas

        menuGaveta = [ ]

        cadenanumeros = ""
        cadena = ""

        for i , cadenai , cadenaf in self.lista:
            cadgav = str ( self.i ).zfill ( 3 )
            enlaceacgi = "item.py?idficha=" + self.Idficha ( i , 1 )
            if cadenai == cadenaf:
                menuGaveta.append ( '<li><a href="./' + enlaceacgi +
                                    '" alt="' + cadgav + '"> ' + cadenai + ' </a></li>' )
            else:
                menuGaveta.append ( '<li><a href="./' + enlaceacgi + '" alt="' +
                                    cadgav + '"> ' + cadenai + "-" + cadenaf + ' </a></li>' )

        abc = [ 'A' , 'B' , 'C' , 'D' , 'E' , 'F' , 'G' , 'H' , 'I' , 'J' , 'K' , 'L' , 'M' ,
                'N' , 'Ñ' , 'O' , 'P' , 'Q' , 'R' , 'S' , 'T' , 'U' , 'V' , 'W' , 'X' , 'Y' , 'Z' ]

        for letra in abc:
            cadena += ' <div class="btn-group" ><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"> ' + \
                      letra + '<span class="caret"></span></button> <ul class="dropdown-menu" role="menu">'
            for linea in menuGaveta:
                if "> " + letra in linea or "-" + letra in linea:
                    cadena += linea

            cadena += '</ul></div>'
        cadena += '</div>'

        return (menuGaveta)

    @property
    def MenuEditarficha(self):
        # Menu de acciones con la ficha
        """


        :return:
        """
        cad = '<a href=' + self.g.C.iriBase + 'cgi-bin/item.py?' + 'idficha=' + self.NombreRandom (
            True ) + '&aleatoria=True' + '"> Aleatoria </a>'
        cad = '<li><a  href=' + self.g.C.iriBase + 'cgi-bin/item.py?' + \
              'idficha=' + self.nombreficha + '&editar=True' + '"> Editar </a></li>'
        cad += '<li><a  href=' + self.g.C.iriBase + 'cgi-bin/item.py?' + \
               'idficha=' + self.nombreficha + '&editar=True' + '"> OCR </a></li>'

        cad += '<li><a  href=""> Anotar </a></li>'
        cad += '<li><a  href=""> Anexar </a></li>'

        return ('<ul class="nav nav-tabs nav-justified" role="tablist">' + cad + '</ul>')

    @property
    def MenuServiciosficha(self):
        # Menu de acciones con la ficha
        """


        :return:
        """

        cad = '<li><a  href=' + self.g.C.iriBase + 'cgi-bin/item.py?' + 'idficha=' + \
              self.nombreficha + '&solicitar=True' + '"> Solicitar </a></li>'
        cad += '<li><a  href=' + self.g.C.iriBase + 'cgi-bin/item.py?' + \
               'idficha=' + self.nombreficha + '&editar=True' + '"> Editar </a></li>'

        return ('<ul class="nav nav-tabs nav-justified" role="tablist">' + cad + '</ul>')

    def NombreRandom(self , total):
        # genera un nombre de ficha aleatoria dentro del conjunto de fichas del catalogo
        # a nivel de cada gaveta o de el catalogo completo
        # si la variable total es verdadera se mueve en la totalidad
        # si es falsa solo dentro de una gaveta

        if total:
            i = random.randint ( self.g.C.firstGaveta , self.g.C.lastGaveta )
        else:
            i = int ( self.i )

        q = int ( self.g.dicData[ str ( i ) ][ 2 ] )
        j = random.randint ( 1 , q )
        return (self.idCatalogo + str ( i ).zfill ( 3 ) + str ( j ).zfill ( 4 ))

    def Htmlfichacgi(self):
        return (
                '<img class="img-rounded" src="' + self.iriImagenFicha + '"  width="' + self.anchoficha + '" height="' + self.altoficha + '"  alt="' + self.Descripcion () + '"/>')

    def Biniciocgi(self):

        if self.j == 1:
            fichaanterior = "item.py?idficha=" + \
                            self.Idficha ( self.i , self.j ) + "&api_key=" + self.api_key
        else:
            fichaanterior = "item.py?idficha=" + \
                            self.Idficha ( self.i , self.j - 1 ) + "&api_key=" + self.api_key
        if self.j < self.q:
            fichasiguiente = "item.py?idficha=" + \
                             self.Idficha ( self.i , self.j + 1 ) + "&api_key=" + self.api_key
        else:
            fichasiguiente = "item.py?idficha=" + \
                             self.Idficha ( self.i , self.q ) + "&api_key=" + self.api_key

        self.cuarto = "item.py?idficha=" + \
                      self.Idficha ( self.i , (int ( self.q / 4 )) ) + \
                      "&api_key=" + self.api_key

        self.octavo = "item.py?idficha=" + \
                      self.Idficha ( self.i , (int ( self.q / 8 )) ) + \
                      "&api_key=" + self.api_key

        self.tresoctavos = "item.py?idficha=" + \
                           self.Idficha ( self.i , (int ( self.q * 3 / 8 )) ) + \
                           "&api_key=" + self.api_key

        self.mitad = "item.py?idficha=" + \
                     self.Idficha ( self.i , (int ( self.q / 2 )) ) + \
                     "&api_key=" + self.api_key

        self.cincooctavos = "item.py?idficha=" + \
                            self.Idficha ( self.i , (int ( self.q * 5 / 8 )) ) + \
                            "&api_key=" + self.api_key

        self.trescuartos = "item.py?idficha=" + \
                           self.Idficha ( self.i , (int ( self.q * 3 / 4 )) ) + \
                           "&api_key=" + self.api_key

        self.sieteoctavos = "item.py?idficha=" + \
                            self.Idficha ( self.i , (int ( self.q * 7 / 8 )) ) + \
                            "&api_key=" + self.api_key

        return (
                '<nav id="binicio"><a class= "btn btn-mini btn-default" href="./' + fichaanterior + '">Anterior</a><STRONG>' + " -- " + self.nombre + "/" + self.final + " -- " + '</STRONG> <a class= "btn btn-mini btn-default" href="' + fichasiguiente + '">Siguiente</a> </nav>')

    def Bbinariacgi(self):
        inicio = "item.py?idficha=" + \
                 self.Idficha ( self.i , 1 ) + "&api_key=" + self.api_key
        final = "item.py?idficha=" + \
                self.Idficha ( self.i , self.q ) + "&api_key=" + self.api_key
        return (
                '<nav id="bbinaria"><a class= "btn btn-mini btn-default" href="' + inicio + '"><<</a> ' + '<a class = "btn btn-mini btn-default" href="' + self.octavo + '"> (1/8) </a> ' + '<a class = "btn btn-mini btn-default" href="' + self.cuarto + '"> (1/4) </a> ' + '<a class = "btn btn-mini btn-default"  href="' + self.tresoctavos + '"> (3/8) </a> ' + '<a class = "btn btn-mini btn-default"  href="' + self.mitad + '"> (1/2) </a>' + '<a class = "btn btn-mini btn-default" href="' + self.cincooctavos + '"> (5/8) </a> ' + '<a class = "btn btn-mini btn-default" href="' + self.trescuartos + '"> (3/4) </a>' + '<a class = "btn btn-mini btn-default"  href="' + self.sieteoctavos + '"> (7/8) </a> ' + '<a class = "btn btn-mini btn-default" href="' + final + '">>></A > ' + "</nav>")

    def Bdialcgi(self):
        # Barra para moverse dentro de la gaveta de fichas

        escala = [ -100 , -75 , -50 , -25 , -20 , -15 , -
        10 , -5 , 0 , 5 , 10 , 15 , 20 , 25 , 50 , 75 , 100 ]
        cadena = ""
        enlace = ""

        for valor in escala:
            if valor + self.j > 0 and valor + self.j <= self.q:  # si esta en el rango del total de fichas
                enlace = "item.py?idficha=" + \
                         self.Idficha ( self.i , valor + self.j ) + \
                         "&api_key=" + self.api_key
            elif valor + self.j < 0:  # si tiene un valor negativo se queda en la primera ficha
                enlace = "item.py?idficha=" + \
                         self.Idficha ( self.i , 1 ) + "&api_key=" + self.api_key
            elif valor + self.j > self.q:  # si supera el total de fichas se queda en la ultima
                enlace = "item.py?idficha=" + \
                         self.Idficha ( self.i , self.q ) + "&api_key=" + self.api_key
            if valor == 0:
                if self.cadenai == self.cadenaf:
                    cadena = cadena + \
                             "<STRONG>(" + self.cadenai + "-" + \
                             self.gaveta + ")</STRONG>" + ' </a>'
                else:
                    cadena = cadena + \
                             "<STRONG>(" + self.cadenai + "/" + self.cadenaf + \
                             "-" + self.gaveta + ")</STRONG>" + ' </a>'
            elif valor > 0:
                cadena = cadena + '<a class= "link" href="' + \
                         enlace + '"> +' + str ( valor ) + ' </a>'

            elif valor < 0:
                cadena = cadena + '<a class= "link" href="' + \
                         enlace + '"> ' + str ( valor ) + ' </a>'

        cadena = '<nav id = "bdial">' + cadena + "</nav>"
        return (cadena)

    def Descripcion(self):

        gaveta = "GAV-" + str ( self.i )
        if self.cadenai != None and self.cadenaf != None:
            desdehasta = " (" + self.cadenai + "-" + self.cadenaf + ")"
        else:
            desdehasta = ""
        if self.idCatalogo != None:
            cadena = "Institucion:" + self.idCatalogo[ 0:4 ].upper () + " Sala:" + self.idCatalogo[
                                                                                   10:12 ].upper ()
        else:
            cadena = ""

        self.descripcion = cadena + " " + gaveta + desdehasta + " Ficha:" + self.nombre
        return (self.descripcion)

    def AddText(self , text):
        # adiciona un texto a la ficha. Si existe un texto lo adiciona al final
        try:
            with open ( self.iriTextoFicha.replace ( self.g.C.iriBase , "../" ) , "a" , encoding="utf-8" ) as fout:
                print ( text , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def ReplaceString(self , old , new):
        # Remplaza una cadena de texto(old) por otra (new) dentro del texto de la ficha
        try:
            with open ( self.iriTextoFicha.replace ( self.g.C.iriBase , "../" ) , "w" , encoding="utf-8" ) as fout:
                print ( self.ocr.replace ( old , new ) , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def CreateText(self , text):
        # Crea un nuevo registro con el texto asociado a la ficha
        try:
            with open ( self.iriTextoFicha.replace ( self.g.C.iriBase , "../" ) , "w" , encoding="utf-8" ) as fout:
                print ( text , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def UpdateText(self , text):
        # Actualiza el texto con un nuevo texto
        try:
            with open ( self.iriTextoFicha.replace ( self.g.C.iriBase , "../" ) , "w" , encoding="utf-8" ) as fout:
                print ( text , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def DeleteText(self):
        # Borra el contenido del fichero de texto asociado a la ficha
        try:
            with open ( self.iriTextoFicha.replace ( self.g.C.iriBase , "../" ) , "w" , encoding="utf-8" ) as fout:
                print ( "" , file=fout )
                return (True)
        except IOError as err:
            self.error = err
            return (False)

    def CleanText(self , text):
        # Limpia el texto de retornos
        cad = ""
        t = text.split ()
        for palabra in t:
            cad += palabra + " "
        return (cad)


class WorldCatWorkJsonld ():
    def __init__(self , oclcWorkNum):
        self.oclcWorkNum = oclcWorkNum
        self.oclcWorkIri = "http://www.worldcat.org/entity/work/id/"
        try:
            r = requests.get ( self.oclcWorkIri + oclcWorkNum + ".jsonld" )
            if r.ok:
                error = ""
                r.encoding = "utf-8"
                data = r.json ()
            else:
                error = r.status_code
                data = [ ]
            r.close ()
        except IOError as err:
            error = err
            data = [ ]
        self.data = data
        self.error = error
        return


class WorldCatInstanceJsonld ():
    def __init__(self , oclcInstanceNum):
        self.oclcInstanceNum = oclcInstanceNum
        self.oclcInstanceIri = "http://www.worldcat.org/oclc/"
        try:
            r = requests.get ( self.oclcInstanceIri +
                               oclcInstanceNum + ".jsonld" )
            if r.ok:
                error = ""
                r.encoding = "utf-8"
                data = r.json ()
            else:
                error = r.status_code
                data = [ ]
            r.close ()
        except IOError as err:
            error = err
            data = [ ]

        self.data = data
        self.error = error
        return


class SolrClient ():
    def __init__(self , url=None , collection=None , params=None):

        if params == None:
            params = {"q": "*:*" , "wt": "json" , "start": 0 , "rows": 10}

        if not url:
            url = "http://localhost:8983/solr/select?"
        if collection and collection != "":
            url = url.replace ( "/select" , "/" + collection + "/select" )

        self.params = params
        self.url = url
        self.collection = collection

        try:
            r = requests.get ( url=self.url , params=self.params )
            if r.ok:
                if r.json ()[ "response" ][ 'numFound' ] % self.params[ "rows" ] == 0:
                    self.qPags = r.json ()[
                                     "response" ][ 'numFound' ] / self.params[ "rows" ]
                elif r.json ()[ "response" ][ 'numFound' ] % self.params[ "rows" ] > 0:
                    self.qPags = int (
                        r.json ()[ "response" ][ 'numFound' ] / self.params[ "rows" ] ) + 1

                numberPage = self.GetPageNumber ( params[ "start" ] , r.json ()[
                    "response" ][ 'numFound' ] , params[ "rows" ] )

                firstPage = 0
                lastPage = self.GetPageNumber ( r.json ()[ "response" ][ 'numFound' ] , r.json ()[
                    "response" ][ 'numFound' ] , params[ "rows" ] )
                actualPage = self.GetPageNumber ( params[ "start" ] , r.json ()[
                    "response" ][ 'numFound' ] , params[ "rows" ] )
                prevPage = actualPage - 1
                if prevPage <= 0:
                    prevPage = 0
                nextPage = actualPage + 1
                if nextPage > lastPage:
                    nextPage = lastPage
                self.ok = True
                self.numFound = r.json ()[ "response" ][ 'numFound' ]
                self.highlighting = r.json ()[ 'highlighting' ]
                self.docs = r.json ()[ "response" ][ 'docs' ]

                self.pagination = [
                    {"puntero": self.GetStartPage (
                        firstPage , self.params[ "rows" ] ) , "etiqueta": "Inicio" , "cadbusca": self.params[ "q" ]} ,
                    {"puntero": self.GetStartPage (
                        prevPage , self.params[ "rows" ] ) , "etiqueta": "Anterior" , "cadbusca": self.params[ "q" ]} ,
                    {"puntero": self.GetStartPage (
                        actualPage , self.params[ "rows" ] ) , "etiqueta": "Actual" , "cadbusca": self.params[ "q" ]} ,
                    {"puntero": self.GetStartPage (
                        nextPage , self.params[ "rows" ] ) , "etiqueta": "Siguiente" , "cadbusca": self.params[ "q" ]} ,
                    {"puntero": self.GetStartPage (
                        lastPage , self.params[ "rows" ] ) , "etiqueta": "Final" , "cadbusca": self.params[ "q" ]}
                ]
            else:
                self.ok = False
                self.numFound = 0
                self.highlighting = [ ]
                self.docs = [ ]
                self.qPags = 0
                self.pagination = {
                    "firstPage": 0 ,
                    "lastPage": 0 ,
                    "actualPage": 0 ,
                    "prevPage": 0 ,
                    "nextPage": 0
                }
                self.error = "Error en la busqueda"
            r.close ()
        except IOError as err:
            self.error = err
            self.ok = False

    def GetPageNumber(self , start , numFound , rows):

        p = int ( start / rows )

        if numFound % rows == 0 and numFound - start <= rows:
            p = p - 1

        return (p)

    def GetStartPage(self , p , rows):

        start = (p * rows)
        if start < 0:
            start = 0
        return (start)

    def GetPage(self , page , p=0):
        params = page[ "params" ]
        params[ "start" ] = self.GetStartPage ( p , page[ "rows" ] )
        return (self.Search ( self.url , params ))

    def ListRecords(self):

        i = self.params[ "start" ]
        lista = [ ]
        for registro in self.docs:
            i += 1

            lista.append ( [ i ,
                             self.numFound ,
                             registro[ "body" ] ,
                             self.IdFicha ( registro[ "id" ] ) ,
                             self.highlighting[ registro[ "id" ] ]
                             ]
                           )

        return (lista)

    def ListHighlighting(self):
        i = self.params[ "start" ]
        lista = [ ]
        for clave in self.highlighting:
            i += 1
            lista.append ( [ i , self.numFound , self.CleanText (
                self.highlighting[ clave ][ 0 ] ) , self.IdFicha ( clave ) ] )
        return (lista)

    def IdFicha(self , cadena):
        cadena = cadena[ -23: ]
        cadena = cadena.split ( "." )
        return (cadena[ 0 ])

    def Record(self , i):
        page = [ ]
        if self.params[ "start" ] <= i <= self.params[ "start" ] + self.params[ "rows" ] - 1:
            registro = page[ "docs" ][ i - self.params[ "start" ] ]
            return (str ( i ) + "/" + str ( self.numFound ) + "\n" + registro[
                "body" ] + '<a href="' + self.g.C.iriBase + registro[ "id" ][ -52: ].replace ( "\\" , "/" )) + '"></a>'
        else:
            print ( "No se encuentra en esta pagina" )
            return ("El registro no se encuentra en esta pagina")

    def CleanText(self , text):
        # Limpia el texto de retornos
        cad = ""
        t = html.escape ( text , quote=True )

        # t = split ()

        for palabra in t:
            cad += palabra + " "
        return (cad)


def LeeTexto(iriFichero):
    if not iriFichero:
        return ("")
    else:
        try:
            r = requests.get ( iriFichero )
            if r.ok:
                r.encoding = "utf-8"
                return (r.text)
            r.close
        except IOError as err:
            return (err)