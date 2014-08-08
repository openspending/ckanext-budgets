import requests
import json
import six
import cgi
import cStringIO
import unicodecsv as csv
from contextlib import closing

from ckanext.budgets import exceptions

class BudgetDataPackage(object):
    """
    Budget data is stored in CSV files. This class wraps a CSV file to limit
    access to the file by providing headers and other helpful methods.
    """

    def __init__(self, specification, *args, **kwargs):
        """
        Initialialize the BudgetDataPackage object with the specification
        that should be used for processing budget data package resources
        """
        self.headers = None
        self.specification = self._get_specification(specification)

    def _get_specification(self, specification):
        """
        Read the specification provided. It can either be a url or a file
        location.
        """
        result = six.moves.urllib.parse.urlparse(specification)

        # If the specification has an http or an https scheme we can
        # retrieve it via an HTTP get request, else we try to open it
        # as a file.
        if result.scheme in ['http', 'https']:
            response = requests.get(specification)
            spec_json = response.json()
        else:
            with open(specification, 'r') as spec_file:
                spec_json = json.load(spec_file)

        return spec_json

    def _get_headers(self, resource):
        """
        Get CSV file headers from the provided resource.
        """

        # If the resource is a file we just open it up with the csv
        # reader (after being sure we're reading from the beginning
        # of the file
        if type(resource) == file:
            resource.seek(0)
            reader = csv.reader(resource)
        # If the resource is a basestring it is either a url or a file
        # location, so similarly to the specification mechanism we either
        # access it with an HTTP get request or by opening the file.
        elif isinstance(resource, basestring):
            result = six.moves.urllib.parse.urlparse(resource)
            if result.scheme in ['http', 'https']:
                with closing(requests.get(resource, stream=True)) as response:
                    # Headers are alway the first row of a CSV file
                    # so it's enought to just get the first line and
                    # hopefully save bandwidth
                    header_row = response.iter_lines().next()
            else:
                # It may seem weird to open up a csv file, read its header row
                # and then StringIO that into a new csv reader but this file
                # we want to close and we want the same interface for all
                with open(resource) as resource_file:
                    reader = csv.reader(resource_file)
                    header_row = reader.next()

            reader = csv.reader(cStringIO.StringIO(header_row))
        else:
            raise IOError('Resource type not supported')
        return reader.next()    

    def load(self, resource):
        """
        Load a resource into the BudgetDataPackage parser. The resource
        can either be an open file object, a url or a file path.
        """
        self.headers = self._get_headers(resource)

    @property
    def version(self):
        """
        Version of budget data package being used, according to the
        specification
        """
        return self.specification.get('version', None)

    @property
    def schema(self):
        """
        The generated budget data package schema for this resource.
        If the resource has any fields that do not conform to the
        provided specification this will raise a
        NotABudgetDataPackageException.
        """

        if self.headers is None:
            raise exceptions.NoResourceLoadedException(
                'Resource must be loaded to find schema')
        try:
            fields = self.specification.get('fields', {})
            parsed = {
                'primaryKey': 'id',
                'fields': [{
                        'name': header,
                        'type': fields[header]['type'],
                        'description': fields[header]['description']
                        } for header in self.headers]
                }
        except KeyError:
            raise exceptions.NotABudgetDataPackageException(
                'Includes other fields than the Budget Data Package fields')
        return parsed

    @property
    def granularity(self):
        """
        Granularity of the budget resource, either aggregated or
        transactional.
        """

        if self.headers is None:
            raise exceptions.NoResourceLoadedException(
                'Resource must be loaded to find granularity')

        return 'transactional' if 'date' in self.headers else 'aggregated'

    @property
    def budget_type(self):
        """
        Type of the budget resource, either expenditure or revenue.
        """

        if self.headers is None:
            raise exceptions.NoResourceLoadedException(
                'Resource must be loaded to find type')

        return 'expenditure' if 'admin' in self.headers else 'revenue'
