#!/usr/bin/env python

import sys
import readline # This import allows for an improvement of the input function
import atexit
import os
from subprocess import call
import getpass

# Created by:
# Jacky Cheng

# Dictionary for quick lookup
common_dict = {"entrust-prod" : "OU=NHIN, O=HHS-ONC, C=US", \
               "entrust-test" : "OU=NHIN-Test, O=NHIN, C=US", \
               "37-prod" : "OU=DISA, OU=PKI, OU=DOD, O=U.S. Government, C=US", \
               "37-test" : "OU = CONTRACTOR, OU = PKI, OU = DoD, O = U.S. Government, C = US", \
               "38" : "OU=DISA, OU=PKI, OU=DOD, O=U.S. Government, C=US"}

# Global variables
certificate_authority = ""
owner_line = ""
common_name = ""
test_or_prod = ''

"""
This function is used to set the common name based on the certificate authority thalts will be the same but the question specifies
what needs to be provided.t will be used. The resu

Parameters:
---------------------
ca : string
  This string will provide the certificate authority that will be used so that more flow control can be performed to properly generate the certificate. The
  certificate authority affects the owner line

Returns:
---------------------
  This string is the result of user input for the common name that will be used in the owner line
"""
def setCommonName(ca):
  cn = ""
  while cn == "":
    if ca == "entrust":
      cn = raw_input(
        'Please input the reference number that you were provided (not the same as the authorization code): \n')
    elif ca == "37" or ca == "38":
      cn = raw_input(
        'Please input the common name you would like to use (it will be used as the alias and filenames): \n')
  return cn

"""
This function is used to set the variables that will be used to create the owner line that will be used as part of the "-dname" option when running the keytool command.

Parameters:
---------------------
ca : string
  This string will provide the certificate authority that will be used so that more flow control can be performed to properly generate the certificate. The
  certificate authority affects the owner line

Returns:
---------------------
owner : string
  This string is the result of determining the proper owner line based on the certificate authority that will be used
cn : string
  This string is the result of user input for the common name that will be used in the owner line
"""
def setOwnerLine(ca):
  if ca != "38" and test_or_prod == 't':
    owner = common_dict[ca + "-test"]
  elif ca != "38" and test_or_prod == 'p':
    owner = common_dict[ca + "-prod"]
  else:
    owner = common_dict[ca]
  cn = setCommonName(ca)
  return owner, cn

"""
This function is used to set the certificate authority that will affect the common name prompt and owner line prompt that will be used
as part of the "-dname" option when running the keytool command.

Parameters:
---------------------
NONE

Returns:
---------------------
ca : string
  This string is the result of user input for the certificate authority that will be used that will affect the owner line
"""
def setCertificateAuthority():
  global test_or_prod
  ca = ""
  while ca != "entrust" and ca != "37" and ca != "38":
    ca = raw_input('Please input the Certificate Authority (CA) you will be using (entrust, 37, 38): \n').lower()
    if (ca != "entrust") and (ca != "37") and (ca != "38"):
      print("\nPlease enter a correct CA!\n")
    elif ca == "entrust" or ca == "37":
      while test_or_prod != 't' and test_or_prod != 'p':
        test_or_prod = raw_input('\nIs this certificate for test or production (T/P)?\n').lower()
  return ca

"""
This function is used to check that all variables are used that the distinguished name is correct before running the keytool command. If the owner line is not correct,
it will query the user to input the right common name.

Parameters:
---------------------
NONE

Returns:
---------------------
NONE
"""
def pollForCorrectness():
  global owner_line
  global common_name
  poll = False
  while not poll:
    userInput = raw_input('Is "' + common_name + ', ' + owner_line + '"\ncorrect (Y/N)?\n')
    if userInput.lower() == 'y':
      poll = True
    elif userInput.lower() == 'n':
      owner_line, common_name = setOwnerLine(certificate_authority)
    else:
      continue

"""
This function is used to combine the common name and the rest of the owner line to create the distinguished name that will be used when running the keytool command.

Parameters:
---------------------
owner : string
  This string is the result of determining the proper owner line based on the certificate authority that will be used
cn : string
  This string is the result of user input for the common name that will be used in the owner line

Returns:
---------------------
string
  This string is the combination of the common name and the rest of the owner line to provide the full owner line that will be used as part of the
  "-dname" option when running the keytool command.
"""
def createDistinguishedName(owner, cn):
  return 'CN=' + cn + ', ' + owner

"""
This function is used to obtain the intended password through user input without printing out the user input to stdout.

Parameters:
---------------------
pw : string
  This string is the password resulting from user input.

Returns:
---------------------
boolean
  This boolean is 
"""
def validatePassword(pw):
  if pw != "":
    check = getpass.getpass("\nPlease retype the password to confirm:\n")
    if check == pw:
      return True
    else:
      print("Passwords do not match!\n")
  return False

"""
This function is used to obtain the intended password through user input without printing out the user input to stdout.

Parameters:
---------------------
NONE

Returns:
---------------------
pw : string
  This string is the password resulting from user input.
"""
def setPassword():
  pw = ""
  while not validatePassword(pw):
    pw = getpass.getpass("Please input the keystore/keypair password you would like to use:\n")
    if pw == "":
      print("\nPlease put in a password so that it can be secure!\n")
  return pw

# Running the main function to query the user for key input and then run the appropriate keytool commands to create the keypair and then to create the CSR based on the keypair
def main():
  global certificate_authority
  global owner_line
  global common_name

  # Getting the appropriate information to run the keytool commands
  certificate_authority = setCertificateAuthority()
  owner_line, common_name = setOwnerLine(certificate_authority)
  pollForCorrectness() # This will check the previous command was run to the user's predilection
  full_line = createDistinguishedName(owner_line, common_name)
  password = setPassword()

  print("\nGenerating the key pair\n")
  call('keytool -genkey -keyalg RSA -keysize 2048 -sigalg SHA256withRSA -validity 3650 -storepass "' + password + '" -keypass "' + password + '" -alias "' + common_name + '" -keystore "' + common_name + '.jks" -dname "' + full_line + '"', shell=True)
  print("\nGenerating the CSR\n")
  call("keytool -certreq -keyalg RSA -storepass " + password + " -alias '" + common_name + "' -file '" + common_name + ".csr' -keystore '" + common_name + ".jks'", shell=True)
  print("\nFinished!\n")

if __name__ == '__main__':
  # Starting the main function
  # This try and except is meant to catch a Ctrl+C sudden stop without raising larger concerns
  try:
    # Takes input arguments beside the name of the script
    main()
  except KeyboardInterrupt:
    print('\nSuddenly exiting: Caused by Ctrl+C\n')
    sys.exit(0)  # Raising the SystemExit exception without classifying the exit as something caused by an error
  except:
    raise