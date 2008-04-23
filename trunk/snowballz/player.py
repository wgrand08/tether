from __future__ import division
import ai
import data



class Player(object):
    def __init__(self, name, type, color):
        self.connection = None
        self.loading = False
        self.name = name
        self.type = type
        self.color = color
        self.train_worker_que = 0
        self.train_snowballer_que = 0

        self._make_glcolor()

        self.alert_tiles = {}
        self.snowballer_alert_range = 40

        self.open_resources = set()

        self.victory = None

        self.ai = ai.Ai(self)

    def _make_glcolor(self):
        self.glcolor = []
        for c in self.color:
            if c > 1:
                c = c/255
            self.glcolor.append(c)

    def send_msg(self, msg):
        if msg[0] == "/" or msg[0] == ">":
            msg = msg.split()
            cmd = msg.pop(0)
            msg = " ".join(msg)
        else:
            cmd = "/say"

        if cmd == "/say":
            # Send to everyone.
            data.messages.send(msg, self, None)

        elif cmd[0] == ">":
            # Send to just one player.
            pname = cmd[1:]
            for p in data.players.values():
                if p.name == pname:
                    data.messages.send(msg, self, p)
                    break
        #if player == data.player:
            #self.game.display.messages.add((self.game.get_ticks(), msg, self.color))

    def _get_victory(self):
        return self._victory
    def _set_victory(self, v):
        if hasattr(self, "player_id") and self._victory is not v and \
                data.THIS_IS_SERVER:
            import networking
            networking.send(networking.MPlayerVictory(self.player_id, v))
        self._victory = v
    victory = property(_get_victory, _set_victory)

    def handle_MPlayerVictory(self, m):
        print m.victory
        self.victory = m.victory

    def is_alive(self):
        for r in data.map.regions.values():
            if r.player == self:
                return True
        return False
