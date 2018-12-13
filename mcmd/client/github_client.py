import re

from github import Github, UnknownObjectException

from mcmd.utils import McmdError

_MOLGENIS_FILES_URL = 'https://github.com/molgenis/molgenis/files/'

_github = None


class Attachment:
    def __init__(self, url):
        self.url = url
        self.id = self.parse_id(url)
        self.name = self.parse_file_name(url)

    def __repr__(self):
        return 'Attachment: %s' % self.id

    @staticmethod
    def parse_id(url):
        """Parses the file name, extension and the preceding identifier from the url."""
        return '/'.join(url.rsplit('/', 2)[-2:])

    @staticmethod
    def parse_file_name(url):
        """Parses the file name + extension from the url."""
        return '/'.join(url.rsplit('/', 1)[-1:])


def get_attachments(issue_num):
    validate_issue_number(issue_num)
    try:
        issue = _molgenis_repo().get_issue(int(issue_num))
    except UnknownObjectException:
        raise McmdError("Issue #%s doesn't exist" % issue_num)

    # GitHub has no API for downloading attachments so we get them from the issue description
    urls = _parse_attachment_urls(issue.body)
    return [Attachment(url.strip('()')) for url in urls]


def _parse_attachment_urls(issue_body):
    return re.findall('\((%s.*?)\)' % re.escape(_MOLGENIS_FILES_URL), issue_body)


def _molgenis_repo():
    global _github
    if not _github:
        _github = Github()

    return _github.get_organization('molgenis').get_repo('molgenis')


def validate_issue_number(issue_num):
    try:
        int(issue_num)
    except ValueError:
        raise McmdError('Not a valid issue number: %s' % issue_num)
