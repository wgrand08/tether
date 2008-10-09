# OpenRTS - Copyright (C) 2006 The OpenRTS Project
#
# OpenRTS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# OpenRTS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

import logging
from twisted.spread import pb
from twisted.cred.portal import IRealm
import cPickle
import zlib
from time import sleep

from conninfo import *


#****************************************************************************
#
#****************************************************************************
"""Code for handling both incoming and outgoing networks commands for the server, equivalent to networkclient.py for the client. Everything with 'perspective' in front of it is for commands coming in from a client."""
class ClientPerspective(pb.Avatar):
  def __init__(self, conn_info, conn_handler, serverstate):
    self.conn_info = conn_info;
    self.state = serverstate;
    self.handler = conn_handler;

#****************************************************************************
# Todo: Add error handling.
#****************************************************************************
  def network_prepare(self, object):
    data = cPickle.dumps(object);
    compressed = zlib.compress(data);
    return compressed;

#****************************************************************************
#
#****************************************************************************
  def network_handle(self, string):
    data = zlib.decompress(string);
    object = cPickle.loads(data);
    return object;


#****************************************************************************
#client connects to game
#****************************************************************************
  def perspective_login(self, username, version):
    if version != self.state.settings.version:
      return "login_failed";
    else:
      self.conn_info.username = username;
      self.conn_info.playerID = self.state.max_players(self.handler.clients);
      join_message = "%s has joined the game" % username;
      self.handler.remote_all('chat', join_message);
      join_message = "as playerID %s" % self.conn_info.playerID;
      self.handler.remote_all('chat', join_message);
      return self.conn_info.playerID; 

#****************************************************************************
#command that everyone is ready and the game actually starts
#****************************************************************************
  def perspective_init_game(self):
    self.state.setup_new_game();
    net_map = self.network_prepare(self.state.map.mapstore); 
    net_unit_list = self.network_prepare(self.state.map.unitstore); 
    self.handler.remote_all('map', net_map);
    self.handler.remote_all('unit_list', net_unit_list);
    self.handler.remote_all('start_client_game');
    self.state.currentplayer = 1; #player1 goes first 
    self.handler.remote_all('next_turn', self.state.currentplayer);

#****************************************************************************
# recieve command for launching a unit, signifying a players turn is done
#****************************************************************************
  def perspective_launch_unit(self, parentID, unit, rotation, power):
    coord = self.state.find_trajectory(parentID, rotation, power, unit, self.conn_info.playerID);
    if self.state.interrupted_tether == False:
        self.state.add_unit(unit, coord, self.conn_info.playerID, parentID);
        net_map = self.network_prepare(self.state.map.mapstore); 
        net_unit_list = self.network_prepare(self.state.map.unitstore); 
        self.handler.remote_all('map', net_map);
        self.handler.remote_all('unit_list', net_unit_list);
        self.handler.remote(self.conn_info.ref, 'confirmation'); #send message confirming unit is placed and maps updated
        self.state.determine_hit(unit, coord);
    self.state.process_death();
    net_map = self.network_prepare(self.state.map.mapstore); 
    net_unit_list = self.network_prepare(self.state.map.unitstore); 
    self.handler.remote_all('map', net_map);
    self.handler.remote_all('unit_list', net_unit_list);
    self.state.currentplayer += 1;
    if self.state.currentplayer > self.state.max_players(self.handler.clients):
        self.state.currentplayer = 1;
    self.handler.remote_all('next_turn', self.state.currentplayer);

#****************************************************************************
#recieve command indicating that this player is skipping all turns until round is over
#****************************************************************************
  def perspective_skip_round(self):
    self.state.skippedplayers = self.state.skippedplayers + 1;
    if self.state.skippedplayers >= self.state.max_players(self.handler.clients):
        self.skippedplayers = 0;
        self.handler.remote_all('next_round');
    self.state.currenplayer = 1; #todo: add code to randomize/rotate the starting player for each round
    self.handler.remote_all('next_turn', self.state.currentplayer);

#****************************************************************************
#forward chat information to all clients
#****************************************************************************
  def perspective_send_chat(self, data):
    message = self.conn_info.username + ": " + self.network_handle(data);
    self.handler.remote_all('chat', message);

#****************************************************************************
#client disconnecting from server
#****************************************************************************
  def logout(self):
    logging.info("logged out");
    del self.handler.clients[self.conn_info.ref];
    #need to add code to handle players that are no longer in the game


#****************************************************************************
#
#****************************************************************************
class ConnectionHandler:
  __implements__ = IRealm

  def __init__(self, serverstate):
    self.state = serverstate;
    self.clients = {}

#****************************************************************************
#send data to all clients
#****************************************************************************
  def remote_all(self, methodName, *args):
    dfs = [self.remote(c, methodName, *args) for c in self.clients]
    return dfs 

#****************************************************************************
#send data to a single client
#****************************************************************************
  def remote(self, client, method_name, *args):
    return client.callRemote(method_name, *args);

#****************************************************************************
#server information about each player
#****************************************************************************
  def requestAvatar(self, name, client_ref, *interfaces):
    logging.info("Client connected.");
    if pb.IPerspective in interfaces:
      address = client_ref.broker.transport.getPeer()
      playerID = 0
      conn_info = ConnInfo(client_ref, name, address, playerID);
      perspective = ClientPerspective(conn_info, self, self.state);
      self.clients[client_ref] = conn_info;
      return (pb.IPerspective, perspective, perspective.logout); 
    else:
      raise NotImplementedError("no interface");


