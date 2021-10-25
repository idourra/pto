
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
        self.orgz = organizer.Organizer(src_path="~/Documents/00-Colección General/",extensions=[".pdf"],keyword="python")

    # test using self.organizer down here

    def test_scan_folder_tree_to_obtain_filenames(self):
        filenames = self.orgz.get_files()
        for file in filenames:
            assert file.name == "morena"

if __name__ == '__main__':
    pytest.main()