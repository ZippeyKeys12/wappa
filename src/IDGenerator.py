from __future__ import annotations

from typing import List


class IDGenerator:
    def __init__(self):
        self.IDs: List[str] = []

        self.usedIDs: List[str] = []
        self.unnameds: int = 0

    def append(self, ID):
        self.IDs.append(ID)

    def pop(self):
        self.IDs.pop()

    def generate_id(self, ID: str = ''):
        if ID == '':
            ret = '{}gen'.format(self.unnameds)

        else:
            ret = "_".join(self.IDs + [ID])

            num = 1
            nret = ret
            while nret in self.usedIDs:
                nret = ret + str(num)
                num += 1

            del nret

            self.usedIDs.append(ret)

        return ret
