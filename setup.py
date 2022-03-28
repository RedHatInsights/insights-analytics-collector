import os
from setuptools import setup, find_packages

__version__ = '0.0.1'

# We use the README as the long_description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")


setup(
    name='insights-analytics-collector',
    version=__version__,
    url='https://github.com/RedHatInsights/insights-analytics-collector/',
    author='Martin Slemr',
    author_email='mslemr@redhat.com',
    description='Collector Package for Insights for AAP',
    long_description=open(readme_path).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    license='Apache',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=False,
    install_requires=['django', 'requests'],
    tests_require=['pytest'],
)
