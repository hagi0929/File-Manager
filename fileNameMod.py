import os
import re
from glob import glob
import shutil
import mutagen


class Modifier:
    def __init__(self, path, extender='.mp3'):
        self.path = path
        self.fileList = []
        i = 0
        for element in glob(f'{path}/*{extender}'):
            i += 1
            title = element.split("\\")[-1][:-len(extender)]
            artistReg = re.match('^([^\[]*?\])', title)
            audioLoad = mutagen.File(element, easy=True)
            if artistReg:
                author = artistReg.group()[:-1]
                title = title[artistReg.end():]
            elif self.checkIfTagExists(audioLoad, 'artist'):
                author = audioLoad['artist'][0]
            else:
                author = None
            self.fileList.append([[element.split("\\")[-1][:-len(extender)], author, extender], [title[:].strip(), author, extender]])

    def __str__(self):
        print(f"path: {self.path}")
        for i, (before, after) in enumerate(self.fileList):
            if before != after:
                print(f'''
id: {i}
    {before}
    {after}
''')
        return ""

    def checkIfTagExists(self, file, tag):
        try:
            _ = file[tag]
            return True
        except:
            return False

    def replace(self, replacers, IDs=None, tagType=0):
        """

        :type tagType: int
        0 = title
        1 = author
        """
        if IDs is None:
            IDs = list(range(len(self.fileList)))
        for ID in IDs:
            _, after = self.fileList[ID]
            for From, To in replacers:
                after[tagType] = re.sub(From, To, after[tagType]).strip()
                print(after)

    def filterAll(self, keywords, tagType=0):
        filteredList = []
        for i, (before, after) in enumerate(self.fileList):
            if all(keyword in after[tagType] for keyword in keywords):
                filteredList.append(i)
        return filteredList

    def filterAny(self, keywords, tagType=0):
        filteredList = []
        for i, (before, after) in enumerate(self.fileList):
            if any(keyword in after[tagType] for keyword in keywords):
                filteredList.append(i)
        return filteredList

    def display(self, IDs = None):
        if IDs is None:
            IDs = list(range(len(self.fileList)))
        for ID in IDs:
            print(ID)
            print(self.fileList[ID][0])
            print(self.fileList[ID][1])
            print()

    def changeAuthor(self, IDs, author):
        for ID in IDs:
            self.fileList[ID][1][1] = author

    def applyChanges(self, newpathRcv):
        dup = 0
        dupList = []
        for before, after in self.fileList:
            if after[0]:
                print(before, after)
                oldPath = rf"{self.path}\{before[0]}{before[2]}"
                newPath = rf"{newpathRcv}\{after[0]}{after[2]}"
                if os.path.isfile(newPath):
                    conflictFile = mutagen.File(newPath, easy=True)
                    if self.checkIfTagExists(conflictFile, 'artist')\
                            and conflictFile['artist'][0]\
                            != after[1]:
                        newPath = rf"{newpathRcv}\{after[0]} {after[1]} {after[2]}"
                    else:
                        dup += 1
                        dupList.append([before, after])
                        continue
                shutil.copy(oldPath, newPath)
                audiofile = mutagen.File(newPath, easy=True)
                audiofile['artist'] = [after[1]]
                audiofile.save()

f = Modifier("C:\\fd marger\오디오\롤플")
f.replace([
    [r'[\(\[]*?[\)\]]', ''],
    ['[^A-Za-z0-9가-힣]', ' '],
    [' {2,}?', ' '],
    ['[0-9]{1,2}분 ?[0-9]{1,2}초', ' ']
])
f.display()
f.applyChanges(r'C:\fd marger\오디오\정리됨')