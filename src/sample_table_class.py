from enum import IntEnum, auto
import functools
import json
import re
import utils


class TableType(IntEnum):
    SAMPLE = auto()

class BaseJsonDto:
    def __str__(self):
        return json.dumps(self.__dict__).replace(' ', '')

class BaseCell:
    def __init__(self, key_size=4, key=1):
        self.key_size = key_size
        self.key = key

class KeyCell(BaseCell):
    def __init__(self, key_size=4, page_id=1, key=1, *, page_size=4):
        self.key_size = key_size
        self.page_size = page_size
        self.key = key
        self.page_id = page_id

    def __str__(self):
        return str(self.key).rjust(self.key_size, ' ') + str(self.page_id).rjust(self.page_size, ' ')

class KeyValueCell(BaseCell):
    def __init__(self, flags=TableType.SAMPLE, key_size=4, value_size=128, key=1, data_record="{}", *, flag_size=1):
        self.key_size = key_size
        self.value_size = value_size
        self.flag_size = flag_size
        self.flags = int(flags.value)
        self.key = key
        self.data_record = data_record

    def __str__(self):
        return str(self.flags) + str(self.key).rjust(self.key_size, ' ') + str(self.data_record).rjust(self.value_size, ' ')

class Header:
    def __init__(self, pointer_start=128, pointer_size=8, item_count=0, key_size=4, prev_page="prev.page", post_page="post.page", page_max_string=65536):
        self.pointer_start = pointer_start
        self.pointer_size = pointer_size
        self.item_count = item_count
        self.key_size = key_size
        self.prev_page = prev_page
        self.post_page = post_page
        self.page_max_string = page_max_string

    def __str__(self):
        return json.dumps(self.__dict__).replace(' ', '').ljust(self.pointer_start, ' ')

class Page:
    def __init__(self, header=Header(), cells=[BaseCell()]):
        self.header = str(header)
        self._page_max_string = header.page_max_string
        self.cells = functools.reduce(lambda x, y: str(x)+str(y), cells[::-1])
        self.pointers = functools.reduce(lambda x, y: str(x).rjust(header.pointer_size, ' ')+str(y+int(str(x)[-header.pointer_size:])-header.page_max_string).rjust(header.pointer_size, ' '), (header.page_max_string-sum([int(i[1]) for i in c.__dict__.items() if "size" in i[0]]) for c in cells))

    def __str__(self):
        return self.header + self.pointers + self.cells.rjust(self._page_max_string - len(self.header) - len(self.pointers), ' ')

    def sort_pointer(self, key_index="id"):
        _header = json.loads(self.header)
        _pointer_size = int(_header["pointer_size"])
        _item_count = int(_header["item_count"])
        _key_size = int(_header["key_size"])
        _pointers = [int(self.pointers[i*_pointer_size:i*_pointer_size+_pointer_size]) for i in range(_item_count)]
        _dict = dict(zip([c for c in re.findall(r'(\d{,4}){', self.cells)], _pointers[::-1]))
        print(_dict)
        self.pointers = "".join((str(s[1]).rjust(_pointer_size, ' ') for s in sorted(_dict.items(), key=lambda x:x[0])))

class SampleTableDefinition(BaseJsonDto):
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age


if __name__ == '__main__':
    records = [
        SampleTableDefinition(id=2,name="secondooooooo",age=123),
        SampleTableDefinition(id=1,name="first",age=123),
        SampleTableDefinition(id=3,name="thirdooo",age=123),
    ]
    # print(records[0])
    # print(records[1])
    cells = [
        KeyValueCell(flags=TableType.SAMPLE, key_size=4, value_size=len(str(data)), key=data.id, data_record=str(data))
        for data in records
    ]
    # print([str(i) for i in cells])
    page = Page(
        header=Header(pointer_start=130, pointer_size=8, item_count=len(cells), key_size=4, prev_page="prev.page", post_page="post.page", page_max_string=300),
        cells=cells,
    )
    print(page)
    page.sort_pointer()
    print(page)
