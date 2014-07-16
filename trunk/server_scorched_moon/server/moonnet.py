"""Copyright 2014:
    Kevin Clement

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import logging

# this class handles network commands for the server

class NetCommands():
    def __init__(self, client, settings):
        logging.debug("")
        self.client = client
        self.settings = settings

    def login(self, checkname):
        logging.debug("")
        badlogin = False
        if checkname.find(" ") != 1: # usernames can not have spaces in them
            badlogin = True
            error.warning("user attempted to login with a space")
        if checkname.find("all"): # user can not be named "all" as this conflicts with chat
            badlogin = True
            error.warning("user attempted to login as room")
        if checkname.find("team"): # user can not be named "team" as this conflicts with chat
            badlogin = True
            error.warning("user attempted to login as team")
        for check in self.player: # make certain username has not already been taken
            if check.username == checkname:
                logging.warning("Duplicate username attempted")
                client.send("error username already taken")
                badlogin = True
        if badlogin == False: # valid login so adding them as a player
            self.player.append(player.Player(client, checkname))
            logging.info("{} logged in from {}" .format(checkname, client.address))
            ID = tools.arrayID(checkname)
            logging.debug("identified arrayID {}" .format(ID))
            logging.debug("identified username = {}" .format(self.player[ID].username))
            client.send("welcome {}" .format(self.player[ID].username))

    def logout(self, name):
        logging.debug("")
        ID = tools.arrayID(name)
        if client == self.player[ID].client: # confirm valid logout command
            logging.info("{} logged out" .format(name))
            del self.player[ID]
        else:
            logging.warning("{} attempted to log out {}" .format(client.address, name))

    def broadcast(self, msg):
        logging.debug("")
        msg = "broadcast " + msg
        for client in self.client:
            client.send(msg)

    def version(self, client):
        logging.debug("")
        client.send("version {}" .format(self.settings.version))

    def chat(self, unformatted):
        logging.debug("unformatted chat request recieved: {}" .format(unformatted))
        try:
            sender, message = unformatted.split(" ", 1) # seperating sender from message
            recipient, message = message.split(" ", 1) # seperating recipient from message
        except:
            logging.warning("Improperly formatted chat command recieved: {}" .format(unformatted))
        else:
            ID = tools.arrayID(sender)
            if client.address == self.player[ID].client.address: # confirm that client sending message matches a user logged in from that particular client
                logging.debug("chat request not spoofed")
                if recipient == "room": # sending message to everyone in the same room
                    checklist = 0
                    for players in self.player:
                        if self.player[ID].room == self.player[checklist].room and ID != checklist: #make certain you don't bounce to yourself
                            logging.info("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                            client.send("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                            checklist += 1
          
                if recipient == "team": # sending message to teammates only
                    if self.player[ID].team != 0: # make certain player trying to team chat is actually on a team
                        checklist = 0
                        for players in self.player:
                            if self.player[ID].team == self.player[checklist].team and ID != checklist: # prevent message from bouncing back to sender
                                logging.info("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                                client.send("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                                checklist += 1
                    else: # silly user tried sending a team message when not on a team
                        client.send("error team chat when not on team")
                        logging.warning("{} sent team chat message when not on team" .format(sender))

                if recipient == self.player[ID].username: # silly user tried sending a message to himself
                    logging.warning("{} tried sending a message to himself" .format(recipient))
                    client.send("error unable to send messages to yourself")
                else:
                    unfound = True
                    for check in self.player: # message isn't to a room or team so must be to a specific user
                        if recipient == self.player[check].username:
                            logging.info("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                            client.send("chat {} {} {}" .format(recipient, self.player[ID].username, message))
                            unfound = False
                    if unfound == False: # no valid user found to send message to
                        logging.warning("{} tried sending message to unknown user {}" .format(self.player[ID].username, recipient))
                        client.send("error unable to send message to {}" .format(recipient))

            else: # someone tried to pretend to be someone else
                client.send("error chatting as invalid user")
                logging.warning("{} attempted to send message as unknown user {}" .format(client.address, sender))
