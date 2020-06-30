"""
Contains bare-bones definitions of System Entity Types of MOLGENIS.
"""
from typing import Optional

import attr


@attr.s(frozen=True, auto_attribs=True)
class User:
    id: str
    username: str


@attr.s(frozen=True, auto_attribs=True)
class Group:
    id: str
    name: str


@attr.s(frozen=True, auto_attribs=True)
class Role:
    id: str
    name: str
    label: str
    group: Optional[Group] = None


@attr.s(frozen=True, auto_attribs=True)
class RoleMembership:
    id: str
    user: User
    role: Role
