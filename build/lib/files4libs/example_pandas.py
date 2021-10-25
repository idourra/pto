#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import time
import commands as c

p = Path("/media/urra/PELICULAS Y ENTRETENIMIENTO/jpg_salva_calendar/dated_images/")
all_files = []
for i in p.rglob('*.*'):
    make = c.get_exif_attribute(i,"make")
    model = c.get_exif_attribute(i,"model")
    datetime = c.get_exif_attribute(i,"datetime_original")
    all_files.append((i.name, i.parent,make, model,datetime,time.ctime(i.stat().st_ctime)))

columns = ["File_Name", "Parent", "Make", "Model","Datetime","Created"]
df = pd.DataFrame.from_records(all_files, columns=columns)

print(df.head())
df.to_excel("jpg_images_all.xlsx")