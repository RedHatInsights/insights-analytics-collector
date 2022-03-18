import os
from setuptools import setup, find_packages

__version__ = '0.0.1'

# We use the README as the long_description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")


setup(
    name='insights-analytics-collector',
    version=__version__,
    url='http://github.com/slemrmartin/insights-analytics-collector/',
    author='Martin Slemr',
    author_email='mslemr@redhat.com',
    description='TODO',
    long_description= open(readme_path).read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='TODO',
    license='Apache',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django'],
    tests_require=['pytest'],
)
