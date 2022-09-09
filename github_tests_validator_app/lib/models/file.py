from typing import List

from dataclasses import dataclass, field


@dataclass
class File:

    NAME: str = ""
    ID: str = ""
    MIMETYPE: str = ""


@dataclass
class WorkSheetFile(File):
    HEADERS: str = ""


@dataclass
class GSheetFile(File):

    WORKSHEETS: List[WorkSheetFile] = field(default_factory=List[WorkSheetFile])


@dataclass
class GSheetDetailFile(File):

    HEADERS: List[str] = field(default_factory=List[str])
