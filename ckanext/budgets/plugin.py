import ckan.plugins as plugins
from ckan.logic.validators import int_validator

import datetime
import os.path
import json

from ckanext.budgets.lib.budgetdatapackage import BudgetDataPackage
from ckanext.budgets import exceptions

import logging
log = logging.getLogger(__name__)



class BudgetDataPackagePlugin(plugins.SingletonPlugin,
                              plugins.toolkit.DefaultDatasetForm):
    """Budget Data Package creator

    The plugin hooks into file upload/import and analyses uploaded/imported
    resources to see if they might be a budget data package. If a resource
    looks like a budget data package resource, the plugin allows the user to
    create a budget data package descriptor file (datapackage.json)
    """

    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    def __init__(self, *args, **kwargs):
        self.countries = {}
        self.currencies = {}
        self.statuses = {}
        self.data = None

    def configure(self, config):
        """
        Initialize the plugin. This creates a data object which holds a
        BudgetDataPackage parser which operates based on a specification
        which is either provided in the config via:
        ``ckan.budgets.specification`` or the included version.
        """

        specification = config.get(
            'ckan.budgets.specification',
            os.path.join(os.path.dirname(__file__),
                         'data', 'bdp', 'schema.json'))
        self.data = BudgetDataPackage(specification)

        countries_json = config.get(
            'ckan.budgets.countries',
            os.path.join(os.path.dirname(__file__),
                         'data', 'countries.json'))
        with open(countries_json) as country_list:
            self.countries = json.load(country_list)

        currencies_json = config.get(
            'ckan.budget.currencies',
            os.path.join(os.path.dirname(__file__),
                         'data', 'currencies.json'))
        with open(currencies_json) as currency_list:
            self.currencies = json.load(currency_list)

        statuses_json = config.get(
            'ckan.budget.statuses',
            os.path.join(os.path.dirname(__file__),
                         'data', 'bdp', 'statuses.json'))
        with open(statuses_json) as statuses_list:
            self.statuses = json.load(statuses_list)

    def update_config(self, config):
        pass
        plugins.toolkit.add_template_directory(
            config,
            os.path.join(os.path.dirname(__file__), 'form', 'templates'))


    def before_map(self, map_):
        controller = "ckanext.budgets.controllers:BudgetDataPackageController"
        map_.connect(
            "budgetdatapackage_descriptor",
            "/dataset/{id}/resource/{resource_id}/datapackage.json",
            controller=controller,
            action="descriptor")

        return map_

    def _sort_value(self, dictionary):
        return sorted(dictionary.iteritems(), key=lambda (key, value): value)

    def get_countries(self):
        countries = [{'value':code, 'text':name}
                     for (code, name) in self._sort_value(self.countries)]
        countries.insert(0, {'value':'', 'text':'-- Not applicable --'})
        return countries

    def get_currencies(self):
        currencies = [{'value':code, 'text':name}
                      for (code, name) in self._sort_value(self.currencies)]
        currencies.insert(0, {'value':'', 'text':'-- Not applicable --'})
        return currencies

    def get_statuses(self):
        statuses = [{'value':code, 'text':label}
                    for (code, label) in self._sort_value(self.statuses)]
        statuses.insert(0, {'value':'', 'text':'-- Not applicable --'})
        return statuses

    def get_helpers(self):
        return {
            'get_countries': self.get_countries,
            'get_currencies': self.get_currencies,
            'get_statuses': self.get_statuses
        }

    def country_validator(self, value, context):
        if value and value not in self.countries:
            raise plugins.toolkit.Invalid(
                'Country value ({0}) is invalid'.format(value))
        return value

    def currency_validator(self, value, context):
        if value and value not in self.currencies:
            raise plugins.toolkit.Invalid(
                'Currency value ({0}) is invalid'.format(value))
        return value

    def year_validator(self, value, context):
        value = int_validator(value, context)
        if value and value < 0:
            raise plugins.toolkit.Invalid(
                'Year value ({0}) is invalid'.format(value))
        return str(value)

    def status_validator(self, value, context):
        if value and value not in self.statuses:
            raise plugins.toolkit.Invalid(
                'Status value ({0}) is invalid'.format(value))
        return value

    def schema_validator(self, value, context):
        if value:
            return value

        return []

    @property
    def resource_schema_additions(self):
        return {
            'country': [
                self.country_validator
            ],
            'currency': [
                self.currency_validator
            ],
            'year': [
                self.year_validator
            ],
            'status': [
                self.status_validator
            ],
            'schema': [
                self.schema_validator
            ]
        }

    def create_package_schema(self):
        schema = super(BudgetDataPackagePlugin, self).create_package_schema()
        schema['resources'].update(self.resource_schema_additions)
        return schema

    def update_package_schema(self):
        schema = super(BudgetDataPackagePlugin, self).update_package_schema()
        schema['resources'].update(self.resource_schema_additions)
        return schema

    def show_package_schema(self):
        schema = super(BudgetDataPackagePlugin, self).show_package_schema()
        schema['resources'].update(self.resource_schema_additions)
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return ['dataset']

    def before_create(self, context, resource):
        """
        When triggered the resource which can either be uploaded or linked
        to will be parsed and analysed to see if it possibly is a budget
        data package resource (checking if all required headers and any of
        the recommended headers exist in the csv).

        The budget data package specific fields are then appended to the
        resource which makes it useful for export the dataset as a budget
        data package.
        """

        # If the resource is being uploaded we load the uploaded file
        # If not we load the provided url
        if resource.get('upload', '') == '':
            self.data.load(resource['url'])
        else:
            self.data.load(resource['upload'].file)

        # Try to grab a budget data package schema from the resource.
        # The schema only allows fields which are defined in the budget
        # data package specification. If a field is found that is not in
        # the specification this will return a NotABudgetDataPackageException
        # and in that case we can just return and ignore the resource
        try:
            resource['schema'] = self.data.schema
        except exceptions.NotABudgetDataPackageException:
            log.debug('Resource is not a Budget Data Package')
            resource['schema'] = []
            return

        # If the schema fits, this can be exported as a budget data package
        # so we add the missing metadata fields to the resource.
        resource['BudgetDataPackage'] = True
        resource['standard'] = self.data.version
        resource['granularity'] = self.data.granularity
        resource['type'] = self.data.budget_type

    def after_create(self, context, resource):
        pass

    def before_update(self, context, current, resource):
        pass

    def after_update(self, context, resource):
        pass

    def before_delete(self, context, resource, resources):
        pass

    def after_delete(self, context, resources):
        pass

    def before_show(self, resource):
        return resource
