

from setuptools import setup, find_packages

setup(
    name='bateau_back',
    version='0.0.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Flask',
        'flask-jwt-extended'
    ]
)
