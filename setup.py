from codecs import open
from setuptools import setup, find_packages

__version__ = None
with open('sgbackend/version.py') as f:
    exec(f.read())

setup(
    name='sendgrid-django',
    version=str(__version__),
    author='Yamil Asusta',
    author_email='yamil@sendgrid.com',
    url='https://github.com/elbuo8/sendgrid-django',
    packages=find_packages(),
    license='MIT',
    description='SendGrid Backend for Django',
    long_description=open('./README.rst', encoding='utf-8').read(),
    install_requires=["sendgrid==1.4.0"],
)
