import json
import ckan.plugins.toolkit as toolkit
import ckan.model
import pylons
import dateutil.parser

from budgetdatapackage import BudgetDataPackage, BudgetResource

import logging
log = logging.getLogger(__name__)

class BudgetDataPackageController(toolkit.BaseController):

    def descriptor(self, id, resource_id):
        # Set context
        context = {'model': ckan.model, 'session': ckan.model.Session,
                   'user': pylons.c.user or pylons.c.author}

        # Get package
        package = toolkit.get_action('package_show')(
            context, {'id': id})

        # Get resource
        resource = toolkit.get_action('resource_show')(
            context, {'id': resource_id})

        if not resource.get('BudgetDataPackage', False):
            raise toolkit.ObjectNotFound(
                'No descriptor file for this resource')

        # If last modified hasn't been set we set it as time of creation
        last_modified = resource.get('last_modified')
        if last_modified is None:
            last_modified = resource['created']

        # Create the budget data package resource
        bdgt_resource = BudgetResource(
            name=resource['id'],
            schema=resource['schema'],
            url=resource['url'],
            currency=resource['currency'],
            fiscalYear=resource['year'],
            granularity=resource['granularity'],
            type=resource['type'],
            status=resource['status'],
            datePublished=dateutil.parser.parse(
                resource['created']).date().isoformat(),
            dateLastUpdated=dateutil.parser.parse(
                last_modified).date().isoformat(),
            location=resource['country'])

        # datapackage_uri and is_local are added but not needed
        # so we clean up our budget resource
        del bdgt_resource['datapackage_uri']
        del bdgt_resource['is_local']

        # Create the budget data package
        bdpkg = BudgetDataPackage(
            name=id,
            title=package['title'],
            description=package['notes'],
            resources=[bdgt_resource]
        )

        # Return the budget data package descriptor (json)
        toolkit.response.headers['Content-Type'] = 'application/json'
        return json.dumps(bdpkg)
