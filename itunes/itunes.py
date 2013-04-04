import sys
import argparse
from appscript import app, k

# Reference to the iTunes application
iTunes = app('iTunes')
# Reference to System Events, used for shuffling
SystemEvents = app('System Events')

# iTunes 11 introduced an internal play queue that AppleScript currently
# cannot interact with. As a workaround, we create a playlist that behaves
# like a play queue for playing albums or particular query matches.
PLAY_QUEUE_NAME = 'itunes_play_queue'
playQueue = iTunes.user_playlists[PLAY_QUEUE_NAME]

def is_shuffling():
    """Is the iTunes player shuffling?
    
    Returns a boolean value indicating whether or not the iTunes
    player is currently shuffling songs.
    
    Relies on System Events to acquire this information.
    """
    # In iTunes 11, Apple for some reason appear to have broken the
    # shuffling AppleScript interface, so we have to use System Events
    # to actually go query/interact with the menu items to control
    # shuffling.
    return 'Off' in SystemEvents.processes['iTunes'].menu_bars[1] \
                    .menu_bar_items['Controls'].menus[1]          \
                    .menu_items['Shuffle'].menus[1].menu_items[1] \
                    .title()

def toggle_shuffle(*args, **kwargs):
    """Toggle shuffling in the iTunes player.
    
    Relies on System Events.
    """
    SystemEvents.processes['iTunes'].menu_bars[1] \
    .menu_bar_items['Controls'].menus[1]          \
    .menu_items['Shuffle'].menus[1].menu_items[1] \
    .actions['AXPress'].perform()

def get_where(songs, artists, albums):
    # Helper function; used to find the right flags to query
    where = k.all
    if songs:
        where = k.songs
    elif artists:
        where = k.artists
    elif albums:
        where = k.albums
    return where

def do_query(query, songs, artists, albums, playlists, library):
    """Queries the iTunes database.
    
    The 'songs' and 'playlists' flags determine what kinds of
    results are considered.
    
    If 'library' is enabled, searches the full library.
    Otherwise, searches the current playlist.
    """
    if playlists:
        lists = iTunes.user_playlists.name()
        matches = set()
        for name in lists:
            if query.lower() in name.lower():
                matches.add(name)
        return matches
    
    where = get_where(songs, artists, albums)        
    if library:
        playlist = iTunes.playlists['Library']
    else:
        playlist = iTunes.current_playlist()
    
    return iTunes.search(playlist, for_=query, only=where)
    

def play(*query, **kwargs):
    """Implementation of the "play" command."""
    
    index       =   kwargs['index']
    songs       =   kwargs['songs']
    artists     =   kwargs['artists']
    albums      =   kwargs['albums']
    playlists   =   kwargs['playlists']
    library     =   kwargs['library']
    quiet       =   kwargs['quiet']
    
    if index is not None:
        if index.isdigit():
            index = int(index)
        
        if index < 0:
            print "Invalid index", index
            return
    
    if not query:
        iTunes.play()
    else:
        query = ' '.join(query)
        matches = do_query(query, songs, artists, albums, playlists, library)
        
        if matches is None:
            print "No matches found"
            if not library:
                print '(Searching current playlist "{}". ' \
                    'Did you mean to search the whole library? Try --library/-l)' \
                    .format(iTunes.current_playlist.name())
            return
        
        if playlists:
            lists = iTunes.user_playlists.name()
            if len(matches) == 1 or index is not None:
                if index is None:
                    index = 0
                if index >= len(matches):
                    print "No playlist at index", index
                else:
                    name = list(matches)[index]
                    print 'Playing playlist "{}"'.format(name)
                    iTunes.user_playlists[name].play()
            else:
                print "More than one result. "\
                    "(Try a better query, or specify an index using -i/--index):"
                for i, name in enumerate(matches):
                    print "{:<5} {}".format(i, name)
            return
        
        where = get_where(songs, artists, albums)        
        if library:
            playlist = iTunes.playlists['Library']
        else:
            playlist = iTunes.current_playlist()
        
        results = iTunes.search(playlist, for_=query, only=where)
        
        def _play(result):
            if not quiet:
                print 'Playing "{}" by "{}" on "{}"'.format(result.name.get(),
                        result.artist.get(), result.album.get())
            result.play()
        
        def _play_all(results):
            if not playQueue.exists():
                iTunes.make(new=k.user_playlist,
                    with_properties={k.name: PLAY_QUEUE_NAME})
            playQueue.tracks.delete()
            for song in results:
                song.duplicate(to=playQueue)
            if is_shuffling():
                # When playing multiple results, we disable shuffling
                # (The expected behavior is usually to play them in
                #  order)
                toggle_shuffle()
            playQueue.play()
        
        if len(results) == 0:
            print "No results"
            return
        
        if len(results) == 1:
            index = 0
        
        if len(results) >= 1:
            if index is not None:
                if type(index) == int:
                    if index < len(results):
                        _play(results[index])
                    else:
                        print "No song at index", index
                elif index == 'all':
                    _play_all(results)
                else:
                    print "Invalid index", index
                return
            
            table = []
            longest = [0, 0, 0]
            artist_set = set()
            album_set = set()
            
            MAXLEN = 40
            for (i, song) in enumerate(results):
                name, artist, album = song.name.get(), song.artist.get(), song.album.get()
                longest[0] = min(MAXLEN, max(longest[0], len(name)))
                longest[1] = min(MAXLEN, max(longest[1], len(artist)))
                longest[2] = min(MAXLEN, max(longest[2], len(album)))
                artist_set.add(artist)
                album_set.add(album)
                table.append((i, name, artist, album))
            
            if artists and len(artist_set) == 1:
                if not quiet:
                    print "Queuing music by", iter(artist_set).next()
                _play_all(results)
                return
            
            if albums and len(album_set) == 1:
                if not quiet:
                    anysong = results[0]
                    print "Queuing music on", anysong.album(), "by", anysong.artist()
                _play_all(results)
                return
            
            if (artists and len(artist_set) == 1) or (albums and len(album_set) == 1):
                _play(results)
                return
            
            if index is not None:
                _play(results[index])
            else:
                fmt = ('| {{:<7}} | ' + '{{:<{}}} | '*3).format(*longest)
                print "More than one result. " \
                      "(Try a better query, or specify an index using -i/--index):"
                print fmt.format('index', 'name', 'artist', 'album')
                print fmt.format(*map(lambda x: '-'*x, [7]+longest))
                for (i, song) in enumerate(results):
                    name = song.name.get()
                    artist = song.artist.get()
                    album = song.album.get()
                    
                    if len(name)   > longest[0]: name   = name[:longest[0]-3]   + '...'
                    if len(artist) > longest[1]: artist = artist[:longest[1]-3] + '...'
                    if len(album)  > longest[2]: album  = album[:longest[2]-3]  + '...'
                    
                    print fmt.format(i, name, artist, album)

def info(*args, **kwargs):
    """Implementation of the "info" command."""
    
    state = iTunes.player_state()
    if state == k.stopped:
        print "iTunes is not playing."
        return
    if state == k.playing:
        print "iTunes is playing."
    elif state == k.paused:
        print "iTunes is paused."
    else:
        print "iTunes is in an unknown state", state
    try:
        print "Shuffling is {}".format("on" if is_shuffling() else "off")
    except:
        print "Cannot determine shuffling status."
    print
    
    try:
        playlist = iTunes.current_playlist()
        if playlist == iTunes.playlists['Library']():
            print "Playing entire library."
        elif playlist == playQueue():
            print "Playing queued songs."
        else:
            print "Playing playlist:", playlist.name()
    except:
        print "Cannot determine which playlist is playing."
    
    try:
        track = iTunes.current_track()
        pos = iTunes.player_position()
        
        print "Current Track:"
        print "\tTitle:  ", track.name()
        print "\tArtist: ", track.artist()
        print "\tAlbum:  ", track.album()
        print "\tRating: ", "*" * (track.rating()//20)
        print
        print make_pbar(pos, track.duration())
    except:
        print "Can't get current track."
    print

def make_pbar(curr, total):
    MAX = 50
    bar = int(float(curr)/total * MAX)
    fmt_time = lambda t: "{}:{:02}".format(int(t/60), int(t-t//60*60))
    curr_str = fmt_time(curr)
    total_str = fmt_time(total)
    return "{}{}\n[{}{}] {}".format(bar*' ', curr_str, bar*'#', '-'*(MAX-bar), total_str)

def list_queue(*args, **kwargs):
    if iTunes.current_playlist() != playQueue():
        print "Not playing from queue; only playing a single song."
        print "(Want information about the song? Try the 'info' command)"
    else:
        playing = iTunes.current_track()
        for song in playQueue.tracks():
            if song == playing:
                print " > ",
            else:
                print "   ",
            print song.name()

def parse_seek(s):
    """Translates a seek command to a player position.
    
    Seek positions may be deltas of the forms:
        +secs
        +mins:secs
        -secs
        -mins:secs
    or they may be absolute times.
    """
    
    def parse_mins_secs(s):
        secs = 0
        if ':' in s:
            i = s.index(':')
            secs += int(s[:i])*60
            s = s[i+1:]
        secs += int(s)
        return secs
    
    if s[0] in '+-':
        # it's a delta
        sign = s[0]
        s = s[1:]
        secs = parse_mins_secs(s)
        delta = secs
        if sign == '-':
            delta *= -1
        return iTunes.player_position() + delta
    else:
        # it's an absolute time
        secs = parse_mins_secs(s)
        return secs
            

def seek(*args, **kwargs):
    if len(args) < 1:
        print "You haven't specified how much to seek by or where to seek to."
        print "For example:"
        print "   itunes seek +10   (seek 10 seconds forward)"
        print "   itunes seek -1:10 (seek 1 minute and 10 seconds back)"
        print "   itunes seek 2:35  (seek to 2 minutes and 35 seconds in)"
        print "(Looking for the current seek time? Try the 'info' command)"
    else:
        iTunes.player_position.set(parse_seek(args[0]))

commands = {
    'play': play,
    'info': info,
    'toggle-shuffle': toggle_shuffle,
    'list-queue': list_queue,
    'stop': lambda *args, **kwargs: iTunes.pause(),
    'next': lambda *args, **kwargs: iTunes.next_track(),
    'back': lambda *args, **kwargs: iTunes.back_track(),
    'seek': seek
}

def main():
    parser = argparse.ArgumentParser(description='Command line querying interface to control iTunes on Mac OS X')
    parser.add_argument('command', default='play')
    parser.add_argument('--index', '-i', type=str)
    parser.add_argument('--artists', '-a', action='store_true')
    parser.add_argument('--albums', '-b', action='store_true')
    parser.add_argument('--library', '-l', action='store_true')
    parser.add_argument('--songs', '-s', action='store_true')
    parser.add_argument('--playlists', '-p', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('query', nargs='*')
    args, query = parser.parse_known_args()
    args = vars(args)
    args['query'] += query
    
    if args['command'] not in commands:
        matches = set()
        for cmd in commands:
            if cmd.lower().startswith(args['command'].lower()):
                matches.add(cmd)
        if len(matches) == 1:
            args['command'] = iter(matches).next()
        elif len(matches) > 1:
            print "Command '{}' is ambiguous (could be any of {})".format(args['command'], ", ".join(matches))
            return
        else:
            args['query'].insert(0, args['command'])
            args['command'] = 'play'
    
    commands[args['command']](*args['query'], **args)

if __name__ == '__main__':
    main()