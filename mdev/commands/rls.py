from mdev import io
from mdev.client import post, login, resource_exists, ResourceType
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError

config = get_config()


def rls(args):
    action_str = 'Enabling'
    if args.disable:
        action_str = 'Disabling'

    io.start('%s row level security on entity type %s' % (action_str, highlight(args.entity)))

    login(args)
    if not resource_exists(args.entity, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type %s doesn't exist" % args.entity)
    post(config.get('api', 'rls'), data={'id': args.entity,
                                         'rlsEnabled': not args.disable})
