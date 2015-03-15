# Hub and offense firing stats #
OMBC map editor uses a grid system for placing objects such as buildings, water, and energy. Small energy pools only take up one grid square each. By creating a special map with small energy pools being used to mark distance I was able to measure roughly how far shots travel without wind or height differences. Be aware that a single screen (not a map) is an exact 8x8 grid. Also the grid system for the map and the grid system for placing units don't sync 100% with each other. The tiles for the map are bigger then each unit is in the game. Also each unit is bigger then the tethers. I estimate that a tether is about half the size of a hub in both height & width (i.e. 1/4 size).
  * Hub maximum = just under 8.5 grids (though definitely higher then 8 grids)
  * Hub minimum = exactly 2 grids
  * Offense maximum = exactly 15 grids
  * Offense minimum = exactly 2 grids
  * AA's = exactly 3 grids
  * mine = exactly 1 grid

Also note that the number of 'dots' in a tether are not related to the distance traveled and can not be used to measure distance.. Placing a unit at minimum distance in a cardinal direction will consistently have 4 dots but at a diagonal direction will have 5.

# Tether spacing stats #
Tethers can not overlap each other. In OMBC if a player attempts to launch a tethered projectile to close to another tether a warning circle appears and the game will not allow the hub to fire. Using a blank map and firing tethers in a circle we have attempted to measure the minimum angle between tethers. As can be seen in the 2 images below:

![http://tether.googlecode.com/svn/wiki/images/rotation_example1.png](http://tether.googlecode.com/svn/wiki/images/rotation_example1.png)
![http://tether.googlecode.com/svn/wiki/images/rotation_example2.png](http://tether.googlecode.com/svn/wiki/images/rotation_example2.png)

Only 11 tethers can be placed but it isn't even. While I may have made a mistake in placing I did perform this test a couple of times and received this result each time. I believe that when moving the pointer OMBC checks to see if you are within 30 degrees of another tether and prevents you from firing if you are (thereby giving each individual tether a 15 degree leeway on each side). I suspect the last tether is impossible to place because while there is technically a 12th 30 degree slice capable of fitting another tether the 'warning system' see's a 1 degree overlap that really doesn't exist. On a side note I think this is something else we can fix to make the system more even.


# Unit HP #

Amount of HP each unit has
  * Hub = 5
  * Tower = 3
  * Balloon = 1
  * Energy = 5
  * AA = 3
  * Offense = 3
  * Shield = 3
  * Crawler = 3

# Weapon Damage #

Amount of damage each weapon does with a direct hit
  * Bomb = 3
  * Missile = 3
  * Crawler = 4
  * Energy = 6
  * EMP = 2
  * Spike = 3
  * Mines = 3

# Energy Collection #

All players start with 11 energy when they begin the game. Each player automatically gains 7 energy per round. All energy collectors give at least 1 energy per round regardless of placement. All energy collectors on an energy pool give 3 energy per round. All disabled energy collectors provide no energy assuming the round ends with them disabled.

# Disabled Units #

Disabled units become active at the end of next turn of the player that disabled it. For example say player 1 disabled an anti-air owned by player 3 by launching a cluster over it. That particular anti-air will not reactivate until the end of player 1's **next** turn regardless of how many people are actually playing. This applies to EMP's as well.

# EMP Range #

The EMP has the largest radius of effect of any of the weapons. The damage radius is relatively small, about the size of a regular bomb. The EMP affect reaches for half of a hubs throwing distance. Note this is larger then the EMP 'explosion' graphic appears. I tested this by launching a tower at maximum range. I then launched EMP's at various ranges to determine where on the power bar the EMP would still disable the tower and when it would not. Launching the EMP at exactly half power would cause the tower to be disabled but 1 section less and it would not. Of interesting note is that at both halfway and one under the launching hub was not disabled. This means that launching at half power is not exactly half way along the tether. This makes sense since there is a minimum launch radius.


# Mine & anti-air range #

The image below has both the AA and the mines fired at absolute minimum power to help estimate the radius of their 'trigger zones'

![http://tether.googlecode.com/svn/wiki/images/radius_example1.png](http://tether.googlecode.com/svn/wiki/images/radius_example1.png)

As can be seen, the mines are just under the minimum range while anti-airs seem to reach about 25% farther then minimum.

# Power Bar #
The power bar has 18 increments for power levels. It takes just under 3 seconds for it to make one complete pass (both up and down), sadly we are unable to be more accurate in our timing. Based off our best estimates though, this means it will take about 1.5 seconds for the bar to make one incomplete pass (one way). Divide this by 18 and you get 0.083+ seconds for each increment. OMBC most likely works by running the power bar at about .08 seconds per increment. This comes to 2.88 seconds for one complete pass which would explain why it is just under 3 seconds instead of being 3 seconds exactly.

# Networking #
OMBC uses port 47624 for IP games. It uses a port somewhere between 2100 & 2800 for LAN games. Because we don't care about backwards compatibility with OMBC we are using port 6112 instead. This port is used by many other RTS games (most notably starcraft) and will make it easier for users to configure firewall settings when playing MoonPy over a network or the internet.