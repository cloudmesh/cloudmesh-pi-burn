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
          "other",
          "image"
          ]

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
total = df["total"].sum()



line = {}
for col in content[0]:
    if col == "total":
        line[col] = "========"
    else:
        line[col] = ""

total_line = dict(line)
total_line["total"] = total


# df = df.append(line,ignore_index=True)
df = df.append(total_line,ignore_index=True)


table = df[order].to_markdown().splitlines()


table[0] = "| " + " | ".join(order) + "|"

table[1] = len(order) * "| --- " + "|"


for i in range(0, len(table)):
    table[i] = " ".join(table[i].split())

table = "\n".join(table)

print()
print (table)
print()
