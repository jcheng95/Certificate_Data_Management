# Description #
This project houses scripts and macros to manipulate data obtained from a listing of certificate keystores.

## generate_results.py ##
### Description ###
This Python program can take 4 different types of inputs (as shown in the table below). This program takes a data dump from the use of "keytool -list -v" in order to extract pertinent metadata and put it into a CSV for spreadsheet maintenance.

### Argument Inputs ###
Arguments      | Description
-------------- | --------------
No input       | Not having an argument passed along when running the Python program will prompt the user to provide the file name of the data dump. It takes the file name and the runs the os.path.abspath() function to get the absolute path of the file that is relative to the path of the Python program.
Directory      | If the file that gets searched turns out to be a directory, the Python program will loop through all files in that directory. It takes the directory name and then runs the os.path.abspath() function to get the absolute path of the directory and its files that are relative to the path of the Python program. Running on a directory will only perform metadata extraction at the depth of the directory's files (no recursive downward extraction).
Single File    | If there is only one file that is provided, then the Python program will only extract metadata from that file. It takes the file name and the runs the os.path.abspath() function to get the absolute path of the file that is relative to the path of the Python program.
Multiple files | If there are multiple files passed as arguments, the Python program will loop through all of the files inputted to extract the metadata. It takes the file names and the runs the os.path.abspath() function to get the absolute path of the files that are relative to the path of the Python program.

## convert_abbreviations_to_numbers.txt ##
### Description ###
This macro converts abbreviated dates into shorthand dates. The month abbreviations must be 3 characters in length with the first character being capitalized. The output will be in the following format: M/DD/YYYY.

Example:
*Aug 12 2018* will be converted to *8/12/2018*

## generate_ninetydays_macro.txt ##
### Description ###
This macro uses the results generated from the generate_results.py program to create a new column after the "Expiration column" and call it "90 Days". Once the new column is created, all subsequent rows (2 and onward) will be populated with the results of the following equation:
Expiration date - 90

The result is the date 90 days prior to the expiration date. This is useful for providing a sysadmin the ability to plan renewals/replacements in advance.

## generate_yearly_macro.txt ##
### Description ###
This macro calculates the difference in years between the creation date and expiration date. It will always produce a positive number as it uses the following equation:
Expiration Year - Creation Year

If the difference in years matches the *comparison_date* variable, then it will notify you with "Use this" to let you know that the difference matches the number specified by that variable. This is useful for when a user wants to know which certificates have a validity period of X years.