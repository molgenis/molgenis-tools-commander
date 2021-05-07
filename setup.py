from setuptools import setup, find_packages

setup(
    name='molgenis-commander',
    version='1.10.3',
    packages=find_packages(),
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
    install_requires=[
        'attrs==20.3.0',
        'colorama==0.4.4',
        'halo==0.0.31',
        'Jinja2==2.11.3',
        'packaging==20.9',
        'parsy==1.3.0',
        'polling==0.3.1',
        'PyGithub==1.54.1',
        'questionary==1.9.0',
        'rainbow_logging_handler==2.2.2',
        'requests==2.21.0',
        'ruamel.yaml==0.17.4'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'molgenis-py-client>=2.3.0',
        'pytest',
        'testfixtures'
    ]
)
