from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='plsnocrash',
    version='0.1.3',
    packages=['plsnocrash'],
    url='https://github.com/HenryWConklin/plsnocrash',
    license='',
    author='Henry Conklin',
    author_email='henrywconklin@gmail.com',
    description='Ever had your code crash after 10 hours of heavy computation because of a dumb mistake?',
    long_description=long_description,
    long_description_content_type="text/markdown",
    test_suite="test"
)
