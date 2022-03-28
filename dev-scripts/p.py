p = 'C:\\Users\\venkata\\.cloudmesh\\cmburn\\distributions.yaml'
p = p.replace("\\","/").replace("C:","/c")
print(p)

from cloudmesh.common.util import path_expand
print(path_expand(p))

def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    with open(path_expand(filename), 'w') as outfile:
        outfile.write(content)

        outfile.truncate()

writefile(p,"hello")
