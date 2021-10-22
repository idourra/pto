#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import time

p = Path("/home/urra/Pictures/brasil")
all_files = []
for i in p.rglob('*.*'):
    all_files.append((i.name, i.parent, time.ctime(i.stat().st_ctime)))

columns = ["File_Name", "Parent", "Created"]
df = pd.DataFrame.from_records(all_files, columns=columns)

df.head()
