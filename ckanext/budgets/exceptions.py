class NotABudgetDataPackageException(Exception):
    '''
    The exception type that is raised when a resource file does not conform
    with the Budget Data Package specification.
    '''
    pass

class ResourceNotLoadedException(Exception):
    """
    The exception type that is raised when methods that rely on a resource
    being loaded are called, before the resource has been loaded.
    """
    pass
