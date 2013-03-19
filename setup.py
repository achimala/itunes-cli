from setuptools import setup, find_packages

setup(
    name="itunes",
    version="0.1",
    packages=find_packages(),
    install_requires=['appscript'],
    author="Anshu Chimala",
    author_email="me@achimala.com",
    description="Command line querying interface to control iTunes on Mac OS X",
    license="GPLv3",
    keywords="itunes",
    url="https://github.com/achimala/itunes-cli",
    entry_points={
        'console_scripts': [
            'itunes = itunes.itunes:main'
        ]
    }
)