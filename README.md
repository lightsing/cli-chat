README
---

# Python Cli-chat (In Developing)

## Requirement

1. Python 3
2. pyCrypto

## Warning

Include Server and Client.
Low efficiency due to RSA encryption almost all traffic.

> Consider using AES in the future.

## How to use

1. Generate a server RSA key pair using util.Operator.generateRSA() and writeoutRSA()
2. Edit config file.(__addr__ and __port__)
3. Run server.py
