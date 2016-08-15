# Protocol of Lightsing Cli-chat
---
## Overview

In each connection, client will send a message encrypted by the public key of
server and server will return one or two message in which the first refers the
state code (`'Accepted'`, `'Invalid'` or something else) and it's signed by the
server.
It's not encrypted. ** Please don not put any thing except the state code
in this message.** The second message (if exist) contains the data that client
requested.

In common situation, if the first message refers a error then server won't send
the second message. The second message can be encrypted in various way. It's
decided by the specific purpose.

## Details

### Log in √

`entry code: 'login'`

In this version of implementation, the server won't offer any way to sign up.
** Please be caution if you want to put this cli-chat server into the public
network.**

The server will accept a request of log in. The message contains **the
 username, SHA256 Hash code of the password and the public key of client**.

 | Part I |   Part II   | Part III |
 |:------:|:-----------:|:--------:|
 |Username|Password Hash|Public Key|

The server will look up if the user exist in the record. If it doesn't exist,
the server will add it into the user-list.

**Please remind the server won't save the user-list. Once it shutdown, the
server will lost all records.**

Once the status of client turns into `Online`, the server will send a token
to client. After this action complete, the connection will be closed.

### Log out √

`entry code: 'logout'`

| Part I | Part II |
|:------:|:-------:|
|Username|  Token  |

This action will revoke the token, public key and set the status of user to
`Offline`

### Switch √

`entry code: 'switch'`

Except `login`, `logout` and `online` action, any other action is post in a
`switch` message.

| Part I | Part II | Part III | Part IV |
|:------:|:-------:|:--------:|:-------:|
|Username|  Token  |  Action  |   Data  |

The four part is necessary for any `switch` message.

#### Check a user status

`action code: 'find'`

##### Request

| Part I |
|:------:|
|Username|

##### Response

###### Message I

1. `Found`
2. `Not Found`

###### Message II

| Part I | Part II | Part III |
|:------:|:-------:|:--------:|
|isOnline|last seen|Public Key|

#### Send Message to Other Clients via Server

`action code: 'send'`

#### Get Others Public Key [x] (Not use)

`action code: 'getPublicKey'`

#### Send Message Directly

`action code: 'sendDirect'`

#### Get Unread Message

`action code: 'getUnread'`

### Keep Online √

`entry code: 'online'`

| Part I | Part II |
|:------:|:-------:|
|Username|  Token  |

This action will refresh the last seen time. Server will check the client if
it is online. When the client is timeout, this will trigger the log out
action. (@logout)

> Suggest using other function call to refresh the last seen time.

> Any other function except `logout` will refresh the last seen time.

## Security

### Validate Server

> I don't think this action has any meaning. Once the sever can decrypt the
message, of course it's the server.

### Play back Attack

See in function `util.Operator.filterReplayAttack()`
