# itunes-cli

A command line interface to iTunes for Mac OS X, written in Python.

## Setup

Like any other else, run

```
$ python setup.py install
```

## Usage

```
usage: itunes [-h] [--index INDEX] [--artists] [--albums] [--library]
              [--songs] [--playlists] [--quiet]
              command [query [query ...]]
              
positional arguments:
  command
  query

optional arguments:
  -h, --help            show this help message and exit
  --index INDEX, -i INDEX
  --artists, -a
  --albums, -b
  --library, -l
  --songs, -s
  --playlists, -p
  --quiet, -q
```

### Commands

Generally, you use this utility like `itunes <command>`, where the commands are described below.

One particularly nifty feature is command auto-completion. Rather than type out `itunes play`, you can simply type out `itunes pla` or `itunes pl` or `itunes p` and the completion will be inferred.

#### Playback and querying

As you'd expect, the "play" command tells iTunes to start playing.

If you specify a query to search for, it will play something in particular. This query can be incomplete and span multiple words; it literally hooks right into iTunes' search functionality, so anything you can search for via the iTunes search bar you can search for here.

By default, it will search within whatever playlist you're playing, or you can tell it to search across your whole library using the `--library` flag.

You can limit your search to artists, albums, songs, or playlists using the appropriate flags. If your query matches multiple songs, they'll be presented to you, and you can either use a more limiting query or pick one out of the list using `--index`. If you want to play all of the matches, you can use `--index all`.

You can suspend playback using `stop` and navigate through your playlist with `next` and `back`. (I chose `stop` over `pause` so that `itunes p` can be used to play and `itunes s` can be used to stop, rather than `itunes p` being ambiguous).

You can control shuffling using `toggle-shuffle`.

#### Viewing iTunes' status

The `info` command displays iTunes' state, including whether or not shuffling is enabled, what song is currently playing, and even a nice progress bar that shows how much of the song is left.

If you're using the queue feature to queue up songs to play (e.g. playing an album or using `--index all`), you can use the `list-queue` command to view the current contents of the queue and your position in it.

#### Convenience

If you omit the command altogether, `itunes` will assume you meant `play`, so you can simply run `itunes <song name>` if you want to listen to a song.

If you don't specify `--library`, it will look in whatever playlist you're currently listening to. (This doesn't apply to `--playlist` searches).

### Examples

```
# Lists all of the songs in my library with the word "Radiohead"
~$ itunes -l radiohead
More than one result. (Try a better query, or specify an index using -i/--index):
| index   | name                                     | artist    | album                                  |
| ------- | ---------------------------------------- | --------- | -------------------------------------- |
| 0       | Packt Like Sardines in a Crushd Tin Box  | Radiohead | Amnesiac                               |
| 1       | Pyramid Song                             | Radiohead | Amnesiac                               |
| 2       | Pulk/Pull Revolving Doors                | Radiohead | Amnesiac
...
```

```
# ...and plays the first one
~$ itunes radiohead -i 0
Playing Packt Like Sardines in a Crushd Tin Box by Radiohead on Amnesiac
```

```
# Finds and plays a playlist with the query "top rated"
~$ itunes -p top rated
Playing playlist My Top Rated
```

```
# Shows current song status
~$ itunes i
iTunes is playing.
Shuffling is on

Current Track:
    Brianstorm
    Arctic Monkeys
    Brianstorm

               0:54
[###############-----------------------------------] 2:49
```

```
# Enqueues all of the songs on an album containing "origin"
~$ itunes -b origin
Queuing music on Origin of Symmetry by Muse
```

```
# Displays play queue and position
~$ itunes list-queue
    New Born
    Bliss
 >  Space Dementia
    Hyper Music
    Plug In Baby
    Citizen Erased
    Micro Cuts
    Screenager
    Darkshines
    Feeling Good
    Megalomania
```

## Limitations

This is currently only available on Mac OS X and only tested on iTunes 11. This is because it uses AppleScript to interface with iTunes because there isn't really an iTunes API aside from AppleScript. This makes it unlikely to be portable to non-OS X systems anytime soon.

I also rely on System Events to navigate iTunes' menu bar as a very hacky way of determining shuffle status and toggling shuffling. (AppleScript's shuffling APIs currently don't appear to work on iTunes 11.)

## Licensing

Don't do anything evil with this (not sure how you would, but...). You may use the code for whatever. Attribution would be nice. Don't sell this to anyone, etc.