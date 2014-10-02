from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-budgets',
    version=version,
    description="CKAN extension for creating and distributing budget data packages",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Tryggvi Bjorgvinsson',
    author_email='tryggvi.bjorgvinsson@okfn.org',
    url='',
    license='AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.budgets'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'unicodecsv',
	'requests',
	'six',
        'py-dateutil',
    ],
    entry_points='''
        [ckan.plugins]
        budgets=ckanext.budgets.plugin:BudgetDataPackagePlugin
    ''',
)
