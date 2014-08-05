import ckan.plugins as plugins


class BudgetDataPackagePlugin(plugins.SingletonPlugin):
    """Budget Data Package creator

    The plugin hooks into file upload/import and analyses uploaded/imported
    resources to see if they might be a budget data package. If a resource
    looks like a budget data package resource, the plugin allows the user to
    create a budget data package descriptor file (datapackage.json)
    """

    # We also need another interface for resource creation
    plugins.implements(plugins.IResourceUrlChange)

    def notify(self, resource):
        """
        This functions receives a notification of resource url changes.

        Changing a resource url means we have to first check if the dataset
        is a budget data package, then if so we re-parse the resource to
        update the resource metdata and see if it fully conforms with the
        budget data package specification. If it does not we throw a warning
        about not being able to include it in the budget data package. If it
        does, then we just update the resource.
        """

        pass

    def missing(self, resource):
        """
        This function is missing from CKAN.

        What this function should be is an extension of a currently
        non-existent interface that gets triggered when a resource is
        created.

        When triggered the resource which can either be uploaded or linked
        to will be downloaded and parsed to see if it possibly is a budget
        data package resource (checking if all required headers and any of
        the recommended headers exist in the csv). If it is then the dataset
        gets marked as a budget data package and the third step of the dataset
        creation process (additional information) will also ask about budget
        data package related metadata around both the overall dataset as well
        as each resource. That information will be saved as part of the
        dataset and from then on it will be possible to access the dataset
        as a budget data package.
        """

        pass
