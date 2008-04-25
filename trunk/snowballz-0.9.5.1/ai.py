import random
import data

class Ai:
    gather = None
    guard_pos = None
    gather_force = 0

    def __init__(self, player):
        self.player = player
        self.units = set()
        self.units_attacking = set()
        self.units_guarding = set()
        self.being_attacked = False
        self.warring_players = set()
        self.personalities = [Offensive(self), Revengefull(self)]
        self.spite = {}
        self.regions = set()
        self.send_msgs = set()
        self.workers = []


    def send_msg(self, msg, from_player):
        msg = msg.lower()
        wrds = msg.split()
        sendto = "player"
        if "hi" in wrds or "hello" in wrds:
            reply = "Hi"
        elif "bye" in msg:
            reply = "Yes, %s, adieu!" % from_player.name
        elif "how" in wrds and "are" in wrds and "you" in wrds:
            reply = "Better than a n00b like you!"
        elif ("freez" in msg or "froz" in msg or "cold" in msg) and "you" in msg:
            reply = "Don't worry, I'll be sure to make it up to you!"
        elif "die" in msg:
            reply = "No no, YOU die! MUHAHAHAHA"
            self.spite[from_player.name] = 5
        elif "dum" in msg or "stupid" in msg or "idiot" in msg:
            reply = "I'll take that as a compliment"
        elif "fair" in msg:
            reply = "Life isn't fair!"
        elif "bot" in msg:
            reply = "What's a bot? I'm not a bot! You're the bot! DIE BOT!"
        elif "go" in wrds and "away" in wrds:
            reply = "I'll go away when I want to!"
        elif "no" in msg:
            reply = "YEEEEES!"
        elif "attack" in msg or "stop" in msg:
            reply = "Uuu... no!"
        elif "thank" in msg:
            reply = "You're quite welcome!"
        elif "loser" in msg:
            reply = "All hail %s, king of the losers!" % from_player.name
            sendto = "all"
        else:
            reply = "Stop babbling"

        if sendto is "player":
            self.send_msgs.add(">%s %s"%(from_player.name, reply))
        else:
            self.send_msgs.add(reply)


    def setup(self):
        for r in data.map.regions.values():
            if r.player == self.player:
                self.regions.add(r)
        self.get_units()

    def get_units(self):
        # TODO: Run everytime a region changes hands.
        self.units = set()
        self.workers = []
        for u in data.units:
            if u.igloo.player == self.player:
                if u.type == "snowballer":
                    self.units.add(u)
                else:
                    self.workers.append(u)

        # Gather any necicary resources.
        if self.gather:
            for w in self.workers:
                w.disban()
            for w in self.workers[0:int(len(self.workers)*(self.gather_force/100.0))]:
                w.going_for = self.gather


    def attack(self, r):
        if not r.player:
            return
        for personality in self.personalities:
            if hasattr(personality, "find_target"):
                target_pos = personality.find_target(r)
                break

        selected_units = set()
        max_selection = len(self.units.difference(self.units_attacking))
        for u in self.units:
            if len(selected_units) >= max_selection:
                break
            if not u in self.units_attacking and u.warmth > 4:
                selected_units.add(u)
        for u in selected_units:
            u.target_pos = target_pos
            self.units_attacking.add(u)

        if not r.player in self.warring_players:
            self.warring_players.add(r.player)
            if not self.spite.has_key(r.player.name):
                self.spite[r.player.name] = 0

            if self.spite[r.player.name] > 6:
                pass
            elif self.spite[r.player.name] > 4:
                self.player.send_msg(">%s DIE DIE DIE!!!"%r.player.name)
            elif self.spite[r.player.name] > 3:
                self.player.send_msg(">%s You are getting on my nerves... prepare to die!"%r.player.name)
            elif self.spite[r.player.name] > 1:
                self.player.send_msg(">%s hmm... I think I'll attack... YOU! MUHAHAHA!!"%r.player.name)
            elif self.spite[r.player.name] >= 0:
                self.player.send_msg(">%s I think I'll try picking on you... no hard feelings"%r.player.name)


    def run(self):
        for m in self.send_msgs:
            self.player.send_msg(m)
        self.send_msgs = set()

        # See if it has taken over any regions.
        for r in data.map.regions.values():
            if r.player is self.player and not r in self.regions:
                self.regions.add(r)
                for u in self.units_attacking:
                    u.target_pos = None
                    u.go_to_building = None
                self.units_attacking = set()
                self.warring_players = set()
                break


        # See if it needs to gaurd anywhere.
        if self.guard_pos:
            if not self.units_guarding:
                free_units = self.units.difference(self.units_attacking)
                guarding_units = 0
                for u in free_units:
                    if guarding_units > len(self.units.difference(self.units_attacking))/3:
                        break
                    self.units_guarding.add(u)
                    guarding_units += 1

            for u in self.units_guarding:
                u.target_pos = self.guard_pos
            # Hack to get guarding units out other control.
            self.units = self.units.difference(self.units_guarding)



        # See if it wants to attack anyone.
        attack_regions = {}
        for region in data.map.regions.values():
            if region.player != self.player:
                #for r in region.adjacent_regions:
                    #if r.player != self.player:
                attack_regions[region] = 0
                for personality in self.personalities:
                    attack_regions[region] += personality.attack_region(region)


        best_option = None
        for (r,amount) in attack_regions.items():
            if not best_option:
                best_option = (r,amount)
            else:
                if amount > best_option[1]:
                    best_option = (r,amount)
                elif amount == best_option[1]:
                    if random.randint(0,1):
                        best_option = (r,amount)

        if best_option:
            if best_option[1] > 0:
                self.attack(best_option[0])

        for u in list(self.units_attacking):
            if u.target_pos == None and u.go_to_building == None:
                # Unit isn't attacking any more.
                self.units_attacking.remove(u)

        if len(self.units_attacking) < 3:
            # Retreat!
            for u in list(self.units_attacking):
                u.target_pos = None
                u.go_to_building = u.igloo
                self.units_attacking.remove(u)

                #for p in self.warring_players:
                    #self.player.send_msg(p, "Ack! I must retreat for now... but I'll back!")
                self.warring_players = set()

        enemy_in_regions = {}
        for unit in data.units:
            # Find all enemy units in owned region. If too many, flag as being attacked.
            pos = (unit.x,unit.y)
            if data.map.tiles[pos].region.player is self.player and\
                    unit.player != self.player and\
                    unit.warmth > 4:
                if not enemy_in_regions.has_key(data.map.tiles[pos].region):
                    enemy_in_regions[data.map.tiles[pos].region] = [1,unit.player]
                else:
                    enemy_in_regions[data.map.tiles[pos].region][0] += 1

        self.being_attacked = False
        for (r,(amount,enemy)) in enemy_in_regions.items():
            if amount >= 4:
                # Defend!
                self.being_attacked = True
                for u in self.units_attacking:
                    if u.igloo.region == r:
                        u.target_pos = None

                for personality in self.personalities:
                    personality.attacked_by(enemy)


        # Check to see if it can takeover.
        currently_attacking_regions = {}
        for u in self.units_attacking:
            region = data.map.tiles[(u.x,u.y)].region
            if not currently_attacking_regions.has_key(region):
                currently_attacking_regions[region] = [1, u]
            else:
                currently_attacking_regions[region][0] += 1

        for (region, (amount, unit)) in currently_attacking_regions.items():
            try_takeover = True
            #for u in region.igloo.units_in_building:
                #if u.player == self.player:
                    ## Already taking over
                    #try_takeover = False
                    #for u in self.units_attacking:
                        #if u.go_to_building:
                            #for personality in self.personalities:
                                #if hasattr(personality, "find_target"):
                                    #target_pos = personality.find_target(region)
                                    #break
                            #u.target_pos = target_pos
                    #print "already taking over"
                    #break
            if try_takeover and amount >= 2 and region.igloo:
                num_enemy = 0
                for u in data.map.unit_nodes.get_objs_around_tile((region.igloo.x,region.igloo.y)):
                    if u.igloo.player is not self.player and u.type == "snowballer" and u.warmth > 4:
                        num_enemy += 1
                # FIXME: needs to get it relitive to how many of owned units are there.
                if num_enemy <= 1:
                    # FIXME: needs to get closest unit to igloo.
                    unit.go_to_building = region.igloo
                    unit.last_tiles = []
                    unit.target_pos = None




class Offensive:
    def __init__(self, ai):
        self.ai = ai

    def attack_region(self, r):
        if len(self.ai.units) - len(self.ai.units_attacking) < 4:
            return -10
        warm_units = cold_units = 0
        for u in self.ai.units:
            if u.warmth < 5:
                cold_units += 1
            else:
                warm_units += 1
        if warm_units < 5:
            return -20
        if self.ai.being_attacked == True:
            return -5
        if len(self.ai.warring_players) > 0:
            return -8
        return 5

    def find_target(self,r):
        for b in data.buildings:
            if b.region == r:
                return (b.x,b.y)

    def attacked_by(self, player):
        pass

class Revengefull:
    def __init__(self, ai):
        self.ai = ai
        self.grudges = set()
        self.last_spite_increase = 0
        self.last_grudge_release = 0

    def attack_region(self, r):
        if not r.player:
            return 0
        if not self.ai.spite.has_key(r.player.name):
            self.ai.spite[r.player.name] = 0
        return min(7, self.ai.spite[r.player.name])

    def attacked_by(self, player):
        if not self.ai.spite.has_key(player.name):
            self.ai.spite[player.name] = 0

        if self.last_spite_increase+20000 < data.get_ticks():
            self.ai.spite[player.name] += 1
            self.last_spite_increase = data.get_ticks()

        #for p in self.ai.warring_players:
            #if p is player:
                #continue
            #if self.ai.spite[p.name] > 5:
                #self.ai.player.send_msg(">%s I regret that for now I will have to stop attacking you. \n I'll be back though you little pig!" % p.name)
            #elif self.ai.spite[p.name] > 3:
                #self.ai.player.send_msg(">%s I'll give you a little breather for now... I have more important \n things to worry about than you!" % p.name)
            #elif self.ai.spite[p.name] > 0:
                #self.ai.player.send_msg(">%s I'll stop attacking you for now. I've got some other little twit that I \n need to get rid of." % p.name)
            #elif self.ai.spite[p.name] == 0:
                #self.ai.player.send_msg(">%s Err... nevermind. Some other business came up that I need to tend to." % p.name)

        self.ai.warring_players = set()

        if self.last_grudge_release+30000 < data.get_ticks():
            self.grudges = set()
            self.last_grudge_release = data.get_ticks()


        if not player in self.grudges:
            self.grudges.add(player)
            if self.ai.spite[player.name] > 6:
                pass
            elif self.ai.spite[player.name] > 4:
                self.ai.player.send_msg(">%s Dirty swine, leave me alone!" % player.name)
            elif self.ai.spite[player.name] > 2:
                self.ai.player.send_msg(">%s *SIGH*, just leave me alone will you?!" % player.name)
            elif self.ai.spite[player.name] > 1:
                self.ai.player.send_msg(">%s I see you! Just what do you think you're doing in MY territory?" % player.name)
            elif self.ai.spite[player.name] > 0:
                self.ai.player.send_msg(">%s *AHEM* I would recommend that you leave me alone!" % player.name)
