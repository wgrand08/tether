"""Copyright 2008:
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

class Game:
    def __init__(self):
        #this section handles all logging for both client and server
        self.logger = logging.getLogger('MoonPy')
        self.filehdlr = logging.FileHandler('MoonPy.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.filehdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.filehdlr)
        self.logger.setLevel(logging.INFO)
