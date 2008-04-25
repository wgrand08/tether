=============================
README: Snowballz
=============================

:Author: Joey Marshall
:Contact: web@joey101.net

Description
-----------
Snowballz is a fun little game in which you engage your group of penguins in a snowball fight.

Run
---
To run the game, simply run snowballz.py

$ python snowballz.py

How to play
-----------


Controls
~~~~~~~~

.. image:: /static/snowballz/snapshot6.png
    :class: section-screenshot

You can control snowballers (not workers) by selecting them (either by clicking on them or dragging a select box around them) and right clicking to tell them to do something.

Left click to select, right click to perform an action. If you right click somewhere, they will move and stay there until they get cold or you tell them to go somewhere else. Snowballers that don't have any orders (they are cleared when they get cold), will walk around their home igloo. Penguins get cold when hit by snowballs.

To disband your units (make them go stray around their igloos) by pressing the **o** key. You can also make your penguins run somewhere without stopping to throw at enemies by middle clicking instead of right clicking.

You can move the screen around by using the arrow keys or **aswd** keys. Hold down on space to bring up a nice big minimap.

Zoom in and out with the page-up and page-down keys. Note that for now it might be a little slow when zoomed out!

Chat
^^^^
To send a chat message, first press enter to bring up the chat box. Once up, simply type your message and press enter again. Your message will be sent to everyone! If you want to send to just one person, you can type::

    >playername Hi playername! This is a privet message!

playername being the name of the person you want to send a chat message to.

There is tab completion too! So you can type ">" then hit TAB to see all players that you can send a private chat to. Two useful shortcuts you can use are the "," and "." keys. Press the period when you aren't in chatmode and it will bring up the chatbox to send a message to the last person that sent a private chat to you. The "," works the same way except to the last person you sent a private chat to.

If you ever have a bunch of chats on your screen that you just want to get rid of, you can press the **c** key to clear them all.


Takeover!
~~~~~~~~~

.. image:: /static/snowballz/snapshot8.png
    :class: section-screenshot

If you tell a snowballer to move to an enemy igloo (by right clicking on it), it will run without stopping until it gets into it. If you can hold the enemy igloo for 30 seconds, it, the region, and all penguins belonging to the igloo will become yours.

Be careful though, if an enemy snowballer enters the igloo you are taking over, your penguin will be shown the door with a cold snowball in his face.

Penguins (on either side) can not exit an igloo that is in the middle of a takeover.

When an igloo is being taken over, the penguins belonging to that igloo will go bananas. The workers will just run around in a panic and the snowballers will rush to try to save it in time not listening to your orders. (actually, the workers don't do that yet, but they will!)

On the bottom right corner of igloos there is a marker designating which player that igloo belongs to. When an igloo is in jeopardy (being taken over), that marker turns multicolored.


Warming and reassigning
~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /static/snowballz/snapshot7.png
    :class: section-screenshot

When a penguin gets cold from being hit with too many snowballs, it will run madly back to it's home igloo (you won't be able to control it again until it's warm). Once back in it's igloo, it can take up to 40 seconds to get warmed up (depending on how cold it was when going in)! It also requires a fish before it will go back out if it's warmth was below a certain level (your workers will automatically gather fish).

If you tell a snowballer to enter one of your igloos (again, by right clicking on it), it will enter it. Immediately after entering, the igloo you told it to go to becomes it's home igloo. If it is all the way warm, it will exit immediately. Otherwise it will stay for a snack and warm up.


Terrain types
~~~~~~~~~~~~~
In the game you will come across two different types of land; Ice and snow. Really the only difference between the two is that snowballers can only create snowballs on snow (not ice).

Try to catch your enemy on the the ice with your snowballers standing on the snow. If you can, you'll cream 'em!


Playing tips
~~~~~~~~~~~~

.. image:: /static/snowballz/snapshot5.png
    :class: section-screenshot

When one of your penguins enters their igloo and is only a little bit cold, they won't eat a fish but will still get warm. The colder the penguin, the longer they take to warm up!

You can gain a strategic advantage in a snowball fight if your penguins are among some trees while your opponents aren't. Snowballs that hit trees have no effect on surrounding penguins.

Normally, a snowball that lands next to a penguin brings it's warmth down just a little while a direct hit will bring it down a lot. If your penguins get close enough to their enemy, they are much more accurate!

One mean strategy you can use against your opponent when they are between your army and their own igloo is to send one of your penguins into their igloo. This will make your penguin run without stop towards their igloo distracting the enemy. This will give your snowballers a chance to get a handle on the situation. If your snowballer does manage to get into their igloo, all of their snowballers will panic and race to it, and stop throwing their snowballs!


Credits
-------
See AUTHORS file.
