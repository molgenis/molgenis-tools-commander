"""
Contains bare-bones definitions of System Entity Types of MOLGENIS.
"""
from typing import NamedTuple, Optional


class User(NamedTuple):
    id: str
    username: str


class Group(NamedTuple):
    id: str
    name: str


class Role(NamedTuple):
    id: str
    name: str
    label: str
    group: Optional[Group]


class RoleMembership(NamedTuple):
    id: str
    user: User
    role: Role
