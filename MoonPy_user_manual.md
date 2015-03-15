# Object of Game #

Destroy your enemies!


# Installation #

  1. Download the version of [MoonPy](http://code.google.com/p/tether/downloads/list/) that corresponds to your OS
  1. If using linux simply use the appropriate package manager to install
  1. If using windows unzip all files and then run MoonPy.exe
  1. If using osX unzip all files, download and install [pygame](http://www.pygame.org/download.shtml) and [PIL](http://www.pythonware.com/products/pil/), then run moon.py


# Playing MoonPy online #

MoonPy has an option on the main menu 'find online game'. Selecting this will automatically connect you to irc.freenode.net channel #moonpy. From here you can find other players more easily. Be aware this isn't a true master server system, when someone chooses to host an automated message will announce this in the chat session along with that players public IP address. Other players can then join that game using the IP address. Be aware that players not in the channel at the time you start hosting won't get the message and so will be unable to join. MoonPy uses port 6112 for it's connections and the host will need to have this port open and/or forwarded in order for others to join.


# Gameplay #

## How to 'move' ##

All units are launched similar to many artillery games, like scorched3D, except with a top down perspective. On your turn select the unit you wish to fire from by clicking on it, only hubs and offenses can be selected this way. The selected unit will always have a direction indicator (a little red line) sticking out out of it. Once selected, choose the direction you wish to fire by holding down the < and > buttons, then choose the weapon you wish to fire. When ready, hold down the fire button. The power indicator will start moving up and down. Releasing the fire button will launch the unit in the direction selected with the power the power indicator ended on.

## Energy, rounds, and turns ##

MoonPy progresses in rounds **and** turns. Each player can launch one unit on their turn. Whenever a unit is launched, energy based on the energy level is used up. All players continue taking turns until they either run out of energy or choose to skip their turns. Once every player has either run out of energy or skipped their turn the round ends. When the round ends all players regain energy.


# Units #

## Level 1 ##

![http://tether.googlecode.com/svn/wiki/images/units/bomb.png](http://tether.googlecode.com/svn/wiki/images/units/bomb.png) Bomb: Most basic weapon, does 3 damage

![http://tether.googlecode.com/svn/wiki/images/units/antiair.png](http://tether.googlecode.com/svn/wiki/images/units/antiair.png) Anti-Air: 3HP, fires a laser that shoots down a single incoming shot within it's range. Requires a turn to reload afterwards

![http://tether.googlecode.com/svn/wiki/images/units/bridge.png](http://tether.googlecode.com/svn/wiki/images/units/bridge.png) Bridge: 3HP, allows tethers and buildings to cross water. Bridges self-destruct if they do not land on water.

![http://tether.googlecode.com/svn/wiki/images/units/cluster.png](http://tether.googlecode.com/svn/wiki/images/units/cluster.png) Cluster Bomb: Splits into 3 mini-bombs midflight. Each mini-bomb does 1 damage

![http://tether.googlecode.com/svn/wiki/images/units/repair.png](http://tether.googlecode.com/svn/wiki/images/units/repair.png) Repair: Restores unit it lands on for 1HP

![http://tether.googlecode.com/svn/wiki/images/units/tower.png](http://tether.googlecode.com/svn/wiki/images/units/tower.png) Tower: 3HP, expands your view in fog of war


## Level 3 ##

![http://tether.googlecode.com/svn/wiki/images/units/emp.png](http://tether.googlecode.com/svn/wiki/images/units/emp.png) EMP: Disables all units within a large radius, also does 2 damage on a direct hit.

![http://tether.googlecode.com/svn/wiki/images/units/missile.png](http://tether.googlecode.com/svn/wiki/images/units/missile.png) Missile: Automatically flys towards the nearest enemy target it detects while being launched, does 3 damage

![http://tether.googlecode.com/svn/wiki/images/units/mine.png](http://tether.googlecode.com/svn/wiki/images/units/mine.png) Mines: 3HP, mines land on the ground and detonate if an enemy gets too close, does 3 damage per mine

![http://tether.googlecode.com/svn/wiki/images/units/recall.png](http://tether.googlecode.com/svn/wiki/images/units/recall.png) Recall: Converts a unit into energy without causing them to explode. Does 3 damage to enemy units and 5 damage to your own.

![http://tether.googlecode.com/svn/wiki/images/units/spike.png](http://tether.googlecode.com/svn/wiki/images/units/spike.png) Spike: Spikes travel down tethers allowing them to hit more then one building and do damage when landing on a tether. Does 3 damage if it lands directly on a unit, 1 damage if it travels down a tether. Spikes can land on tethers and travel down them to deal damage to both ends as well.

![http://tether.googlecode.com/svn/wiki/images/units/balloon.png](http://tether.googlecode.com/svn/wiki/images/units/balloon.png) Balloon: 3HP, expands your view in fog of war, but floats in the air and does not require a tether. (Note: This unit has not yet been implemented)


## Level 7 ##

![http://tether.googlecode.com/svn/wiki/images/units/crawler.png](http://tether.googlecode.com/svn/wiki/images/units/crawler.png) Crawler: 3HP, crawlers travel forward each round until they run into something. At which point they detonate for 4 damage.

![http://tether.googlecode.com/svn/wiki/images/units/collector.png](http://tether.googlecode.com/svn/wiki/images/units/collector.png) Collector: 5HP, provides 3 energy per round if placed on an energy pool. Provides 1 energy per round if placed on normal ground. When destroyed they explode in a large radius for 5 damage

![http://tether.googlecode.com/svn/wiki/images/units/offense.png](http://tether.googlecode.com/svn/wiki/images/units/offense.png) Offense: 3HP, fires weapons at twice the range of a hub, but is unable to launch buildings.

![http://tether.googlecode.com/svn/wiki/images/units/shield.png](http://tether.googlecode.com/svn/wiki/images/units/shield.png) Shield: 3HP, fires a laser that shoots down all incoming shots within it's range. Unlike the anti-air it does not need to reload.

![http://tether.googlecode.com/svn/wiki/images/units/virus.png](http://tether.googlecode.com/svn/wiki/images/units/virus.png) Virus: Infects units, infected units are disabled and can not be used for that turn. During each turn the virus deals one damage to the infected unit and travels down the tether to infect another unit. This continues until all connected units have been infected. Although viruses can deal damage they can not destroy units.

![http://tether.googlecode.com/svn/wiki/images/units/hub.png](http://tether.googlecode.com/svn/wiki/images/units/hub.png) Hub: 5HP, your primary unit. It is capable of launching all other units including other hubs.


## Misc ##
![http://tether.googlecode.com/svn/wiki/images/terrain/tether.png](http://tether.googlecode.com/svn/wiki/images/terrain/tether.png) Tether: Most units are connected to each other by tethers. When a hub is destoyed all tethered units that were launched by that hub are also destroyed. This means if your main hub (the one you start the game with) is destroyed you have lost the game since all units are ultimately connected to that hub. The flashing lights on the tethers always move back towards the center hub.

![http://tether.googlecode.com/svn/wiki/images/terrain/tile_grass.png](http://tether.googlecode.com/svn/wiki/images/terrain/tile_grass.png) Grass: Regular ground, all units can be placed on it.

![http://tether.googlecode.com/svn/wiki/images/terrain/tile_energy.png](http://tether.googlecode.com/svn/wiki/images/terrain/tile_energy.png) Energy Pool: Placing a collector on an energy pool provides extra energy per turn

![http://tether.googlecode.com/svn/wiki/images/terrain/tile_rocks.png](http://tether.googlecode.com/svn/wiki/images/terrain/tile_rocks.png) Rocks: Tethers can cross rocks but buildings that land on them are destroyed

![http://tether.googlecode.com/svn/wiki/images/terrain/tile_water.png](http://tether.googlecode.com/svn/wiki/images/terrain/tile_water.png) Water: All units except for bridges and crawlers are destroyed when landing in water. Bridges can be used to cross water.


# Differences between MoonPy and Moonbase Commander #

Because of fundamental differences between the MoonPy engine and the original Moonbase Commander (OMBC) engine. There are currently some differences between the two. The ones we are planning on fixing have been marked. The others we do not plan on changing but if someone wants to take the code and change it for us they are more then welcome to. Please check the [issue tracker](http://code.google.com/p/tether/issues/list) for more information.
  1. Anti-air's shoot incoming shots automatically: In OMBC when an anti-air detected an incoming shot a little missile would fly out to hit it. This would give players the possibility of hitting something before the anti-air missile hit. In MoonPy anti-air's are now instantaneous just like shields, though they still require one turn to reload.
  1. Spike damage is not based on distance: In OMBC a spike would do 3 damage and depending on how far the spike had to travel down the tether would do less and less damage until it did no damage at all. In MoonPy a spike does 3 damage on a direct hit and only 1 damage if it travels down a tether regardless of how long/short it has to travel. A hit on a tether deals only 1 damage to both ends of the tether.
  1. No unique player colors: In OMBC, players would choose a color that would identify them to other players. In MoonPy all of "your" units are colored green while all enemies are colored red and all allies are colored blue. Although this makes it harder to identify and target a specific person, this change allows us to theoretically have an unlimited number of players rather then the 4 player cap OMBC had.
  1. No balloons: Currently balloons can not be launched out. This is mostly due to the fact coding a 'floating' unit will take a lot of work and since there is no FoW there isn't really any need for balloons at this time. Balloons will be implemented later once FoW is done.
  1. 2D engine: Although OMBC used 2D graphics it was a fully 3D game that paid attention to things like 'up' and 'down' (especially noticeable with towers). MoonPy has a fully 2D engine so there is no height differences with units. Although we do not have any intention of implementing height for units we do plan on eventually implementing height differences for terrain.
  1. Difference in unit radius: Because of the difference in sizing between units and tiles in MoonPy and OMBC, having radius effects at the exact ratio's they were in OMBC results in a very unbalanced game. We have modified the radius effect of some of the weapons so that while they are no longer mathematically the same, the overall effectiveness of the weapons are the same and remain balanced.