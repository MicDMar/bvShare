from os import listdir
from os.path import isfile, join
import os
import sys

from socket import *

DEFAULT_REPO_PATH = 'repository'

#Reads in all the bytes that we were expecting to recieve
#from the server.
def getAllBytes(bytesExpected, conn):
  data = []
  while len(data) < bytesExpected:
    chunk = conn.recv(bytesExpected - len(data))
    data += chunk
  return data

#Reads in bytes one at a time so that it can stop
#at a new line character. (\n)
def getByteLine(conn):
  data = ""
  
  #Push one byte into the data array
  byte = conn.recv(1)
  data += byte.decode()

  index = 0
  while data[index] != '\n':
    byte = conn.recv(1)
    data += byte.decode()
    index += 1
  return data[:-1]

#Prints the fileArray as shown:
#   [1] file.txt
#   [2] file.py
#   [3] file.cpp
#   [4] file.png
def prettyPrintFiles(fileArray):
  value = 1
  for fileName in fileArray:
    print( '[' + str(value) + '] ' + str(fileName))
    value += 1

#Check to see if the input is indeed an integer and less than the
#specified maximum. If not then 0 is returned instead.
def getValidInput(maximum):
  selectedFileNum = input('Select a file to download: ')
  try:
    selectedFileNum = int(selectedFileNum)
    if (selectedFileNum > maximum):
      return 0
    else:
      return selectedFileNum
  except:
    return 0


def main():
  files = []

  #Check to see if the user provided command line arguments.
  #If not then request them here.
  if (len(sys.argv) < 3):
    address = input('Please specify a server IP Address: ')
    port = int(input('Please specify a port: '))
  else:
    address = sys.argv[1]
    port = int(sys.argv[2])

  repo = os.environ.get('REPOSITORY', DEFAULT_REPO_PATH)


  #Establish a connection to the server.
  conn = socket(AF_INET, SOCK_STREAM)
  conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  conn.connect((address, port))


  #Recieve the number of file names that will be sent from the server.
  numFiles = int.from_bytes(getAllBytes(4, conn), 'big')

  #Recieve file names here and append them to our file list.
  while (len(files) < numFiles):
    files.append(getByteLine(conn))

  #Print out file names in a 'pretty' fashion for the user.
  prettyPrintFiles(files)

  #Get the file that the user wants to download.
  selectedFile = getValidInput(numFiles)

  #Send a request to download the file from the server.
  conn.send(selectedFile.to_bytes(4, 'big'))

  if(0 <= selectedFile > len(files)):
    print("INVALID FILE SELECTION!")
    print("Closing connection...")
    return

  print("Downloading " + files[selectedFile - 1] + "...")


  #Recieve the size of the specified file.
  fileSize = int.from_bytes(getAllBytes(4, conn), 'big')

  #Recieve the file contents from the server.
  actualFile = getAllBytes(fileSize, conn)

  #Write to the file in our specified repository location
  with open(os.path.join(repo, files[selectedFile-1]), 'wb') as f:
    f.write(bytes(actualFile))

  print("Finished Downloading!")
  print("Closing Connection...")
  conn.close()


if __name__ == "__main__":
  main()
