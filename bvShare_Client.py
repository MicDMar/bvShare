from socket import *

def getAllBytes(bytesExpected):
  data = []
  while len(data) < bytesExpected:
    chunk = conn.recv(bytesExpected - len(data))
    data += chunk
  return data

serverIP='10.92.16.58'
serverPort=3000

conn = socket(AF_INET, SOCK_STREAM)
conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
conn.connect((serverIP, serverPort))

fileSize = int.from_bytes(getAllBytes(8), 'big')

#print(fileSize)

actualFile = getAllBytes(fileSize)

#print(len(actualFile))

with open("forkBomb.py", 'wb') as f:
  f.write(bytes(actualFile))

print("Closing...")
conn.close()
