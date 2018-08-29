from setuptools import setup

setup(
    name = 'mdev',
    version = '0.1.0',
    packages = ['mdev'],
    entry_points = {
        'console_scripts': [
            'mdev = mdev.__main__:main'
        ]
    }
)