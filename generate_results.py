#!/usr/bin/env python

import sys
import atexit
import os

# Created by:
# Jacky Cheng

"""
The aim of this script is to parse a text file without using a higher-level object-oriented language.
It can take either one input parameter of a filename in the same directory or will prompt for a filename if no input
parameter was given.

Results format has the follow columns (in order):
* Archived
* Location
* Product
* Product Component
* Host Name/IP
* Expiration Date
* Connection
* Use
* Alias/Common Name
* Issuer
* Creation Date
* File Name
* Key pair location
* File Type
* Key Strength
* Owner/Subject/RootCA Title
* Serial Number
* Owner
* Comments
* Received On
* Received From
* Inherited
"""
# Global variables
cert_store = ''
location = ''
product = ''
product_component = ''
received_on = ''
received_from = ''
host_name_available = False

hostname_splice_start = 2
alias_splice_start = 12
certType_splice_start = 12
owner_splice_start = 7
issuer_splice_start = 8
serialNumber_splice_start = 15
keyStrength_splice_start = 28

hostname_comp_string = "============ servername:"
alias_comp_string = "Alias"
certType_comp_string = "Entry type:"
owner_comp_string = "Owner"
issuer_comp_string = "Issuer:"
serialNumber_comp_string = "Serial"
startDate_comp_string = "start"
expirationDate_comp_string = "expiration"
keyStrength_comp_string = "Signature"
public_key_type = "trustedCertEntry"
private_key_type = "PrivateKeyEntry"

# Variable to be used for grabbing one certificate at a time
is_full_metadata = False

"""
Results file
Note that this will always create/overwrite on a file named "results.csv"
"""
results = open("results.csv", 'w+')
# Initial write to create the columns headers
results.write("Archived,Location,Product,Product Component,Host Name/IP,Expiration,Connection,Use,Alias/Common Name,Issuer,Creation,File Name,Key Pair Location,File Type,Key Strength,Owner/Subject/RootCA Title,Serial Number,Owner,Comments,Received On,Received From,Inherited\n")

"""
Function used in the atexit exit handler
"""
def closeAllOpenFiles():
  # Although Python always closes file when it ends and after a "with" statement, this is to ensure data corruption does not occur
  results.close()

"""
Registering the "closeAllOpenFiles" function as a function that will
be called upon exit (hopefully whenever a sudden exit occurs but not when fatal errors occur)
"""
atexit.register(closeAllOpenFiles)

"""
This function serves no other purpose than for modularity and making more (useful) subprocedures for future testing.
"""
def updateFileName():
  global cert_store
  while cert_store == "":
    cert_store = raw_input('\nPlease input the keystore/truststore text file you would like to access: \n')
  cert_store = os.path.abspath(cert_store)

"""
This function validates whether or not the user provided the input they wanted by polling the user for more input.
"""
def validateInputCorrectness(var):
  var_check = raw_input('\nPlease confirm "' + var + '" is correct(Y/N):\n').lower()
  while var_check != 'y' and var_check != 'n':
    print("\nPlease provide a valid response!\n")
    var_check = raw_input('\nPlease confirm "' + var + '" is correct(Y/N):\n').lower()
  if var_check == 'n':
    return ""
  return var

"""
This method defines the global variables set at the beginning of this file by polling the user for input.
"""
def defineGlobalVariables():
  global location
  global product
  global product_component
  global received_on
  global received_from
  global host_name_available

  host_name_input = ""

  while location == "":
    location = raw_input("\nPlease input the physical location that the certificate will be at:\n")
    if location == "":
      print("\nPlease provide a physical location!\n")
    else:
      location = validateInputCorrectness(location)

  while product == "":
    product = raw_input("\nPlease input the product that will make use of the certificate:\n")
    if product == "":
      print("\nPlease provide a product!\n")
    else:
      product = validateInputCorrectness(product)

  while product_component == "":
    product_component = raw_input("\nPlease input the component corresponding the product that will make use of the certificate:\n")
    if product_component == "":
      print("\nPlease provide a product component!\n")
    else:
      product_component = validateInputCorrectness(product_component)

  while received_on == "":
    received_on = raw_input("\nPlease input the day (format: M/D/YYYY) that the certificate(s) was/were provided:\n")
    received_on_test = received_on.split('/')
    if received_on == "":
      print("\nPlease provide a date that the certificate(s) was/were received on!\n")
    elif len(received_on_test) == 3:
      if not received_on_test[0].isdigit() or \
         (len(received_on_test[0]) != 1 and len(received_on_test[0]) != 2) or \
         not received_on_test[1].isdigit() or \
         (len(received_on_test[1]) != 1 and len(received_on_test[1]) != 2) or \
         not received_on_test[2].isdigit() or \
         len(received_on_test[2]) != 4:
        received_on = ""
        print("\nPlease provide a valid date!\n")
    elif len(received_on_test) != 3:
      received_on = ""
      print("\nPlease provide a valid date!\n")
    else:
      received_on = validateInputCorrectness(received_on)

  while received_from == "":
    received_from = raw_input("\nPlease input the person/group who provided the certificate(s)\n")
    if received_from == "":
      print("\nPlease provide a person or group from whom the certificate(s) was/were obtained from!\n")
    else:
      received_from = validateInputCorrectness(received_from)

  while host_name_input != 'y' and host_name_input != 'n':
    host_name_input = raw_input("\nAre there host names in the files that we can use (Y/N)?\n").lower()
    if host_name_input == 'y':
      host_name_available = True
    elif host_name_input == 'n':
      host_name_available = False
    else:
      print("\nPlease provide a valid response!\n")

"""
This function is the basic extraction where it begins a string splice from the starting
position provided in the parameter and returns the result

Parameters:
---------------------
current_string : string
  This string will provide a pass-by-reference type of return in the event that the comp_string
  does not match to prevent any loss of value of the current string
comp_string : string
  This string will provide the sub-string that will be compared to the line to search for
  the appropriate line containing the pertinent metadata
line : string
  This string is a line that is read using the "with" statement and will go through the file
  that was inputted by the user
slice_start_pos : integer
  This is the starting position for the string splicing to occur to gather the results from
  the line variable

Returns:
---------------------
result_string : string
  This string is the result of the splicing of the line variable in the case that the
  comparison sub-string exists within the line variable
current_string: string
  This is the string's original value before it might be changed. This means that the variable
  that gets assigned the output of this function is the same as current_string
"""
def validateAndExtract(current_string, comp_string, line, slice_start_pos):
  global is_full_metadata

  if (not is_full_metadata) and (comp_string in line) and (current_string == ""):
    result_string = line[slice_start_pos:]
    # Parsing to only have the pertinent information from each line
    return result_string
  else:
    return current_string

"""
This function is used specifically to extract server names.

Parameters:
---------------------
current_string : string
  This string will provide a pass-by-reference type of return in the event that the comp_string
  does not match to prevent any loss of value of the current string
comp_string : string
  This string will provide the sub-string that will be compared to the line to search for
  the appropriate line containing the pertinent metadata
line : string
  This string is a line that is read using the "with" statement and will go through the file
  that was inputted by the user
string_split_pos : integer
  This is the position that contains the pertinent data after a string split using a space as the
  delimiter

Returns:
---------------------
result_string : string
  This string is the result of the split of the line variable in the case that the
  comparison sub-string exists within the line variable
current_string: string
  This is the string's original value before it might be changed. This means that the variable
  that gets assigned the output of this function is the same as current_string
"""
def validateAndExtractServerNames(current_string, comp_string, line, string_split_pos):
  if comp_string in line:
    print(line)
    result_string = line.split(' ')[string_split_pos]
    # Parsing to only have the pertinent information from each line
    if result_string != current_string:
      return result_string
  else:
    return current_string

"""
This function is used convert extracted dates into the ideal date for manipulation in Excel.

Parameters:
---------------------
month : string
  This string will provide the month abbreviated to three letters with the first letter being capitalized
day : string
  This string will provide the day as a number
year : string
  This string will provide the year as a number

Returns:
---------------------
string
  This string is the result of the abbreviated month converted to a number resulting in the following format: M/DD/YYYY
"""
def convertAbbreviatedDates(month, day, year):
  if month == "Jan":
    return "1/" + day + '/' + year
  elif month == "Feb":
    return "2/" + day + '/' + year
  elif month == "Mar":
    return "3/" + day + '/' + year
  elif month == "Apr":
    return "4/" + day + '/' + year
  elif month == "May":
    return "5/" + day + '/' + year
  elif month == "Jun":
    return "6/" + day + '/' + year
  elif month == "Jul":
    return "7/" + day + '/' + year
  elif month == "Aug":
    return "8/" + day + '/' + year
  elif month == "Sep":
    return "9/" + day + '/' + year
  elif month == "Oct":
    return "10/" + day + '/' + year
  elif month == "Nov":
    return "11/" + day + '/' + year
  elif month == "Dec":
    return "12/" + day + '/' + year

"""
This function is used specifically to extract dates.

Parameters:
---------------------
current_string : string
  This string will provide a pass-by-reference type of return in the event that the comp_string
  does not match to prevent any loss of value of the current string
comp_string : string
  This string will provide the sub-string that will be compared to the line to search for
  the appropriate line containing the pertinent metadata
line : string
  This string is a line that is read using the "with" statement and will go through the file
  that was inputted by the user
start_or_expiration : string
  This tells the function whether or not the date that is to be searched is a "start" or "expiration" date
  which requires different positions to be obtained after the split to gather the correct data

Returns:
---------------------
result_string : string
  This string is the result of the splitting of the line variable in the case that the
  comparison sub-string exists within the line variable
current_string: string
  This is the string's original value before it might be changed. This means that the variable
  that gets assigned the output of this function is the same as current_string
"""
def validateAndExtractDates(current_string, comp_string, line, start_or_expiration):
  global is_full_metadata

  if (not is_full_metadata) and (comp_string in line):
    line_splitted = line.split(' ')
    result_string = ''
    if start_or_expiration == 'start':
      result_string = convertAbbreviatedDates(line_splitted[3], line_splitted[4], line_splitted[7])
    elif start_or_expiration == 'expiration':
      result_string = convertAbbreviatedDates(line_splitted[10], line_splitted[11], line_splitted[14])
    # Parsing to only have the pertinent information from each line
    return result_string
  else:
    return current_string

"""
Performs a check on the line to see if the host name is on the line.
"""
def checkForHostName(hostName, line):
  newHostName = validateAndExtractServerNames(hostName, hostname_comp_string, line, hostname_splice_start)
  return newHostName

"""
Performs a check on the line to see if the alias is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForAlias(alias, line):
  newAlias = validateAndExtract(alias, alias_comp_string, line, alias_splice_start)
  # Some aliases use an issuer/owner name (which is strange) so we must remove the commas
  newAlias = newAlias.replace(',', '_')
  return newAlias

"""
Performs a check on the line to see if the key type is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForCertType(certType, line):
  newCertType = validateAndExtract(certType, certType_comp_string, line, certType_splice_start)
  # Removes any newlines that might have been generated during the printing of the
  # input text file or any DOS code that wasn't originally recognized
  newCertType = newCertType.replace('\r', '')
  newCertType = newCertType.replace('\n', '')
  return newCertType

"""
Performs a check on the line to see if the owner is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForOwner(owner, line):
  newOwner = validateAndExtract(owner, owner_comp_string, line, owner_splice_start)
  newOwner = newOwner.replace(',', '_')
  # Removes any newlines that might have been generated during the printing of the
  # input text file or any DOS code that wasn't originally recognized
  newOwner = newOwner.replace('\r', '')
  newOwner = newOwner.replace('\n', '')
  return newOwner

"""
Performs a check on the line to see if the issuer is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForIssuer(issuer, line):
  newIssuer = validateAndExtract(issuer, issuer_comp_string, line, issuer_splice_start)
  newIssuer = newIssuer.replace(',', '_')
  # Removes any newlines that might have been generated during the printing of the
  # input text file or any DOS code that wasn't originally recognized
  newIssuer = newIssuer.replace('\r', '')
  newIssuer = newIssuer.replace('\n', '')
  return newIssuer

"""
Performs a check on the line to see if the serial number is on the line.
"""
def checkForSerialNumber(serialNumber, line):
  newSerialNumber = validateAndExtract(serialNumber, serialNumber_comp_string, line, serialNumber_splice_start)
  return newSerialNumber

"""
Performs a check on the line to see if the start date is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForStartDate(startDate, line):
  newStartDate = validateAndExtractDates(startDate, "Valid", line, startDate_comp_string)
  # Removes any newlines that might have been generated during the printing of the
  # input text file or any DOS code that wasn't originally recognized
  newStartDate = newStartDate.replace('\r', '')
  return newStartDate

"""
Performs a check on the line to see if the expiration date is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForExpirationDate(expirationDate, line):
  newExpirationDate = validateAndExtractDates(expirationDate, "Valid", line, expirationDate_comp_string)
  # Removes any newlines that might have been generated during the printing of the
  # input text file or any DOS code that wasn't originally recognized
  newExpirationDate = newExpirationDate.replace('\r', '')
  return newExpirationDate

"""
Performs a check on the line to see if the key strength is on the line. Afterwards, the necessary string reformatting is performed.
"""
def checkForKeyStrength(keyStrength, line):
  newKeyStrength = validateAndExtract(keyStrength, keyStrength_comp_string, line, keyStrength_splice_start)
  newKeyStrength = newKeyStrength.replace("with", " with ")
  return newKeyStrength

"""
Writes all the appropriate variables into the results file in the correct format for further data manipulation after the full results are generated.
TODO: Add functionality to change file type by extension. If no extension exists, leave the value as blank. 
"""
def writeToFile(hostName, alias, certType, owner, issuer, serialNumber, startDate, expirationDate, keyStrength):
  # Beyond just having a full set of metadata, we have to check that it wasn't set to full due to an error (repetition/redundancy is acceptable and can be removed easily in post-results)
  # Import line to results.csv
  """
  Archived,Location,Product,Product Component,Host Name/IP,Expiration,Connection,Use,Alias/Common Name,Issuer,Creation,File Name,Key Pair Location,File Type,Key Strength,Owner/Subject/RootCA Title,Serial Number,Owner,Comments,Received On,Received From,Inherited
  """
  # Determines if the entry was a client certificate or a server certificate
  if certType == public_key_type:
    if host_name_available:
      results.write("," + \
                    location + "," + \
                    product + "," + \
                    product_component + "," + \
                    hostName + "," + \
                    expirationDate + \
                    ",,Trusted Cert," + \
                    alias + "," + \
                    issuer + "," + \
                    startDate + "," + \
                    os.path.basename(cert_store) + \
                    ",,.jks," + \
                    keyStrength + "," + \
                    owner + "," + \
                    serialNumber + \
                    ",,," + \
                    received_on + "," + \
                    received_from + "," + \
                    "YES\n")
    else:
      results.write("," + \
                    location + "," + \
                    product + "," + \
                    product_component + ",," + \
                    expirationDate + \
                    ",,Trusted Cert," + \
                    alias + "," + \
                    issuer + "," + \
                    startDate + "," + \
                    os.path.basename(cert_store) + \
                    ",,.jks," + \
                    keyStrength + "," + \
                    owner + "," + \
                    serialNumber + \
                    ",,," + \
                    received_on + "," + \
                    received_from + "," + \
                    "YES\n")
  elif certType == private_key_type:
    if host_name_available:
      results.write("," + \
                    location + "," + \
                    product + "," + \
                    product_component + "," + \
                    hostName + "," + \
                    expirationDate + \
                    ",,Key Pair," + \
                    alias + "," + \
                    issuer + "," + \
                    startDate + "," + \
                    os.path.basename(cert_store) + \
                    ",,.jks," + \
                    keyStrength + "," + \
                    owner + "," + \
                    serialNumber + \
                    ",,," + \
                    received_on + "," + \
                    received_from + "," + \
                    "YES\n")
    else:
      results.write("," + \
                    location + "," + \
                    product + "," + \
                    product_component + ",," + \
                    expirationDate + \
                    ",,Key Pair," + \
                    alias + "," + \
                    issuer + "," + \
                    startDate + "," + \
                    os.path.basename(cert_store) + \
                    ",,.jks," + \
                    keyStrength + "," + \
                    owner + "," + \
                    serialNumber + \
                    ",,," + \
                    received_on + "," + \
                    received_from + "," + \
                    "YES\n")

"""
This function checks if all appropriate variables have been assigned. If the appropriate variables have been assigned, the variables are printed out in the following format:
alias, key type, host name, issuer, owner, serial number, start date, expiration date, key strength

This function also returns whether or not the check was successful.
"""
def checkForCompleteness(hostName, alias, certType, owner, issuer, serialNumber, startDate, expirationDate, keyStrength):
  # Provides an output to see the results of the extraction and to validate that the list of metadata is full
  if (alias != "") and (certType != "") and (serialNumber != "") and (issuer != "") and \
     (owner != "") and (expirationDate != "") and (startDate != "") and \
     (keyStrength != ""):
    if host_name_available:
      print("\nExtraction Result:\n\n{}, {}, {}, {}, {}, {}, {}, {}, {}".format(alias, certType, hostName, issuer, owner, serialNumber, startDate, expirationDate, keyStrength))
    else:
      print("\nExtraction Result:\n\n{}, {}, "", {}, {}, {}, {}, {}, {}".format(alias, certType, issuer, owner, serialNumber, startDate, expirationDate, keyStrength))
    return True
  else:
    return False

"""
This function parses through each line of the text file that this script takes as user input
and then prints out all the pertinent metadata (including hard-coded values stored as global
variables) in the appropriate columns headers format to results.csv

*** Please note that any file that has been formatted by DOS must be converted to UNIX ***

Parameters:
---------------------
line: string
This is the file that runs under the assumption that the file is a regular file and then runs the parsing function to
extract all pertinent metadata.

alias: string
This is the alias that is currently set when trying to interpret the line.

cert_type: string
This is the certificate type (keypair or trusted cert) that is currently set when trying to interpret the line.

owner: string
This is the owner line that is currently set when trying to interpret the line.

issuer: string
This is the issuer line that is currently set when trying to interpret the line.

serial_number: string
This is the serial number that is currently set when trying to interpret the line.

start_date: string
This is the shorthand start date that is currently set when trying to interpret the line.

expiration_date: string
This is the shorthand expiration date that is currently set when trying to interpret the line.

key_strength: string
This is the signature algorithm that is currently set when trying to interpret the line.

Returns:
---------------------
newAlias: string
This is the new alias determined by the line if it exists on the line and the input parameter was empty.

newCertType: string
This is the certificate type (keypair or trusted ert) determined by the line if it exists on the line and the input
parameter was empty.

newOwner: string
This is the owner line determined by the line if it exists on the line and the input parameter was empty.

newIssuer: string
This is the issuer line determined by the line if it exists on the line and the input parameter was empty.

newSerialNumber: string
This is the serial number determined by the line if it exists on the line and the input parameter was empty.

newStartDate: string
This is the shorthand start date determined by the line if it exists on the line and the input parameter was empty.

newExpirationDate: string
This is the shorthand expiration date determined by the line if it exists on the line and the input parameter was empty.

newKeyStrength: string
This is the signature algorithm determined by the line if it exists on the line and the input parameter was empty.
"""
def processLine(line, alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength):
  newAlias = alias
  newCertType = cert_type
  newOwner = owner
  newIssuer = issuer
  newSerialNumber = serial_number
  newStartDate = start_date
  newExpirationDate = expiration_date
  newKeyStrength = key_strength
  # Nested if statement control flow to prevent multiple calls to the validateAndExtract
  # or validateAndExtractDates functions which will take up space on the assembly instructions set
  if alias == "":
    newAlias = checkForAlias(alias, line)
  else:
    if cert_type == "":
      newCertType = checkForCertType(cert_type, line)
    else:
      if owner == "":
        newOwner = checkForOwner(owner, line)
      else:
        if issuer == "":
          newIssuer = checkForIssuer(issuer, line)
        else:
          if serial_number == "":
            newSerialNumber = checkForSerialNumber(serial_number, line)
          else:
            if start_date == "":
              newStartDate = checkForStartDate(start_date, line)
            if expiration_date == "":
              newExpirationDate = checkForExpirationDate(expiration_date, line)
            else:
              if key_strength == "":
                newKeyStrength = checkForKeyStrength(key_strength, line)
  return newAlias, newCertType, newOwner, newIssuer, newSerialNumber, newStartDate, newExpirationDate, newKeyStrength

"""
This function parses through each line of the text file that this script takes as user input
and then prints out all the pertinent metadata (including hard-coded values stored as global
variables) in the appropriate columns headers format to results.csv

*** Please note that any file that has been formatted by DOS must be converted to UNIX ***

Parameters:
---------------------
f: string
This is the file that runs under the assumption that the file is a regular file and then runs the parsing function to
extract all pertinent metadata.

Returns:
---------------------
None
"""
def parse(f):
  global results
  global location
  global product

  # Initializing the variables for results
  if host_name_available:
    host_name=''

  alias = ''
  serial_number = ''
  issuer = ''
  owner = ''
  expiration_date = ''
  start_date = ''
  key_strength = ''
  cert_type = ''

  # Variable to be used for grabbing one certificate at a time
  global is_full_metadata

  # Opening the file
  with open(f, 'r') as file:
    # For whatever reason, readlines() will not work because additional
    # new-line characters were added into the text file. This (file.read().splitlines()) removes that issue.
    lines = file.read().splitlines()
    line_numbers = iter(range(0, len(lines)))
    for line_number in line_numbers:
      line = lines[line_number]

      # Ensures only the starts (before any certificate metadata) of the servernames are recognized
      # to be used as the host name/IP
      if host_name_available:
        host_name = checkForHostName(host_name, line)

      # This entire set of logic could have been placed in a separate function for modularity
      # ** Take note to do this in future revisions **
      if not is_full_metadata:
        alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength = processLine(line, alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength)

        if host_name_available:
          is_full_metadata = checkForCompleteness(host_name, alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength)
        else:
          is_full_metadata = checkForCompleteness('', alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength)
      else:
        if host_name_available:
          writeToFile(host_name, alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength)
        else:
          writeToFile('', alias, cert_type, owner, issuer, serial_number, start_date, expiration_date, key_strength)

        # Cleaning up data after import so a new certificate can be extracted
        is_full_metadata = False
        alias = ""
        issuer = ""
        owner = ""
        serial_number = ""
        expiration_date = ""
        start_date = ""
        key_strength = ""
        cert_type = ""

    # Although the ending of the with statement will close the file it interacts with,
    # to ensure data doesn't get lost or corrupted, we will close prior to the end of the with statement
    file.close()

"""
This function parses a single file. This function assumes that the file passed in will be a regular file.

Parameters:
---------------------
file: string
This is the file that runs under the assumption that the file is a regular file and then runs the parsing function to
extract all pertinent metadata.

Returns:
---------------------
None
"""
def parseFile(file):
  parse(os.path.abspath(file))

"""
This is the replacement to runSingleArgumentParsing() whereby this function recursively digs through the filesystem until it reaches
a directory that has only files in it and only parses files. This removes the restriction of only searching 1-level deep into a
filesystem.

Parameters:
---------------------
f: string
This is the file that will be checked as either a regular file or a directory and will be treated accordingly
to recursively parse through all available files.

Returns:
---------------------
None
"""
def recursiveParsing(f):
  global cert_store
  if os.path.isdir(f):
    base_path = os.path.abspath(f)
    directory_list = os.listdir(base_path)
    for file in directory_list:
      if os.path.isdir(base_path + '/' + file):
        recursiveParsing(base_path + '/' + file)
      elif os.path.isfile(base_path + '/' + file):
        parseFile(base_path + '/' + file)
  elif os.path.isfile(os.path.abspath(f)):
    parseFile(f)

def main(argv):
  global cert_store

  defineGlobalVariables()

  # No input parameter`
  if len(argv) == 0:
    updateFileName()
    recursiveParsing(cert_store)
  # One or more input parameter but only the first input parameter is taken
  elif len(argv) == 1:
    cert_store = argv[0]
    recursiveParsing(cert_store)
  elif len(argv) > 1:
    # This assumes that things will only happen from the current level downward
    full_path = os.path.abspath(cert_store)
    for file in argv:
      cert_store = full_path + '/' + file
      recursiveParsing(cert_store)
  results.close()

if __name__ == '__main__':
  # Starting the main function
  # This try and except is meant to catch a Ctrl+C sudden stop without raising larger concerns
  try:
    # Takes input arguments beside the name of the script
    main(sys.argv[1:])
  except KeyboardInterrupt:
    print('Suddenly exiting: Caused by Ctrl+C')
    sys.exit(0) # Raising the SystemExit exception without classifying the exit as something caused by an error
  except:
    raise
