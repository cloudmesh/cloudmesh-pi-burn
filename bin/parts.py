import oyaml as yaml
import sys
from cloudmesh.common.util import readfile
import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format

try:
    file = sys.argv[1]
except:
    file = "README-parts-list.yml"

content = readfile(file)

content = yaml.safe_load(content)

data = {}
for i in range(0,len(content)):
    data[i] = content[i]




df = pd.DataFrame(
    data=data,
    index=["vendor",
           "description",
           "count",
           "price",
           "comment",
           "other"]

).transpose()

df["total"] = df["count"] * df["price"]
total = df["total"].sum()




line = {}
for col in content[0]:
    if col == "total":
        line[col] = "========"
    else:
        line[col] = ""
total_line = dict(line)
total_line["total"] = total

print (line)


# df = df.append(line,ignore_index=True)
df = df.append(total_line,ignore_index=True)


print(df[["vendor",
          "description",
          "count",
          "price",
          "total",
          "comment",
          "other",
          "url"]].to_markdown())

