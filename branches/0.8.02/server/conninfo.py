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

import logging

#****************************************************************************
#
#****************************************************************************
class ConnInfo:
    def __init__(self, client_ref, name, address, playerID, energy, Idisabled, reload, Ireloading):
        self.ref = client_ref
        self.name = name
        self.username = None
        self.address = address
        self.playerID = 0
        self.energy = 11
        self.undisable = False
        self.Idisabled = []
        self.reload = False
        self.Ireloading = []
