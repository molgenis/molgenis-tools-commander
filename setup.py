from setuptools import setup

setup(
    name='mdev',
    version='0.0.4',
    packages=['mdev', 'mdev.client', 'mdev.commands', 'mdev.config'],
    description='The MOLGENIS command line development tool',
    url='https://github.com/molgenis/molgenis-tools-mdev',
    author='Tommy de Boer',
    author_email='tommydeboer4@gmail.com',
    license='GNU Lesser General Public License 3.0',
    entry_points={
        'console_scripts': [
            'mdev = mdev.__main__:main'
        ]
    },
    install_requires=['requests', 'rainbow_logging_handler', 'PyInquirer', 'halo', 'polling', 'PyGithub',
                      'colorama==0.3.9'],
)
