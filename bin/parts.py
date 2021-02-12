import oyaml as yaml
import sys
from cloudmesh.common.util import readfile
import pandas as pd

order = ["vendor",
          "description",
          "count",
          "price",
          "total",
          "comment",
          "image"]

pd.options.display.float_format = '{:,.2f}'.format

try:
    file = sys.argv[1]
except:
    file = "README-parts-list.yml"

content = readfile(file)

content = yaml.safe_load(content)

for i in range(0,len(content)):
    content[i]


data = {}
for i in range(0,len(content)):
    description = content[i]["description"]
    url = content[i]["url"]
    content[i]["link"] = f"[{description}]({url})"
    data[i] = content[i]
    image_url = content[i]["image"]
    content[i]["image"] = f"![]({image_url})"

df = pd.DataFrame(
    data=data,
    index=["vendor",
           "description",
           "count",
           "price",
           "comment",
           "other",
           "url",
           "link",
           "image"]

).transpose()

df['description'] = df['link']


df["total"] = df["count"] * df["price"]
total = round(df["total"].sum(),2)
df = df.round(2)


df = df[order]

entry = {}
for a in order:
    entry[a] = ""


entry["total"] = " ======== "
df = df.append(entry, ignore_index=True)

entry["total"] = total
df = df.append(entry, ignore_index=True)

table = df.to_markdown()


print()
print (table)
print()
