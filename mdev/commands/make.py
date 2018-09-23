from mdev import io
from mdev.client import login, post, get
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import lower_kebab, MdevError, upper_snake

config = get_config()


def make(args):
    io.start('Making user %s a member of role %s' % (highlight(args.user), highlight(args.role.upper())))
    login(args)

    group_name = _find_group(args.role)

    url = config.get('api', 'member') % group_name
    post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    io.debug('Fetching groups')
    groups = get(config.get('api', 'rest2') + 'sys_sec_Group?attrs=name')
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        raise MdevError('No group found for role %s' % upper_snake(role))

    return matches[max(matches, key=int)]
