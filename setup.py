from setuptools import setup

setup(
    name='mdev',
    version='0.1.0',
    packages=['mdev', 'client'],
    entry_points={
        'console_scripts': [
            'mdev = mdev.__main__:main'
        ]
    }, install_requires=['requests', 'rainbow_logging_handler', 'PyInquirer', 'halo', 'polling', 'github']
)
