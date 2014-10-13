CKAN Budgets
============

A `CKAN <http://ckan.org/>`__ extension that improves handling of budget
data in CKAN. Central to the budget data handling are `budget data
packages <https://github.com/openspending/budget-data-package>`__.

When a CSV file is uploaded to CKAN and the CSV includes all of the
headers defined in the budget data package specification, the dataset is
automatically converted into a budget data package (i.e. it can be
exported as a budget data package). So automatically the budget data
distribution is standardised and becomes usable in the different tools
that support budget data packages.

Installation
------------

This CKAN extension can be installed via `pypi <http://pypi.python.org>`__ using ``pip``::

    pip install ckanext-budgets

If you have followed the `CKAN installation documentation <http://docs.ckan.org/en/latest/maintaining/installing/install-from-source.html>`__ remember to activate your CKAN environment (virtual environment) before installing the extension::

    . /usr/lib/ckan/default/bin/activate

Then add ``budgets`` to the list in ``ckan.plugins`` in your CKAN
configuration file. Restart your webserver and budget data is
automatically handled for you.

Configuration
-------------

-  **ckan.budgets.specification** - JSON schema file to describe the budget
   data package specification used.
-  **ckan.budgets.countries** - JSON object with country codes as keys and
   country names as values. Use this if you want to translate the country
   names into another language (default is English).
-  **ckan.budgets.currencies** - JSON object with currency code as keys and
   currency names as values. Use this if you want to translated the currency
   names into another language (default is English).
-  **ckan.budgets.statuses** - JSON object representing the different status
   of data with keys as *proposed*, *approved*, *adjusted* or *executed*) and
   with the English description of those statuses as values. Use this if you
   want to translate description into another language (status keys should
   remain intact).
-  **ckan.budgets.default.country** - Country code of a default country which
   is auto-selected.
-  **ckan.budgets.default.currency** - Currency code of a default currency
   which is auto-selected.

License
-------

Copyright (C) 2014 Open Knowledge Foundation

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see http://www.gnu.org/licenses/.
