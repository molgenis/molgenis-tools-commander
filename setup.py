from setuptools import setup

setup(
    name='molgenis-commander',
    version='1.1.0',
    packages=['mcmd', 'mcmd.client', 'mcmd.commands', 'mcmd.config', 'mcmd.utils'],
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
    python_requires='>3.7.0',
    install_requires=['requests==2.21.0', 'rainbow_logging_handler==2.2.2', 'PyInquirer==1.0.3', 'halo==0.0.22',
                      'polling==0.3.0', 'PyGithub==1.43.3', 'colorama==0.3.9', 'ruamel.yaml==0.15.81',
                      'molgenis-py-client==1.0.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
