import os
from dotenv import load_dotenv
import string
import disnake
from disnake.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
load_dotenv()

bot = commands.Bot(command_prefix="-")
bot.remove_command('help')
case_insensitive = True
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET")))

@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="/help"))
    print(f"{bot.user} is online")

@bot.slash_command()
async def help(inter):
    """
    Commands and Additional Information about this bot
    """
    embed = disnake.Embed(title="Querify",
                          description="Use this bot to search Spotify and more!\n(This Bot uses the Spotify API)",
                          color=0x8792c6)
    embed.add_field(
        name="Now using Slash Commands!",
        value=
        "`/track <name>` - search a track\n`/album <name>` - search a album\n`/artist <name>` - search a artist\n[[Invite]](https://discord.com/api/oauth2/authorize?client_id=936725976753254511&permissions=0&scope=bot%20applications.commands)",
        inline=True)
    embed.set_footer(text="Querify | bot by gorgonzola#6770")
    await inter.response.send_message(embed=embed)

@bot.slash_command()
async def track(inter, name: str):
    """Search Spotify for a Track/ Song

    Parameters
    ----------
    name: What track do you want to lookup?
    """
    results = sp.search(q=name.lower(), type="track", limit=20, offset=0)
    try:
      await inter.response.send_message(results['tracks']['items'][0]['external_urls']['spotify'])
    except IndexError:
      await inter.response.send_message(f"No track found for `{track}`")
        

@bot.slash_command()
async def album(inter, name: str):
    """Search Spotify for a Album

      Parameters
      ----------
      name: What album do you want to lookup?
    """
    results = sp.search(q=name.lower(), type="album", limit=20, offset=0)
    try:
      album_id = results['albums']['items'][0]['id']
      tracks = sp.album_tracks(album_id=album_id, limit=30, offset=0, market="US")

      tracklist = []
      for c in range(tracks['total']):
          name = tracks['items'][c]['name'].replace("*", "\*")
          tracklist.append(f"{c + 1}. {name}")
      tracklist = "\n".join(tracklist)

      embed = disnake.Embed(
          title=results['albums']['items'][0]['artists'][0]['name'],
         color=0x8792c6)
      embed.set_thumbnail(url=results['albums']['items'][0]['images'][1]['url'])
      embed.add_field(name=results['albums']['items'][0]['name'],
                     value=f"{tracklist}**\n[LISTEN ON SPOTIFY]({results['albums']['items'][0]['external_urls']['spotify']})**",
                     inline=True)
      await inter.response.send_message(embed=embed)
    except IndexError:
      await inter.response.send_message(f"No album found for `{album.title()}`.")

@bot.slash_command()
async def artist(inter, name: str):
  """Search Spotify for a Artist

    Parameters
    ----------
    name: What artist do you want to lookup?
  """
  artist = sp.search(q=name.lower(), type="artist", limit=20, offset=0)
  try:
    artist_id = artist['artists']['items'][0]['id']
    top_tracks = sp.artist_top_tracks(artist_id=artist_id, country="US")

    tracklist = []
    for c in range(5):
        name = top_tracks['tracks'][c]['name'].replace("*", "\*")
        tracklist.append(f"{c + 1}. **[{name}]({top_tracks['tracks'][c]['external_urls']['spotify']})**")
    genres = [string.capwords(x, sep=None) for x in artist['artists']['items'][0]['genres']]
    followers_count = format(artist['artists']['items'][0]['followers']['total'],
                        ",")
    tracklist = "\n".join(tracklist)

    embed = disnake.Embed(title=artist['artists']['items'][0]['name'],
                          color=0x8792c6)
    embed.set_thumbnail(url=artist['artists']['items'][0]['images'][2]['url'])
    embed.add_field(name="General Information:",
                    value=f"Genres: `{', '.join(genres)}`\nFollowers: `{followers_count}`\n Popularity: `{str(artist['artists']['items'][0]['popularity'])}/100`",inline=False)
    embed.add_field(name="Top 5 Songs:", value=tracklist, inline=False)
    await inter.response.send_message(embed=embed)
  except IndexError:
    await inter.response.send_message(f"No artist found for `{artist.title()}`.")

bot.run(os.getenv("TOKEN"))
