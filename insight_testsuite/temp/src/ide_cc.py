import numpy as np
import pandas as pd
import os
import re
import warnings
import heapq

'''

'''
def push_data_into_heaps(list_min_heap, list_max_heap, value):
	if (len(list_min_heap) == 0) and (len(list_max_heap) == 0):	# No heaps initialised
		heapq.heappush(list_min_heap, value)
	elif (len(list_min_heap) == 1) and (len(list_max_heap) == 0):	# Only min heap initialised
		tmp = heapq.heappop(list_min_heap)
		heapq.heappush(list_max_heap, -min(tmp, value))
		heapq.heappush(list_min_heap, max(tmp, value))
	else:	# Both heaps initialised
		if (value < -list_max_heap[0]):	# Value smaller than root of max heap => value added to max heap
			heapq.heappush(list_max_heap, -value)
		else:	# Values greater than or equal to max heap root added to min heap
			heapq.heappush(list_min_heap, value)

		# Ensuring Heaps Not Imbalanced by More than One Element
		if (len(list_max_heap) == len(list_min_heap) + 2):
			tmp = -heapq.heappop(list_max_heap)
			heapq.heappush(list_min_heap, tmp)		
		if (len(list_min_heap) == len(list_max_heap) + 2):
			tmp = -heapq.heappop(list_min_heap)
			heapq.heappush(list_max_heap, tmp)
'''

'''
def calculate_median_from_heaps(list_min_heap, list_max_heap):
	if (len(list_min_heap) == 0) and (len(list_max_heap) == 0):
		print "# Error [calculate_median_from_heaps(...)]: Empty max and min heaps specified"
		return float("NaN")
	if (len(list_min_heap) == len(list_max_heap)):
		return 0.5*(list_min_heap[0] - list_max_heap[0])
	if (len(list_min_heap) == len(list_max_heap) + 1):
		return list_min_heap[0]
	if (len(list_max_heap) == len(list_min_heap) + 1):
		return -list_max_heap[0]
	print "# Error [calculate_median_from_heaps(...)]: Logic error while computing median"
	return float("NaN")

'''
Function name: custom_round

Description: 
	Rounding function for numerical values in lieu of conventional rounding functions
	* For positive values, rounding up to next integer for fractional part >= 0.5 (e.g. 2.5 --> 3, 4.5 --> 5, etc.)
	* For negative values, rounding down to next integer for fractional part >= 0.5 (e.g. -2.5 --> -3, -4.5 --> -5, etc.)
	* Rounding to integer part for fractional part <0.5 (e.g. 2.1 --> 2, -3.49 --> -3, etc.)
	
Input(s):	
	value -- numerical value to be rounded

Output(s):
	return

Return value(s):
 	Rounded value
'''
def custom_round(value):
	fractional_part = value - int(value)
	if (2*fractional_part >= +1.0):
		return int(value) + 1
	if (2*fractional_part <= -1.0):
		return int(value) - 1
	return int(value)

'''
Function name: process_medians_by_date

Description:
	Batch procesing of median data by date
	* Creation of appropriate output file
	* Collating/writing max, min, total, and count data for each CMTE_ID and TRANSACTION_DT pairs
		~ O(N) computational complexity
		~ Sorted data should be O(N*log(N)) complexity by the algorithm in pandas
	* Closing output file once done

Input(s):
	sorted_data_array 	-- data array (values from pandas data-frame) already sorted in the desired order (by CMTE_ID and TRANSACTION_DT)
	output_dir_abspath 	-- absolute path to output directory
	output_file_name 	-- name of output file to be generated
	idx_cmte_id 		-- index of CMTE_ID column in sorted_data_array
	idx_date 		-- index of TRANSACTION_DT column in sorted_data_array
	idx_amt			-- index of TRANSACTION_AMT column in sorted_data_array

Output(s):
	Data file in appropriate directory

Return value(s):
	N/A
'''
def process_medians_by_date(sorted_data_array, output_dir_abspath, output_file_name, idx_cmte_id=0, idx_date=13, idx_amt=14):
	if not(os.path.exists(output_dir_abspath)):
		os.mkdir(output_dir_abspath)
	
	output_file = open(output_dir_abspath + '/' + output_file_name, 'w')
	# To-do (AA): Output file column headers... 
	#output_file.write("CMTE_ID", "TRANSACTION_DT", "MEDIAN_AMT", "NUM_TRANSACTIONS", "TOTAL_AMT")
	
	idx_data = 0
	while (idx_data < sorted_data_array.shape[0]):
		curr_cmte_id = sorted_data_array[idx_data, idx_cmte_id]
		curr_date = sorted_data_array[idx_data, idx_date]
		heap_min = []
		heap_max = []
		push_data_into_heaps(heap_min, heap_max, sorted_data_array[idx_data, idx_amt])
		amt_total = sorted_data_array[idx_data, idx_amt]
		count = 1

		while (idx_data+1 < sorted_data_array.shape[0]) and (sorted_data_array[idx_data+1, idx_cmte_id] == curr_cmte_id) and (sorted_data_array[idx_data+1, idx_date] == curr_date):
			idx_data += 1
			push_data_into_heaps(heap_min, heap_max, sorted_data_array[idx_data, idx_amt])
			amt_total += sorted_data_array[idx_data, idx_amt]
			count += 1

		median_amt = custom_round(calculate_median_from_heaps(heap_min, heap_max))
		amt_total = custom_round(amt_total)
			
		output_file.write("%s|%s|%d|%d|%d\n" %(curr_cmte_id, curr_date, median_amt, count, amt_total))	
		
		idx_data += 1
	
	output_file.close()

'''
Function name: process_stream_medians_by_zip

Description:
	Processing one row of streamed contribution data
	* Validating data row
		1. OTHER_ID field to be empty (read as float("NaN") by pandas)
		2. ZIP_CODE field to be a sequence of 5 or 9 digits (cheked by RegEx matching)
	* Looking up CMTE_ID and ZIP_CODE pair in keys of data dictionary
		~ Search to use hash table built into the dict structure of Python [using dict.keys() look-up a very bad idea!]		
	* Creating dictinary entry if not already present, otherwise, updating available data
	* Writing data to output file

Input(s):
	accumulator_dict	-- dict structure for essential data
	single_data_row		-- individual data row (line of data from file) sent from data stream
	output_file		-- file object for writing data into
	idx_cmte_id		-- index of CMTE_ID column in single_data_row
	idx_zip			-- index of ZIP_CODE column in single_data_row
	idx_amt			-- index of TRANSACTION_AMT column in single_data_row
	idx_other_id		-- index of OTHER_ID column in single_data_row

Output(s):
	Line of data (if applicable) in file contained in appropriate directory
	
Return value(s):
	N/A

'''
def process_stream_medians_by_zip(accumulator_dict, single_data_row, output_file, idx_cmte_id=0, idx_zip=10, idx_amt=14, idx_other_id=15):
	if (str(single_data_row[idx_cmte_id]) != "nan") and (str(single_data_row[idx_amt]) != "nan") and (str(single_data_row[idx_other_id]) == "nan") and bool(re.match(r"^\d{5}(?:\d{4})?$", str(single_data_row[idx_zip]))):
		cmte_id = single_data_row[idx_cmte_id]
		zip_code = single_data_row[idx_zip][0:5]
		data_key = (cmte_id, zip_code)
		amt = single_data_row[idx_amt]
		if (data_key in accumulator_dict):
			accumulator_dict[data_key][2] += 1
			accumulator_dict[data_key][3] += amt
		else:
			accumulator_dict[data_key] = [[], [], 1, amt]	# accumulator_dict[key] = [min_heap, max_heap, 1, amt_total]	
		push_data_into_heaps(accumulator_dict[data_key][0], accumulator_dict[data_key][1], amt)
		amt_median = custom_round(calculate_median_from_heaps(accumulator_dict[data_key][0], accumulator_dict[data_key][1]))
		count = accumulator_dict[data_key][2]
		amt_total = custom_round(accumulator_dict[data_key][3])

		output_file.write("%s|%s|%d|%d|%d\n"  %(cmte_id, zip_code, amt_median, count, amt_total)) 

if __name__ == "__main__":

	input_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'input'))
	input_file_name = "itcont.txt"
	
	output_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'output'))
	output_by_date_file_name = "medianvals_by_date.txt"
	output_by_zip_file_name = "medianvals_by_zip.txt"

	''' Data Processing Only in Case of Data File Being Present at Expected Location '''
	if os.path.exists(input_dir + '/' + input_file_name):

		''' Reading Input Data File as a Pandas Data-Frame '''
		data = pd.read_csv(input_dir + '/' + input_file_name, sep='|', names=["CMTE_ID","AMNDT_IND","RPT_TP","TRANSACTION_PGI","IMAGE_NUM","TRANSACTION_TP","ENTITY_TP","NAME","CITY","STATE","ZIP_CODE","EMPLOYER","OCCUPATION","TRANSACTION_DT","TRANSACTION_AMT","OTHER_ID","TRAN_ID","FILE_NUM","MEMO_CD","MEMO_TEXT","SUB_ID"], dtype={"CMTE_ID":str, "OTHER_ID":str, "ZIP_CODE":str, "TRANSACTION_DT":str, "TRANSACTION_AMT":float}, low_memory=False)

		''' Batch Processing of Data by Date '''
		data_by_date = data[pd.isnull(data["OTHER_ID"])]	# Empty OTHER_ID 
		data_by_date = data_by_date[pd.notnull(data_by_date["TRANSACTION_AMT"])]	# Non-empty TRANSACTION_AMT
		data_by_date = data_by_date[pd.notnull(data_by_date["CMTE_ID"])] 	# Non-empty CMTE_ID
		warnings.filterwarnings("ignore", "This pattern has match groups")	# Warning suppression for RegEx check below	
		data_by_date["valid_date"] = data_by_date.TRANSACTION_DT.str.contains(r"^(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])(19|20\d\d)")	# Valid TRANSACTION_DT RegEx 
		data_by_date = data_by_date[data_by_date["valid_date"] == True]
		array_date_iso = np.array([date[-4:]+date[0:len(date)-4] for date in data_by_date["TRANSACTION_DT"]], dtype=str) # MMDDYYYY --> YYYYMMDD
		data_by_date["date_iso"] = array_date_iso	
		sorted_data_by_date = data_by_date.sort_values(["CMTE_ID","date_iso"], ascending=[True, True]) # Sorting data by CMTE_ID and TRANSACTION_DT
		process_medians_by_date(sorted_data_by_date.values, output_dir, output_by_date_file_name)	# Function defined earlier

		''' Streamed Processing of Data by ZIP Code '''
		if not(os.path.exists(output_dir)):
			os.mkdir(output_dir)
		output_by_zip_file = open(output_dir + '/' + output_by_zip_file_name, 'w')
		data_array_by_zip = data.values
		data_dict_by_zip = {}

		for i_data in range(data_array_by_zip.shape[0]):	# Creating line-by-line data stream from input file
			data_row = data_array_by_zip[i_data, :]
			process_stream_medians_by_zip(data_dict_by_zip, data_row, output_by_zip_file)	# Function defined earlier
			
		output_by_zip_file.close()
		
	else:
		print "# Error: File \'" + input_dir + '/' + input_file_name + "\' not found"
	
