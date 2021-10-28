import pytest
from pathlib import Path
from files4libs.organizer import Organizer
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

def test_create_calendar_folder_of_pictures_from_source_folder():
    # get all pictures files from source considering as filter variables extension and keyword in file name

    # set folder_path 
    folder_path = "/home/urra/Pictures"
    # set extensions
    extensions = [".jpg", ".jpeg"]
    # set keyword
    keyword = "hayde"

    # create an organizer object to manipulate pictures
    o = Organizer(src_path= folder_path, extensions=extensions, keyword = keyword) 
    assert o.keyword == keyword



if __name__ == '__main__':
    pytest.main()