from os.path import join, dirname

from setuptools import setup


def long_description():
    return open(join(dirname(__file__), 'README.rst')).read()


setup(
    description='just text',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    description_content_type='text/markdown'
)
