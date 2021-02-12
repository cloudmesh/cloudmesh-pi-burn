import oyaml as yaml
import sys
from cloudmesh.common.util import readfile
import pandas as pd

order = ["vendor",
          "description",
          "included",
          "price",
          "count",
          "total",
          "comment",
          "image"]

pd.options.display.float_format = '{:,.2f}'.format

file = sys.argv[1]  # yaml file

content = readfile(file)

content = yaml.safe_load(content)


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
           "included",
           "price",
           "comment",
           "other",
           "url",
           "link",
           "image",
           "count"]
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
