from __future__ import division

import struct
from cStringIO import StringIO

#import pyraknet
#from pyraknet import PacketTypes, PacketReliability, PacketPriority

import socket, traceback, os, sys, threading
from Queue import Queue

from unit import Unit
from buildings.igloo import Igloo
from player import Player
import data, snowball

# This will be assigned to the pyraknet Peer instance.
net = None

def send(message, to="*", exclude=()):
    """
    This is mostly a shortcut to send a message over the network.

    It will fail silently if there is no network connection.
    """
    if net:
        if isinstance(net, Server):
            net.send(message, to, exclude)
        else:
            net.send(message)

unit_states = ["idle", "walking", "frozen", "throwing", "gathering", "entering",
        "inbuilding", "unloading", "getting_snowball", "stray"]
holding_types = [None, "fish", "crystal"]


class Connection(object):
    def __init__(self, sock, recv_queue=None):
        self.sock = sock
        self.send_queue = Queue() # Strings
        if recv_queue:
            self.recv_queue = recv_queue
        else:
            self.recv_queue = Queue() # Message objects
        # recv_queue might be reassigned in another thread.  (e.g., the server
        # might want all connections so share a single queue after they have
        # been authenticated.  Thus, this lock should be held before accessing
        # or reassigning the queue.  (Unless if it is being accessed in the
        # only thread it is ever reassigned in.)
        self.recv_queue_lock = threading.Lock()

        self.send_thread = threading.Thread(target=self.send_loop)
        self.send_thread.setDaemon(1)
        self.recv_thread = threading.Thread(target=self.receive_loop)
        self.recv_thread.setDaemon(1)
        self.send_thread.start()
        self.recv_thread.start()

    def replace_recv_queue(self, new_queue):
        """
        This will assign a new queue for receiving messages for this connection.
        All required locking will be done, and any messages left in the old
        queue will be added to the new one.
        """
        self.recv_queue_lock.acquire()
        while not self.recv_queue.empty():
            new_queue.put(self.recv_queue.get(True), True)
        self.recv_queue = new_queue
        self.recv_queue_lock.release()

    def send_loop(self):
        try:
            #bytes = 0
            #last_print = 0
            while True:
                d = self.send_queue.get(True)
                self.sock.sendall(d)
                #bytes += len(d)
                #if data.get_ticks() > last_print + 1000:
                    #last_print = data.get_ticks()
                    #print "sent kB:", bytes/1000.
                    #bytes = 0
        except:
            print "****** Exception while sending: ****************"
            traceback.print_exc()
            self.sock.close()

    def receive_loop(self):
        try:
            while True:
                type_id = struct.unpack("!B", self.read(1))[0]
                cls = indexed_message_classes[type_id]
                m = cls.from_stream(self)
                m.connection = self
                self.recv_queue_lock.acquire()
                self.recv_queue.put(m, True)
                self.recv_queue_lock.release()
                #print "*** Received ****", m
        except:
            print "****** Exception while receiving: **************"
            traceback.print_exc()
            self.sock.close()

    def send(self, message):
        """
        Queues a message up for sending.

        Takes a single argument, ``message``, which can either be a ``Message``
        object or a string.
        """
        if isinstance(message, basestring):
            self.send_queue.put(message)
        else:
            self.send_queue.put(struct.pack("!B", message.type_id) +
                    message.pack())

    def read(self, count):
        """
        Reads exactly ``count`` bytes from the socket.
        """
        d = self.sock.recv(count, socket.MSG_WAITALL)
        assert len(d) == count
        return d



class Server(object):
    def __init__(self, port):
        self.connections = set()
        self.recv_queue = Queue()
        self.port = port

    def start(self):
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.setDaemon(1)
        self.listen_thread.start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", self.port))
        s.listen(1)
        while True:
            try:
                clientsock, clientaddr = s.accept()
            except:
                traceback.print_exc()
                continue
            self.new_connection(Connection(clientsock))

    def new_connection(self, connection):
        self.connections.add(connection)
        connection.replace_recv_queue(self.recv_queue)

    def send(self, message, to="*", exclude=()):
        if isinstance(message, Message):
            message = struct.pack("!B", message.type_id) + message.pack()
        if to == "*":
            to = set(self.connections)
        for connection in to:
            if connection in exclude or not connection: continue
            connection.send(message)


def send_chat_message(msg, from_player, to_player=None):
    if to_player:
        to_id = to_player.player_id
    else:
        to_id = 0xffff
    m = MChatMessage(msg, from_player.player_id, to_id)
    if data.THIS_IS_SERVER:
        if to_player:
            send(m, to=[to_player.connection])
        else:
            send(m, exclude=[from_player.connection])
    else:
        net.send(m)

class Writer(object):
    def __init__(self, data=None):
        if data is None:
            data = StringIO()
        self.data = data

    def single(self, format, *values):
        if format[0] not in "@=<>!":
            format = "!"+format
        self.data.write(struct.pack(format, *values))

    def multi(self, format, values):
        self.single("!H", len(values))
        if len(format.strip("@=<>!")) > 1:
            for v in values:
                self.single(format, *v)
        else:
            for v in values:
                self.single(format, v)

    def string(self, s):
        self.multi("s", s)

class Reader(object):
    def __init__(self, data):
        if not hasattr(data, "read"):
            data = StringIO(data)
        self.data = data


    def single(self, format):
        if format[0] not in "@=<>!":
            format = "!"+format
        return struct.unpack(format, self.data.read(struct.calcsize(format)))

    def multi(self, format, limit=1000):
        length = self.single("!H")[0]
        if length > limit:
            raise RuntimeError("multi length (%d) is above limit (%d)!!" %
                    (length, limit))
        if len(format.strip("@=<>!")) > 1:
            for i in range(length):
                yield self.single(format)
        else:
            for i in range(length):
                yield self.single(format)[0]

    def string(self):
        return "".join(self.multi("s"))


class Message(object):
    type_id = None
    struct_format = None
    attrs = None
    def __init__(self, *pargs, **kwargs):
        attrs = list(self.attrs)
        for arg in pargs:
            n = attrs.pop(0)
            setattr(self, n, arg)
        for n in attrs:
            setattr(self, n, kwargs.pop(n))
        if kwargs:
            raise TypeError("unexpected keyword argument '%s'" %
                    kwargs.keys()[0])

    def values(self):
        l = []
        for a in self.attrs:
            l.append(getattr(self, a))
        return l

    @classmethod
    def from_stream(cls, stream):
        res = struct.unpack(cls.struct_format,
                stream.read(struct.calcsize(cls.struct_format)))
        return cls(*res)

    def pack(self):
        return struct.pack(self.struct_format, *[getattr(self, n) for n in
                self.attrs])

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__,
                dict([(a, getattr(self, a)) for a in self.attrs]))


# Unit stuff

class MUnitPosition(Message):
    type_id = 100
    struct_format = "!HhhbbBB"
    attrs = ('unit_id', 'x', 'y', 'dir_x', 'dir_y', 'state_id', 'holding_id')

# 101 is free

class MUnitAddEmblem(Message):
    type_id = 102
    attrs = ("unit_id", "image_name", "animate", "offset")
    def pack(self):
        w = Writer()
        w.single("H", self.unit_id)
        w.string(self.image_name)
        w.single("B", self.animate)
        w.single("hh", *self.offset)
        return w.data.getvalue()
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(r.single("H")[0], r.string(), bool(r.single("B")),
                r.single("hh"))

class MUnitRemoveEmblem(Message):
    type_id = 103
    struct_format = "!H"
    attrs = ("unit_id",)
    # TODO support removing only one emblem, instead of all.


class MWarmth(Message):
    type_id = 104
    struct_format = "!HB"
    attrs = ("unit_id", "warmth")

class MSnowball(Message):
    type_id = 105
    struct_format = "!HIIIIHHBHH"
    attrs = ("unit_id", "start_x", "start_y", "end_x", "end_y", "end_tile_x",
            "end_tile_y", "snowballs_left", 'px', 'py')


class MUnitIglooChange(Message):
    type_id = 109
    struct_format = "!HH"
    attrs = ("unit_id", "building_id")

# Building stuff

class MBuildingOwner(Message):
    type_id = 110
    struct_format = "!HH"
    attrs = ('building_id', 'player_id')

class MBuildingJeopardy(Message):
    type_id = 111
    struct_format = "!HBH"
    attrs = ('building_id', 'jeopardy', 'player_taking_over_id')

class MBuildingStorage(Message):
    type_id = 112
    struct_format = "!Hhh"
    attrs = ("building_id", 'fish', 'crystal')


class MCreateDynamicMapObject(Message):
    type_id = 114
    attrs = ("dmo_id", "image_name", "position", "obstruction", "hidden",
            "minimapimage")
    def pack(self):
        w = Writer()
        w.single("H", self.dmo_id)
        w.string(self.image_name)
        w.single("HH", *self.position)
        w.single("B", (self.hidden << 0) + (self.obstruction << 1))
        w.string(self.minimapimage)
        return w.data.getvalue()
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        dmo_id = r.single("H")[0]
        image_name = r.string()
        pos = r.single("HH")
        v = r.single("B")[0] # Two bools are in one byte.
        o = bool(v & 2) # second bit
        h = bool(v & 1) # first bit
        mini = r.string()
        return cls(dmo_id, image_name, pos, o, h, mini)

class MDMOHidden(Message):
    type_id = 115
    struct_format = "!HB"
    attrs = ("dmo_id", "hidden")

class MDMOPosition(Message):
    type_id = 116
    # TODO


class MResourceQuantity(Message):
    type_id = 117
    struct_format = "!hhh"
    attrs = ("tx", "ty", "q")


# Player/connection stuff

class MNewPlayer(Message):
    type_id = 120
    attrs = ("player_id", "name", "color", "loading")
    def pack(self):
        w = Writer()
        w.single("H", self.player_id)
        w.string(self.name)
        w.single("BBB", *self.color)
        w.single("B", self.loading)
        return w.data.getvalue()
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(r.single("H")[0], r.string(), r.single("BBB"),
                bool(r.single("B")[0]))

class MWhoYouAre(Message):
    type_id = 121
    struct_format = "!H"
    attrs = ("player_id",)

class MSetJob(Message):
    type_id = 122
    attrs = ("pos", "run_mode", "unit_ids")
    def pack(self):
        w = Writer()
        w.single("HH", *self.pos)
        w.single("B", self.run_mode)
        w.multi("H", self.unit_ids)
        return w.data.getvalue()

    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        pos = r.single("HH")
        run_mode = bool(r.single("B")[0])
        unit_ids = list(r.multi("H"))
        return cls(pos, run_mode, unit_ids)

class MDisbanUnits(Message):
    type_id = 123
    attrs = ("unit_ids",)
    def pack(self):
        w = Writer()
        w.multi("H", self.unit_ids)
        return w.data.getvalue()

    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(list(r.multi("H")))

class MClientFinishedLoading(Message):
    type_id = 124
    struct_format = "!H"
    attrs = ("player_id",)


class MGameStart(Message):
    type_id = 224
    struct_format = ""
    attrs = ()

class MChatMessage(Message):
    type_id = 225
    attrs = ("msg", "from_id", "to_id")
    def pack(self):
        w = Writer()
        w.string(self.msg)
        # to_id will be 0xffff to specify everyone.
        w.single("HH", self.from_id, self.to_id)
        return w.data.getvalue()
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(r.string(), *r.single("HH"))

class MPlayerVictory(Message):
    type_id = 226
    attrs = ("player_id", "victory")
    def pack(self):
        return struct.pack("!Hs", self.player_id,
                {True:'t', False:'f', None:'n'}[self.victory])
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(r.single("H")[0],
                dict(t=True, f=False, n=None)[r.single("s")[0]])

class MMapname(Message):
    type_id = 227
    attrs = ("mapname",)
    def pack(self):
        w = Writer()
        w.string(self.mapname)
        return w.data.getvalue()
    @classmethod
    def from_stream(cls, stream):
        r = Reader(stream)
        return cls(r.string())

message_classes = [MUnitPosition, MBuildingOwner, MBuildingJeopardy,
        MBuildingStorage, MSnowball, MWarmth, MNewPlayer, MWhoYouAre, MSetJob,
        MDisbanUnits, MCreateDynamicMapObject, MDMOHidden, MDMOPosition,
        MResourceQuantity, MUnitAddEmblem, MUnitRemoveEmblem, MGameStart,
        MChatMessage, MUnitIglooChange, MClientFinishedLoading, MPlayerVictory,
        MMapname]

indexed_message_classes = {}
for cls in message_classes:
    indexed_message_classes[cls.type_id] = cls

class NetLoopBase(object):
    def handle_network(self):
        while not self.net.recv_queue.empty():
            message = self.net.recv_queue.get()
            if not self.handle_message(message):
                print "Unhandled message: ", message

    def handle_message(self, message):
        attr = "handle_" + message.__class__.__name__
        if hasattr(self, attr):
            getattr(self, attr)(message)
            return True
        else:
            return False


class MasterUnit(Unit):
    def __init__(self, *pargs, **kwargs):
        self.observers = []
        Unit.__init__(self, *pargs, **kwargs)
        self._last_state_sent = self.state

    def _set_warmth(self, w):
        self._warmth = w
        if hasattr(self, "unit_id"):
            send(MWarmth(self.unit_id, w))
    warmth = property(lambda self:self._warmth, _set_warmth)

    #def _set_max_warmth(self, mw):
        #self._max_warmth = mw
        #self.call_remote("update_max_warmth", mw)
    #max_warmth = property(lambda self:self._max_warmth, _set_max_warmth)

    def _set_igloo(self, i):
        self._igloo = i
        if hasattr(self, "unit_id") and hasattr(i, "building_id"):
            send(MUnitIglooChange(self.unit_id, i.building_id))

    def move(self):

        pos = self.x, self.y
        Unit.move(self)
        if pos != (self.x, self.y) or (self.state != self._last_state_sent and
                    self.state not in ['throwing', 'getting_snowball']):
            send(MUnitPosition(self.unit_id, self.x, self.y,
                    self.direction[0], self.direction[1],
                    unit_states.index(self.state),
                    holding_types.index(self.holding)))
        self._last_state_sent = self.state

    def throw_snowball(self, target):
        s = Unit.throw_snowball(self, target)
        send(MSnowball(self.unit_id, s.start_x, s.start_y, s.end_x, s.end_y,
                s.end_tile.x, s.end_tile.y,
                self.snowballs, self.x, self.y))
        self._last_state_sent = "throwing"
        return s

    def add_emblem(self, emblem):
        m = MUnitAddEmblem(self.unit_id, emblem.image_name, emblem.animate,
                emblem.offset)
        send(m)
        Unit.add_emblem(self, emblem)

    def remove_emblem(self, emblem):
        if emblem in self._emblems:
            send(MUnitRemoveEmblem(self.unit_id))
        Unit.remove_emblem(self, emblem)


class SlaveUnit(Unit):
    def __init__(self, *pargs, **kwargs):
        Unit.__init__(self, *pargs, **kwargs)
        # State of the unit will be set later.
        self._next_position = None
        self._next_snowball = None

    def handle_MUnitPosition(self, m):
        state = unit_states[m.state_id]
        holding = holding_types[m.holding_id]
        self._next_position = ((m.x, m.y), (m.dir_x, m.dir_y), state, holding)

    def handle_MSnowball(self, m):
        self.snowballs = m.snowballs_left
        #self.current_frame = 1
        dir = self.direction_to_tile(m.end_tile_x, m.end_tile_y)
        self._next_position = ((m.px, m.py), dir, "throwing", None)
        end_tile = data.map.tiles[(m.end_tile_x, m.end_tile_y)]
        self._next_snowball = (m.start_x, m.start_y, m.end_x, m.end_y, end_tile)

    def handle_MWarmth(self, m):
        self.warmth = m.warmth

    def handle_MUnitIglooChange(self, m):
        try:
            self.igloo = data.buildings[m.building_id]
        except KeyError:
            pass

    def handle_MUnitAddEmblem(self, m):
        self.add_emblem(Emblem(m.image_name, m.animate, m.offset))

    def handle_MUnitRemoveEmblem(self, m):
        for e in list(self._emblems):
            self.remove_emblem(e)

    def move(self):
        startxy = self.x, self.y
        try_next_position = True
        if self.state == "throwing" and self.current_frame < 9:
            # We don't want to process a new state if we are still in a throw.
            try_next_position = False
        elif self.moving:
            time_passed = data.get_ticks()-self.counter
            self.offset = int(time_passed/self.walk_speed*32)
            if self.offset < 32:
                try_next_position = False
        if try_next_position:
            self.offset = 0
            if self._next_position:
                p, self.direction, self.state, self.holding = self._next_position
                if (self.x, self.y) == p:
                    self.moving = False
                else:
                    self.moving = True
                self.x, self.y = p
                self._next_posision = None
                if self.state == "throwing" and self._next_snowball:
                    # We need to throw a snowball!
                    self.current_frame = 1
                    data.snowballs.add(snowball.Snowball(*self._next_snowball))
                    self._next_snowball = None
                    self.moving = False
                    if self.snowballs == 0:
                        self._next_position = ((self.x, self.y), self.direction,
                                "getting_snowball", None)
                self.counter = data.get_ticks()
            else:
                self.moving = False
        endxy = self.x, self.y
        if startxy != endxy:
            self.move_sprites(startxy, endxy)


class MasterIgloo(Igloo):
    def __init__(self, *pargs, **kwargs):
        self.observers = set()
        Igloo.__init__(self, *pargs, **kwargs)

    def _set_player(self, player):
        if player != self.player:
            Igloo._set_player(self, player)
            send(MBuildingOwner(self.building_id, player.player_id))
    player = property(Igloo._get_player, _set_player)

    def _set_jeopardy(self, j):
        self._jeopardy = j
        if hasattr(self, 'building_id'):
            send(MBuildingJeopardy(self.building_id, j, 
                    self.player_taking_over.player_id))
    jeopardy = property((lambda self:self._jeopardy), _set_jeopardy)

    def storage_changed(self):
        Igloo.storage_changed(self)
        m = MBuildingStorage(self.building_id, self.num_storage('fish'),
                self.num_storage('crystal'))
        send(m)

class SlaveIgloo(Igloo):

    def handle_MBuildingOwner(self, m):
        # This will change the player of all the units too.
        if m.player_id in data.players:
            p = data.players[m.player_id]
            if p != self.player:
                self.player = p
                self.region.player = p

    def handle_MBuildingJeopardy(self, m):
        self.jeopardy = bool(m.jeopardy)
	self.player_taking_over = data.players[m.player_taking_over_id]
	self.jeopardy_count = data.get_ticks()

    def handle_MBuildingStorage(self, m):
        self._storage['fish'] = m.fish
        self._storage['crystal'] = m.crystal
        self.storage_changed()



from plugin import Emblem, DynamicMapObject, BaseDynamicMapObject

class SlaveDynamicMapObject(BaseDynamicMapObject):
    def handle_MDMOHidden(self, m):
        self.hidden = bool(m.hidden)



