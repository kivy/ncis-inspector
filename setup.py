"""
NCIS - Not a Clever Inspector Service - Kivy module
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ncis-inspector",
    version="0.1",
    description="Client/GUI for NCIS",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kivy/ncis-inspector',
    author='Kivy Team',
    author_email='kivy-dev@googlegroups.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'sseclient-py', 'kaki'],
    entry_points={
        'console_scripts': [
            'inspector=inspector.standalone:main'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/kivy/ncis-inspector/issues',
        'Source': 'https://github.com/kivy/ncis-inspector/',
    },
)
