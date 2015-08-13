# describe-tables

Given multiple SQL data definition files, read through each and export the table definitions in spreadsheets by schema for documentation.

Currently developed to use SQL DDL scripts exported from Toad for Oracle Professional 10.6.1.3. Other SQL DDL scripts may work, but have not been tested.


----
## Requirements

* [Python 3.3+](https://www.python.org/downloads/)
* [pip](https://pypi.python.org/pypi/pip)

Install the following Python packages via the following `pip` command line commands:

* [tqdm](https://github.com/tqdm/tqdm) (`pip install tqdm`)
* [xlsxwriter](https://pypi.python.org/pypi/XlsxWriter) (`pip install xlsxwriter`)


----
## Usage

1. Open Schema Browser (`Menu: Database > Schema Browser`); select one or more tables in browser. Right-click on selected table(s) and select `Create Script` menu option.

2. Set output options to:
  * One file per object
  * Include schema in filename

3. Export table definitions to a folder on the Desktop named `ddl`.

4. Run `main.py`. Files will be processed and will be stored in spreadsheets in `/ddl/Data Definitions` named for each schema encountered; definitions are grouped by table (listed in each header in column A). Key types are indicated in column B, and in the case of foreign keys, the key the foreign key references is indicated in the Description column. Column constraints, data types, and any default values are also indicated in the output.