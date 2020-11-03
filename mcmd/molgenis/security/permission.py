from enum import Enum


class Permission(Enum):
    """Enum of security (and synonyms) that map to MOLGENIS security."""

    NONE = 'none'
    WRITEMETA = 'writemeta'
    READMETA = 'readmeta'
    EDIT = 'write'
    WRITE = 'write'
    VIEW = 'read'
    READ = 'read'
    COUNT = 'count'
