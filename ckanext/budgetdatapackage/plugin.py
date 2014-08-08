import ckan.plugins as plugins
import pylons.config as config

import datetime
import os.path

from ckanext.budgetdatapackage.lib.resource import BudgetDataPackage
from ckanext.budgetdatapackage import exceptions

import logging
log = logging.getLogger(__name__)

class BudgetDataPackagePlugin(plugins.SingletonPlugin):
    """Budget Data Package creator

    The plugin hooks into file upload/import and analyses uploaded/imported
    resources to see if they might be a budget data package. If a resource
    looks like a budget data package resource, the plugin allows the user to
    create a budget data package descriptor file (datapackage.json)
    """

    plugins.implements(plugins.IResourceModification)

    def __init__(self, *args, **kwargs):
        """
        Initialize the plugin. This creates a data object which holds a
        BudgetDataPackage parser which operates based on a specification
        which is either provided in the config via:
        ``ckan.budgets.specification`` or the included version.
        """

        specification = config.get(
            'ckan.budgets.specification',
            os.path.join(os.path.dirname(__file__), 'data', 'bdp.json'))
        self.data = BudgetDataPackage(specification)

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
        if resource.get('upload', ''):
            self.data.load(resource['upload'].file)
        else:
            self.data.load(resource['url'])

        # Try to grab a budget data package schema from the resource.
        # The schema only allows fields which are defined in the budget
        # data package specification. If a field is found that is not in
        # the specification this will return a NotABudgetDataPackageException
        # and in that case we can just return and ignore the resource
        try:
            resource['schema'] = self.data.schema
        except exceptions.NotABudgetDataPackageException:
            log.debug('Resource is not a Budget Data Package')
            return

        # If the schema fits, this can be exported as a budget data package
        # so we add the missing metadata fields to the resource.
        resource['datePublished'] = datetime.date.today().isoformat()
        resource['dateLastUpdated'] = datetime.date.today().isoformat()
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
