import os, re

src = '/root/funNLP-master/data'
for y, x, names in os.walk(src):
    # print(x)
    # print(y)
    for name in names:
        # print(name)
        if name.endswith('txt') or name.endswith('TXT'):
            with open(os.path.join(y, name), 'r') as f:
                try:
                    for line in f.readlines():
                        print(line)
                        line = line.splitlines()
                        for x in line:
                            if re.search(r'\d', x) is None:
                                print(x)
                except:
                    pass
        # print(os.path.join(y,name))
