"""Copyright 2009:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

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


import sys
import socket
import string 
import pygame
import gui
import logging
import gettext
import mainmenu
import urllib
from pygame.locals import *
from random import randint


class Universe:
    def __init__(self, client):
        self.client = client
        self.irc=socket.socket() #Create the socket
        self.HOST='irc.freenode.org' #The server we want to connect to
        self.PORT=6667 #The connection port which is usually 6667
        self.NICK=self.client.settings.playername #Users nick on IRC
        self.IDENT='moonpy'
        self.REALNAME='moonpy'
        self.CHANNELINIT='#moonpy' #The default channel for the bot
        self.readbuffer='' 
        self.run_IRC = True
        self.myIP = "Unidentified IP"

#****************************************************************************
# IRC chat screen for finding a game
#****************************************************************************

    def connectIRC(self):
        self.session = str(randint(100, 999)) #this is to help prevent multiple identical nicks
        self.NICK = self.client.settings.playername + "-MoonPy" + self.session 
        self.IDENT='MoonPy-client' + self.session
        self.REALNAME='MoonPy-player' + self.session
        pingit = urllib.urlopen('http://whatismyip.org') #get public IP address from the internet
        self.myIP = pingit.read()
        pingit.close()

        self.irc=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
        self.irc.connect((self.HOST, self.PORT)) #Connect to server
        self.irc.sendall('NICK '+ self.NICK +'\n') #Send the nick to server
        self.irc.sendall("USER Python-IRC host server :" + self.REALNAME + "\n")#Identify to server 


        width = 850
        height = 650
        self.app = gui.Desktop()
        self.app.connect(gui.QUIT, self.app.quit, None)
        container = gui.Container(align=-1, valign=-1)
        table = gui.Table(width=width, height=220)

        table.add(gui.Widget(),0,0)

        #self.message_label = gui.Label(("Pregame setup"))
        table.add(gui.Widget(width=1, height=5), 0, 0)

        self.chat_table = gui.Table(width=width,height=height)

        self.chat_table.tr()
        self.lines = gui.Table()
        self.message_out = StringStream(self.lines)
        self.box = gui.ScrollArea(self.lines, width, height)

        self.chat_table.td(self.box) 

        self.chat_table.tr()
        self.line = gui.Input()
        self.line.style.width = width
        self.chat_table.td(self.line)

        self.chat_table.tr()
        self.chat_table.td(MySpacer(1,1, self.box))

        table.add(self.chat_table, 0, 1)

        table.add(gui.Widget(), 0, 2)
        sub_table = gui.Table(width=140, height=35)
        table.add(sub_table, 0, 3)

        cancel_button = gui.Button(("Cancel"))
        cancel_button.connect(gui.CLICK, self.cancel_callback)
        sub_table.add(cancel_button, 0,0)
        if self.client.ishost == True:
            connect_button = gui.Button(("Start Game"))
            connect_button.connect(gui.CLICK, self.start_callback)
            sub_table.add(connect_button, 1,0)
            

        container.add(mainmenu.MenuBackground(client=self.client, width = self.client.screen.get_width(), height = self.client.screen.get_height()), 0, 0)
        container.add(table, self.client.screen.get_width() / 20, self.client.screen.get_height() / 19)
        #container.add(self.message_label, self.client.screen.get_width() / 2 - 160, self.client.screen.get_height() * 0.315)

        self.message_out.write("System: Connecting to " + self.HOST)

        self.app.init(container)
        self.IRC_loop()


#****************************************************************************
#  internal loop while being connected to IRC
#****************************************************************************
    def IRC_loop(self):

        self.run_IRC = True
        self.irc.settimeout(1)
        while self.run_IRC:
            getinput = True
            try:
                self.readbuffer = self.irc.recv(500)
            except:
                getinput = False

            if getinput == True:
                line = self.readbuffer
                line=line.rstrip() #remove trailing 'rn'
                temp=string.split(self.readbuffer, "\n")
                for line in temp:
                    if line.find('End of /MOTD command.')!=-1: 
                        self.irc.sendall('JOIN ' + self.CHANNELINIT + '\n') #Join a channel
                        self.message_out.write("System: Joined channel " + self.CHANNELINIT)
                    if line.find('PRIVMSG')!=-1 and line.find(self.CHANNELINIT) != -1: 
                        #self.parsemsg(line)
                        line = line.rstrip() #strip message to display only username and message
                        user = line.split('!')
                        user = user[0]
                        user = user[1:]
                        message = line.split(':')
                        message = message[2]
                        output = user + ": " + message
                        self.message_out.write(output)
                        if(line[0]=='PING'): #If server pings then pong
                            self.irc.sendall('PONG '+line[1]+'\n')

            for event in pygame.event.get():
                self.app.event(event)
                if event.type == KEYDOWN and event.key == K_RETURN:
                    text = self.line.value
                    self.line.value = ""
                    self.message_out.write(self.NICK + ": " + text)
                    self.irc.sendall("PRIVMSG " + self.CHANNELINIT + " :" + text + "\n")
                    self.line.focus()
            self.app.repaint()
            self.app.update(self.client.screen)
            pygame.display.flip()

#****************************************************************************
#parse the incoming IRC message
#****************************************************************************
    def parsemsg(self, msg): #this is disabled for the time being
        complete=msg[1:].split(':',1) #Parse the message into useful data
        info=complete[0].split(' ')
        msgpart=complete[1]
        sender=info[0].split('!')
        if msgpart[0]=='`' and sender[0]==OWNER: #Treat all messages starting with '`' as command
            cmd=msgpart[1:].split(' ')
            if cmd[0]=='op':
                s.send('MODE '+info[2]+' +o '+cmd[1]+'n')
            if cmd[0]=='deop':
                s.send('MODE '+info[2]+' -o '+cmd[1]+'n')
            if cmd[0]=='voice':
                s.send('MODE '+info[2]+' +v '+cmd[1]+'n')
            if cmd[0]=='devoice':
                s.send('MODE '+info[2]+' -v '+cmd[1]+'n')
            if cmd[0]=='sys':
                placeholder = True
                #syscmd(msgpart[1:],info[2])
            
        if msgpart[0]=='-' and sender[0]== self.OWNER : #Treat msgs with - as explicit command to send to server
            cmd=msgpart[1:]
            s.send(cmd+'n')

#****************************************************************************
# display chat message
#****************************************************************************
    def show_message(self, message):
        self.message_out.write(message)


#****************************************************************************
# canceling game
#****************************************************************************
    def cancel_callback(self):
        self.run_IRC = False
        self.irc.close()
        self.client.moonaudio.sound("buttonclick.ogg")
        self.app.quit()
        mainmenu.MainMenu(self.client)


#****************************************************************************
# 
#****************************************************************************
class StringStream:
    def __init__(self, lines):
        self.lines = lines

    def write(self,data):
        self.lines.tr()
        self.lines.td(gui.Label(str(data)),align=-1)

#****************************************************************************
# Hack, to scroll to the latest new message.
#****************************************************************************
class MySpacer(gui.Spacer):
    def __init__(self,width,height,box,**params):
        params.setdefault('focusable', False)
        self.box = box
        gui.widget.Widget.__init__(self,width=width,height=height,**params)

#****************************************************************************
# 
#****************************************************************************
    def resize(self,width=None,height=None):
        self.box.set_vertical_scroll(65535)
        return 1,1
