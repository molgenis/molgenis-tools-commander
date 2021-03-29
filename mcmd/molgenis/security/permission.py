from enum import Enum


class Permission(Enum):
    """Enum of permissions (and synonyms) that map to MOLGENIS permissions."""

    NONE = 'none'
    WRITEMETA = 'writemeta'
    READMETA = 'readmeta'
    EDIT = 'write'
    WRITE = 'write'
    VIEW = 'read'
    READ = 'read'
    COUNT = 'count'
