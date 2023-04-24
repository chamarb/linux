from enum import Enum
from glob import glob
from pathlib import Path
from typing import List
import os
import pwd
import datetime
import zipfile

from flask import(
    Flask, render_template, request, session, redirect, url_for, send_file
)

from markupsafe import escape

import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

SHADOW_FILE: Path = Path("/etc/passwd")
app = Flask(__name__)


@app.route("/files/<path:subpath>")
def hello_world(subpath):
    _files = show_files(f"/{escape(subpath)}")
    return [ff.parts[-1:][0] for ff in _files]


def show_files(
    root_fs: str,
) -> List[Path]:
    assert len(root_fs) > 0
    _files = glob(
        "{}/**/*".format(root_fs),
        recursive=True,
        include_hidden=True,
    )
    return [Path(f) for f in _files]


class Shells(Enum):
    BASH = "bash"
    SH = "sh"
    ZSH = "zsh"

    @classmethod
    def from_str(cls, shell: str):
        _shell = shell.split("/")[-1:][0].strip()
        if _shell == Shells.BASH.value:
            return Shells.BASH
        if _shell == Shells.ZSH.value:
            return Shells.ZSH
        else:
            return Shells.SH


class User:
    uid: int
    gid: int
    shell: Shells
    home: Path

    def __init__(
        self,
        name: str,
        uid: int,
        gid: int,
        home: Path,
        shell: Shells,
    ) -> None:
        self.name = name
        self.uid = uid
        self.gid = gid
        self.home = home
        self.shell = shell

    def __repr__(self) -> str:
        return f"""
            [{self.name}, {self.uid}, {self.gid}, {self.home}, {self.shell}]
            """


def parse_line(entry: str) -> User:
    assert len(entry) > 0
    entries = entry.split(":")
    assert len(entries) == 7
    return User(
        name=entries[0],
        uid=int(entries[2]),
        gid=int(entries[3]),
        home=Path(entries[5]),
        shell=Shells.from_str(entries[6]),
    )


def find_unix_users(user: str):
    """
    looks up users in the /etc/passwd file
    """
    assert SHADOW_FILE.exists()

    os_users = []

    with open(SHADOW_FILE) as input_file:
        while line := input_file.readline():
            os_users.append(parse_line(line))
    return os_users
#####################

