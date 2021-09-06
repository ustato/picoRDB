import os
import uuid


def generate_pagefile(dirname, *, text=""):
    filename = f"{dirname}/{str(uuid.uuid4())}.page"

    os.makedirs(dirname)
    with open(filename, "w") as f:
        f.write(text)

    return filename


if __name__ == '__main__':
    generate_pagefile("sample_dir")
