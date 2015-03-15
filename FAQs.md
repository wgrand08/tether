# FAQs of project tether #

#### What is project tether? ####
Project tether is an open source project focused on recreating the classic strategy game [Moonbase commander](http://en.wikipedia.org/wiki/Moonbase_Commander)

#### What is Moonbase Commander? ####
Moonbase Commander has quite often been called "the best game no one has ever heard of". It is the first and most well known ATS game. If you've never played an ATS, most people describe it as a unique combination of Starcraft and Scorched Earth but that doesn't say much. The best way to find out what Moonbase Commander is like is to play the game.

#### Well then where can I go to play Moonbase Commander? ####
Do a web search and you can find places online that still sell it for cheap. There used to be a trial but that is hard to find these days.

#### Moonbase Commander absolutely rocks! Why recreate something thats so perfect? ####
While Moonbase Commander is a great game, there are some flaws and glitches that have never been fixed. Because the game has not received any support or updates from any of the different companies that have owned it for over 10 years we assume that they will never be resolved. Rather then live with it we started this project to resolve these flaws ourselves.

#### Aren't there other ATS games out there that fix those issues? What about Kingdom Commander? ####
There are very few ATS games out there, we've looked. Project Tether was started in 2005 long before Kingdom Commander was announced. While we have no problem with others remaking Moonbase Commander as a commercial venture we remain dedicated to making an open source version as well so that if commercial versions become unprofitable the users won't be stuck like what happened with OMBC. Given that kingdom commander has not updated since 2012 our concerns are justified.

#### What is Scorched Moon? ####
Scorched Moon is our current program we are developing at project tether. It is being designed in two parts, a server and a client. The server is being designed to run as a persistent service on a server that users will be able to connect to using a client and find other players to play with. Kind of like how battle.net works. The client will of course be a graphical system to allow players to connect to the server. To limit cheating all game calculations will take effect on the server and the client merely displays the information.

#### I can't find a download for Scorched Moon, where is it? ####
Scorched Moon is still in early development and has no release packages yet. The code for it is available on SVN if you want to help with testing or just take a look.

#### I downloaded Scorched Moon from SVN but can't figure out how to play or run it ####
Scorched Moon is not playable yet as we are still early in development. Currently the only purpose in running either server or client is for testing purposes.

#### Why is it sometimes months between updates? ####
Because we're all unpaid volunteers, so when we get busy with real life work on Scorched Moon gets put on the back burner.

#### Why are you using python, why not a real programming language like C++? ####
There are many reasons we're using python but the top 3 reasons are: it's simple to code, it's easily portable to different OS's, and it does what we need.

#### What OS are you developing for? ####
We are planning on having Scorched Moon be compatible with Linux, osX, and Windows. The server should theoretically work on any computer with python3 installed while the client should theoretically work on any computer with python3 and pygame for python3 installed.

#### Will any project tether game be compatible with Moonbase Commander? ####
No.

#### Really? Why not? ####
Mostly because Moonbase Commander is essentially dead, practically no one plays it anymore and the networking is pretty unstable to begin with. What we're trying to do is hard enough already and we don't want to go through the hassle of reverse engineering everything for no real benefit. We are making some changes that make Scorched Moon incompatible with the original even if we did manage to reverse engineer everything.

#### What changes were made? ####
The biggest change is the number of players. The original Moonbase Commander can not have more then 4 players in a single game which we found inconvenient. In addition to the change in the player limit. We are also planning on implementing internet play.

#### Changing Moonbase Commander is heresy! Why did you change things? ####
Most of the changes we have listed are things that we felt were flaws in Moonbase Commander. The 4 player limit for example was always a major problem for most of us. Likewise being able to find people to play with and actually being able to play online without a VPN are absolutely essential. Same goes true for most of the other changes listed. We have tried to keep the actual gameplay itself as accurate to the original as we can make it.

#### I think Scorched Moon should do X, why don't you do it? ####
We take suggestions but remember we're all unpaid volunteers doing this out love for Moonbase Commander. If you **really** want something implemented everything we have is open source so feel free to implement it yourself.

#### Where did the MoonPy downloads go? ####
Since all work has stopped on MoonPy we have deprecated it so the OS specific downloads are no longer available. The source tar.gz package is available on the download page though you'll have to search for deprecated files to see them. It is also available as a branch on SVN. You can also sometimes find it on some 3rd party sites like playdeb.

#### I have no clue what you just said, is there an easier way to download MoonPy? ####
We don't support MoonPy anymore so basically no.

#### I found a bug, what do I do? ####
Great, identifying them is (usually) the hardest part. Remember though that we've stopped development on MoonPy so we will ignore bug reports for it. If you have found a problem with Scorched Moon it's still in very early development so chances are we're already aware of it even if it's not listed on the [issue tracker](http://code.google.com/p/tether/issues/list).

#### How can I help out with the project? ####
We can always use some help to keep this going. Currently the biggest help we need is people to help us code it. In addition to help with the code we also could use graphics, sounds, music, documentation, etc. We also could also use a server to use as an official game host. You can always check out the [issue tracker](http://code.google.com/p/tether/issues/list), or post onto our [mailing list](http://groups.google.com/group/project-tether). Also just spreading the word about project tether is a big benefit to us as well. The more people interested, the more likely someone with skills we need will be able to help.

#### I've been looking through the MoonPy source code archives and keep seeing mention of openRTS, is project tether a part of openRTS? ####
openRTS is a completely separate project from project tether. We have however integrated code from various other open source projects to help speed up development of project tether. The MoonPy engine is a heavily modified version of the openRTS engine and as such elements of openRTS occasionally show up, especially in older versions of MoonPy. Currently very little of the original openRTS engine remains unchanged within MoonPy, we do however have the original unedited openRTS source files deprecated on our [downloads page](http://code.google.com/p/tether/downloads/list) for reference and historical purposes. Scorched Moon shares no code at all with openRTS.