# Welcome to SQLSense

Parse SQL statements and extract metadata and lineage information from it.

This module is currently in **Planning** / **Pre-Aplha** Development State. It is currently being developed for ***PostgreSQL***. However, it is being developed such that it can be extended to other databases as well.

Currently sqlsense works only for Select Statements.

## Features

* Generate SQL Parse Tree.
* Extract *Datasets* and *Datafields* used in the SQL Statements.

## Features in Development

* Window Functions
* Data-Modifying Statements in WITH Clause

## Quick Start

```python
>>> from sqlsense.postgres.postgres_parser import PostgresParser
>>> my_postgres_parser = PostgresParser()
>>> sql_text = '''
... --- let's parse this statement.
... select upper(d.dept_name) department, e.*
... from org.dept d join emp e
... on d.id = e.dept_id;
... '''
>>> parsed_stmt = [stmt for stmt in my_postgres_parser.parse(sql_text)]

>>> ## Datasets [tables/views] used in the sql
... for ds in parsed_stmt[0].datasets_involved():
...     print(ds)

{'type': 'Dataset', 'dataset': 'dept', 'schema': 'org', 'catalog': None, 'alias': 'd', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:org.dept d]}
{'type': 'Dataset', 'dataset': 'emp', 'schema': None, 'catalog': None, 'alias': 'e', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:emp e]}

>>> ## Datafields [columns] used in the sql
... for df in parsed_stmt[0].datafields_involved():
...     print(df)

{'type': 'Function Field', 'datafield': 'upper(d.dept_name) ', 'datafield_alias': 'department', 'dataset': None, 'schema': None, 'catalog': None, 'dataset_type': None, 'dataset_alias': None, 'rw_ind': 'r', 'defined_at': [TokenGroup:Function:upper(d.dept_name) department]}
{'type': 'Datafield', 'datafield': 'dept_name', 'datafield_alias': None, 'dataset': 'dept', 'schema': 'org', 'catalog': None, 'dataset_type': 'Dataset', 'dataset_alias': 'd', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:d.dept_name]}
{'type': 'Datafield', 'datafield': '*', 'datafield_alias': None, 'dataset': 'emp', 'schema': None, 'catalog': None, 'dataset_type': 'Dataset', 'dataset_alias': 'e', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:e.*]}
{'type': 'Datafield', 'datafield': 'id', 'datafield_alias': None, 'dataset': 'dept', 'schema': 'org', 'catalog': None, 'dataset_type': 'Dataset', 'dataset_alias': 'd', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:d.id]}
{'type': 'Datafield', 'datafield': 'dept_id', 'datafield_alias': None, 'dataset': 'emp', 'schema': None, 'catalog': None, 'dataset_type': 'Dataset', 'dataset_alias': 'e', 'rw_ind': 'r', 'defined_at': [TokenGroup:Identifier:e.dept_id]}
```

## Links

### GitHub Project Page

<https://github.com/beingPeeDi/sqlsense>

## License

SQLSense is licensed under the [MIT license](LICENSE.txt).

## Author

**SQLSense** is maintained by **Priyadarshan Shashikant Dalvi** <priyadarshan.dalvi@hotmail.com>
