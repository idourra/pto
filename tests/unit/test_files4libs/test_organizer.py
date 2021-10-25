
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
        self.orgz = organizer.Organizer(src_path="/home/urra/projects/pto/tests/data/dated_images/2017/1/1/")

    # test using self.organizer down here

    def test_scan_folder_tree_to_obtain_filenames_with_filter(self):
        filenames = self.orgz.get_files()
        for file in filenames:
            assert file.suffix in self.orgz.extensions and "20170101" in file.name
    
    def test_get_image_exif_metadata(self):
        filename = Path("/home/urra/projects/pto/tests/data/dated_images/2017/1/1/20170101_194348.jpg")
        exif_data = self.orgz.get_exif_data(filename)
        assert exif_data.get("make") == "samsung"
        assert exif_data.get("model") == "SM-J500H"
        assert exif_data.get("datetime_original") == "2017:01:01 19:43:48"

    
        

if __name__ == '__main__':
    pytest.main()