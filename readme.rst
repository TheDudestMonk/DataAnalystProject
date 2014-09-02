===========
Description
===========

usage: DataAnalystAssignment.py [-h] [-f FILENAME]

Establish conn to example.db

======
Query
======

Select: patient_id, date, kit_type, result

Conditions:

* kit_type=abbott
* results < 1000
* records dated > Jan 1, 2000

Output:

	Default:  prints records and errors to stdout
	-f, or --filename: outputs to csv and errorlog in current working directory

======================
Command Line Arguments
======================

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        filename for output to csv: default = results to
                        stdout
