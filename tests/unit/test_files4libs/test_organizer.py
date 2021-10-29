
from datetime import datetime
import pytest
from pathlib import Path
from files4libs import organizer
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

class TestOrganizer():
    def setup(self):
        self.o = organizer.Organizer(src_path="/home/urra/projects/pto/tests/data", extensions = [".jpg",".JPG"])
        self.filename = Path("/home/urra/projects/pto/tests/data/E31006098.JPG")
        self.filenames = self.o.get_files()

    # test using self.organizer down here

    def test_get_files(self):
        files = self.o.get_files(keyword="hayd")
        assert self.o.ok == True

    def test_get_all_files(self):
        files = self.o.get_all_files()
        assert self.o.ok == True

    def test_get_exif_data(self):
        """
        returns the exif metadata of an image file    
        """
        exif_data = self.o.get_exif_data(self.filename)
        assert exif_data.get("model") == "E3100" and exif_data.get("make") == "NIKON"
        assert self.o.ok == True

    def test_get_exif_attribute(self):
        assert self.o.get_exif_attribute(self.o.get_exif_data(self.filename), tag="model") == "E3100"
        assert self.o.ok == True
    
    def test_read_files_exif_data(self):
        # :param: files:list
        exif_files_data = self.o.read_files_exif_data(self.filenames)
        for file in exif_files_data:
            assert "make" in file.keys() == True
        assert self.o.ok == True
    

class TestCollection():
    def setup(self):
        self.c = organizer.Collection("/home/urra/projects/pto/tests/data","bnjm")

    def test_create_calendar_folder(self):
        self.c.create_calendar_folder(self.c.name,datetime(2021,10,28))
        assert Path.joinpath(self.c.name,"2021/10/28").exists() == True

# if __name__ == '__main__':
#     pytest.main()