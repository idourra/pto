from datetime import datetime
import pytest
from pathlib import Path
from files4libs import cipac

"""

    GIVEN - what are the initial conditions for the test?
    WHEN - what is occurring that needs to be tested?
    THEN - what is the expected response?

    OR

    Arrange-Act-Assert model

    ARRANGE, or set up, the conditions for the test
    ACT by calling some function or method
    ASSERT that some end condition is true


"""

class TestCard():
    def setup(self):
        self.card = cipac.Card("bnjmsculyfof0010001","http://bnjm.sld.cu/bnjmsculyfof","/home/urra/tests/bnjmsculyfof")

    # test using self.card down here

    def test_card_id(self):
        assert self.card.id == "bnjmsculyfof0010001"

    def test_image_name(self):
        assert self.card.image_name == "/bnjmsculyfof/bnjmsculyfof001/images/bnjmsculyfof0010001.jpg"

    def test_catalog(self):
        assert self.card.catalog.q_drawers == 23
    
    def test_drawer(self):
        assert self.card.drawer.q_cards == 936

    def test_card_position(self):
        assert self.card.position == 1

    def test_card_drawer(self):
        assert self.card.drawer == 1

    def test_card_image_name(self):
        assert self.card.image_name.stem  == 'bihcarccarco0020009'
          
    def test_card_image_ocr_filenamename(self):
        assert self.card.image_ocr_text_filename.suffix == ".txt"

    def test_card_url_ocr(self):
         assert self.card.url_ocr.geturl() == 'http://bnjm.sld.cu/bnjmsculyfof/bnjmsculyfof001/bnjmsculyfof0010001.txt'
    
    def test_card_image_ocr_text(self):
        assert "patriotismo" in self.card.ocr_text

    
class TestDrawer():
    def setup(self):
        self.drawer = cipac.Drawer(card_id = "bihcarccarco002",catalog_src_path="/home/urra/projects/pto/tests/data/bdc/ihc/catalogos/bihcarccarco")
