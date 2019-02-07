import sys

from tests.integration import fake_loader, fake_home

sys.modules['mcmd.config.loader'] = fake_loader
sys.modules['mcmd.config.home'] = fake_home
