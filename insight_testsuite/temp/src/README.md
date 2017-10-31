##################################################################################################

	Analysis of US Federal Elections Commission Individual Campaign Contribution Datasets

		Coding Challenge Submission for Insight Data Engineering Fellowship


	
					Abdullah Al Rashid


					October 31st, 2017

##################################################################################################


===================================
	General Information
===================================

Programming language used: Python

Modules used:
* pandas: version 0.20.0+
* numpy
* os
* re


========================================
	Transaction Data by Date
========================================

We process the input file as a Pandas data-frame for transaction by date, as we need not process a stream:
* A data-frame offers O(1) to O(log(N)) performance for filtering data.
* We filter out inadmissible input data using pandas.isnull(...), pandas.notnull(...), and RegEx matching for OTHER_ID, TRANSACTION_AMT, and TRANSACTION_DT, respectively.
* We also convert dates from MMDDYYYY to the YYYYMMDD ISO format for sorting
* The filtered data-frame is then sorted via pandas.dataframe.sort_values(...), which is available on Pandas versions 0.20.0+ and offers O(N*log(N)) performance
* We then traverse the data-frame line-by-line to collate statistics per (CMTE_ID, TRANSACTION_DT) pair: this has O(N) performance


============================================
	Transaction Data by ZIP Code
============================================

For processing by ZIP code case, we stream the raw Pandas data-frame parsed earlier row-by-row into a function:
* We validate CMTE_ID, OTHER_ID, TRANSACTION_AMT, and ZIP_CODE fields for each input row.
* We hold the necessary data in a Python dict and utilise its built-in hash table to search for and update data for existing (CMTE_ID, ZIP_CODE) keys: search and insert operations perform at O(1) on average
* We ouptut data into the output stream/file from the last updated entry in the dict.


