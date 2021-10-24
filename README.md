# Files to Libraries
A Python library for organizing digital files into collections and catalogs of files

Python script to organize images in folders by year, month and day.
The script has as input a valid source path name and destination path name. 
If the original image file has exif metadata containing the date of creation, 
the file will be stored in the corresponding folder, eg. year/month/date/image_file. 
If the image file does not have date metadata, it is stored in a none_exif_date folder.

https://towardsdatascience.com/deep-dive-create-and-publish-your-first-python-library-f7f618719e14


### Installation
```
pip install files_to_libraries
```

### Get started
How to scan your file system with filters and organize files in cronological, alphabetical or thematic collectios:

```Python
from medium_multiply import Multiplication

# Instantiate a Multiplication object
multiplication = Multiplication(2)

# Call the multiply method
result = multiplication.multiply(5)
```