#!/bin/usr/env python

import sys
import readline # This import allows for an improvement of the input function
import atexit
import os

"""
The aim of this script is to parse a text file without using a higher-level object-oriented language.
It can take either one input parameter of a filename in the same directory or will prompt for a filename if no input
parameter was given.

Results format has the follow columns (in order):
* Archived                       - Used when a certificate is no longer used even if it hasn't expired yet
* Location                       - The physical location of where the server is housed
* Product                        - The product that the certificate supports
* Product Component              - A more specific part to the product that uses the certificate
* Host Name/IP                   - If local an IP might be more useful information but all things should be resolved to a domain name by the DNS
* Expiration Date                - Expiration date of the certificate (extracted from the "valid to" portion of metadata)
* Connection                     - Specifies what the connection is used for; typically shown as X connects to Y as a client by authentication this certificate
* Use                            - Used either as a client (trust cert) or a server (keypair) certificate
* Alias/Common Name              - Sometimes the alias matches the common name but this is the alias present in the keystore
* Issuer                         - The issuer of the certificate
* Creation Date                  - Creation date of the certificate (extracted from the "valid from" portion of the metadata)
* File Name                      - File name that is extracted from the absolute path of the variable cert_store
* Key pair location              - This is an archaic field
* File Type                      - File extension
* Key Strength                   - Encryption algorithm
* Owner/Subject/RootCA Title     - The subject of the certificate
* Serial Number                  - Serial number of the certificate
* Owner                          - This is an archaic field but it represented the group owner of the certificate (person in control of the keypair)
* Comments                       - Any additional comments or updates that add more specific details
* Received On                    - Date when the certificate metadata was provided
* Received From                  - Person who provided the certificate metadata
* Inherited                      - Whether or not the certificate was created by an internal group or provided by someone else or another vendor
"""
# Global variables
cert_store = ''
location = ''
product = ''
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

# Variable to be used for grabbing one certificate at a time
is_full_metadata = False

"""
Results file
Note that this will always create/overwrite on a file named "results.csv"
"""
results = open("results.csv", 'w+')
# Initial write to create the columns headers
results.write("Archived,Location,Product,Product Component,Host Name/IP,Expiration,Connection,Use,Alias/Common Name,Issuer,Creation,File Name,Key Pair Location,File Type,Key Strength,Owner/Subject/RootCA Title,Serial Number,Owner,Comments,Received On,Received From,Inherited\n")

# Function used in the atexit exit handler
def closeAllOpenFiles():
  # Although Python always closes file when it ends and after a "with" statement, this is to ensure data corruption does not occur
  results.close()

# Registering the "closeAllOpenFiles" function as a function that will
# be called upon exit (hopefully whenever a sudden exit occurs but not when fatal errors occur)
atexit.register(closeAllOpenFiles)

# This function serves no other purpose than for modularity and making more (useful) subprocedures for future testing
def updateFileName():
  global cert_store
  
  cert_store = raw_input('Please input the keystore/truststore text file you would like to access: \n')
  cert_store = os.path.abspath(cert_store)

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
This function parses through each line of the text file that this script takes as user input
and then prints out all the pertinent metadata (including hard-coded values stored as global
variables) in the appropriate columns headers format to results.csv

*** Please note that any file that has been formatted by DOS must be converted to UNIX ***
"""
def parse():
  global cert_store
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
  with open(cert_store, 'r') as file:
    # For whatever reason, readlines() will not work because additional
    # new-line characters were added into the text file. This (file.read().splitlines()) removes that issue.
    lines = file.read().splitlines()
    line_numbers = iter(range(0, len(lines)))
    for line_number in line_numbers:
      line = lines[line_number]

      # Ensures only the starts (before any certificate metadata) of the servernames are recognized
      # to be used as the host name/IP
      if host_name_available:
        host_name = validateAndExtractServerNames(host_name, "============ servername:", line, hostname_splice_start)

      # This entire set of logic could have been placed in a separate function for modularity
      # ** Take note to do this in future revisions **
      if not is_full_metadata:
        # Nested if statement control flow to prevent multiple calls to the validateAndExtract
        # or validateAndExtractDates functions which will take up space on the assembly instructions set
        if alias == "":
          alias = validateAndExtract(alias, "Alias", line, alias_splice_start)
          # Some aliases use an issuer/owner name (which is strange) so we must remove the commas
          alias = alias.replace(',', '_')
        else:
          if cert_type == "":
            cert_type = validateAndExtract(cert_type, "Entry type:", line, certType_splice_start)
            # Removes any newlines that might have been generated during the printing of the
            # input text file or any DOS code that wasn't originally recognized
            cert_type = cert_type.replace('\r', '')
            cert_type = cert_type.replace('\n', '')
          else:
            if owner == "":
              owner = validateAndExtract(owner, "Owner", line, owner_splice_start)
              owner = owner.replace(',', '_')
              # Removes any newlines that might have been generated during the printing of the
              # input text file or any DOS code that wasn't originally recognized
              owner = owner.replace('\r', '')
              owner = owner.replace('\n', '')
            else:
              if issuer == "":
                issuer = validateAndExtract(issuer, "Issuer:", line, issuer_splice_start)
                issuer = issuer.replace(',', '_')
                # Removes any newlines that might have been generated during the printing of the
                # input text file or any DOS code that wasn't originally recognized
                issuer = issuer.replace('\r', '')
                issuer = issuer.replace('\n', '')
              else:
                if serial_number == "":
                  serial_number = validateAndExtract(serial_number, "Serial", line, serialNumber_splice_start)
                else:
                  if start_date == "":
                    start_date = validateAndExtractDates(start_date, "Valid", line, "start")
                    # Removes any newlines that might have been generated during the printing of the
                    # input text file or any DOS code that wasn't originally recognized
                    start_date = start_date.replace('\r', '')
                  if expiration_date == "":
                    expiration_date = validateAndExtractDates(expiration_date, "Valid", line, "expiration")
                    # Removes any newlines that might have been generated during the printing of the
                    # input text file or any DOS code that wasn't originally recognized
                    expiration_date = expiration_date.replace('\r', '')
                  else:
                    if key_strength == "":
                      key_strength = validateAndExtract(key_strength, "Signature", line, keyStrength_splice_start)
                      key_strength = key_strength.replace("with", " with ")
        # Provides an output to see the results of the extraction and to validate that the list of metadata is full
        if (alias != "") and (cert_type != "") and (serial_number != "") and (issuer != "") and \
           (owner != "") and (expiration_date != "") and (start_date != "") and \
           (key_strength != ""):
          is_full_metadata = True
          if host_name_available:
            print("\nExtraction Result:\n\n{}, {}, {}, {}, {}, {}, {}, {}, {}".format(alias, cert_type, host_name, issuer, owner, serial_number, start_date, expiration_date, key_strength))
          else:
            print("\nExtraction Result:\n\n{}, {}, "", {}, {}, {}, {}, {}, {}".format(alias, cert_type, issuer, owner, serial_number, start_date, expiration_date, key_strength))

      if is_full_metadata:
        # Beyond just having a full set of metadata, we have to check that it wasn't set to full due to an error (repetition/redundancy is acceptable and can be removed easily in post-results)
        # Import line to results.csv
        """
        Archived,Location,Product,Product Component,Host Name/IP,Expiration,Connection,Use,Alias/Common Name,Issuer,Creation,File Name,Key Pair Location,File Type,Key Strength,Owner/Subject/RootCA Title,Serial Number,Owner,Comments,Received On,Received From,Inherited
        """
        # Determines if the entry was a client certificate or a server certificate
        if cert_type == "trustedCertEntry":
          if host_name_available:
            results.write("," + \
                          location + "," + \
                          product + ",," + \
                          host_name + "," + \
                          expiration_date + \
                          ",,Trusted Cert," + \
                          alias + "," + \
                          issuer + "," + \
                          start_date + "," + \
                          cert_store + \
                          ",,.jks," + \
                          key_strength + "," + \
                          owner + "," + \
                          serial_number + \
                          ",,," + \
                          received_on + "," + \
                          received_from + "," + \
                          "YES\n")
          else:
            results.write("," + \
                          location + "," + \
                          product + ",,," + \
                          expiration_date + \
                          ",,Trusted Cert," + \
                          alias + "," + \
                          issuer + "," + \
                          start_date + "," + \
                          cert_store + \
                          ",,.jks," + \
                          key_strength + "," + \
                          owner + "," + \
                          serial_number + \
                          ",,," + \
                          received_on + "," + \
                          received_from + "," + \
                          "YES\n")
        elif cert_type == "PrivateKeyEntry":
          if host_name_available:
            results.write("," + \
                          location + "," + \
                          product + ",," + \
                          host_name + "," + \
                          expiration_date + \
                          ",,Key Pair," + \
                          alias + "," + \
                          issuer + "," + \
                          start_date + "," \
                          + cert_store + \
                          ",,.jks," + \
                          key_strength + "," + \
                          owner + "," + \
                          serial_number + \
                          ",,," + \
                          received_on + "," + \
                          received_from + "," + \
                          "YES\n")
          else:
            results.write("," + \
                          location + "," + \
                          product + ",,," + \
                          expiration_date + \
                          ",,Key Pair," + \
                          alias + "," + \
                          issuer + "," + \
                          start_date + "," + \
                          cert_store + \
                          ",,.jks," + \
                          key_strength + "," + \
                          owner + "," + \
                          serial_number + \
                          ",,," + \
                          received_on + "," + \
                          received_from + "," + \
                          "YES\n")
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
def main(argv):
  global cert_store
  
  # No input parameter
  if len(argv) == 0:
    updateFileName()
    parse()
  # One or more input parameter but only the first input parameter is taken
  elif len(argv) == 1:
    cert_store = argv[0]
    if os.path.isdir(os.path.abspath(cert_store)):
      directory_list = os.listdir(os.path.abspath(cert_store))
      full_path = os.path.abspath(cert_store)
      for file in directory_list:
        cert_store = full_path + '/' + file
        parse()
    elif os.path.isfile(cert_store):
      cert_store = os.path.abspath(cert_store)
      parse()
  elif len(argv) > 1:
    # This assumes that things will only happen from the current level downward
    full_path = os.path.abspath(cert_store)
    for file in argv:
      cert_store = full_path + '/' + file
      parse()
  results.close()

if __name__ == '__main__':
  # Starting the main function
  # This try and except is meant to catch a Ctrl+C sudden stop without raising larger concerns
  try:
    # Takes parameters beside the name of the script
    main(sys.argv[1:])
  except KeyboardInterrupt:
    print('Suddenly exiting: Caused by Ctrl+C')
    sys.exit(0) # Raising the SystemExit exception without classifying the exit as something caused by an error
  except:
    raise