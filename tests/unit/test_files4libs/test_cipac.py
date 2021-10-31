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
        self.card = cipac.Card(id_card = "bihcarccarco0020009",catalog_src_path="/home/urra/projects/pto/tests/data/bdc/ihc/catalogos/bihcarccarco")

    # test using self.card down here

    def test_card_id(self):
        assert self.card.id == "bihcarccarco0020009"
    
    def test_card_pattern(self):
        assert self.card.pattern == "bihcarccarco"
    
    def test_card_drawer(self):
        assert self.card.drawer == 2

    def test_card_position(self):
        #card position inside the drawer
        self.card.position = 9

    def test_card_image_name(self):
        assert self.card.image_name.stem  == 'bihcarccarco0020009'
          
    def test_card_image_name_uri(self):
        assert self.card.image_name.as_uri()
        #assert self.card.image_name_uri == 'file:///home/urra/projects/pto/tests/data/bdc/ihc/catalogos/bihcarccarco/bihcarccarco002/images/bihcarccarco0020009.jpg'

    def test_card_image_ocr_filenamename(self):
        assert self.card.image_ocr_text_filename.suffix == ".txt"

    def test_card_image_ocr_text_uri(self):
         assert self.card.image_ocr_text_filename.as_uri()
    
    def test_card_image_parent_path(self):
        assert self.card.image_name.parent.stem == "images"

    def test_card_image_ocr_text(self):
        assert "Habana" in self.card.ocr_text
