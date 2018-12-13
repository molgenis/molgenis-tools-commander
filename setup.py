from setuptools import setup

setup(
    name='molgenis-commander',
    version='0.0.8',
    packages=['mcmd', 'mcmd.client', 'mcmd.commands', 'mcmd.config'],
    description='A command line interface for Molgenis',
    url='https://github.com/molgenis/molgenis-tools-commander',
    author='Tommy de Boer',
    author_email='tommydeboer4@gmail.com',
    license='GNU Lesser General Public License 3.0',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mcmd = mcmd.__main__:main'
        ]
    },
    install_requires=['requests', 'rainbow_logging_handler', 'PyInquirer', 'halo', 'polling', 'PyGithub',
                      'colorama==0.3.9']
)
