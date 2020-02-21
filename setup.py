from setuptools import setup, find_packages

setup(
    name='molgenis-commander',
    version='1.7.0',
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
    install_requires=['requests==2.21.0', 'rainbow_logging_handler==2.2.2', 'halo==0.0.28',
                      'polling==0.3.0', 'PyGithub==1.43.3', 'colorama==0.3.9', 'ruamel.yaml==0.15.81',
                      'questionary==1.3.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'molgenis-py-client==1.0.0']
)
