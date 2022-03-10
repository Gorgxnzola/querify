import os
import disnake
from disnake import Message
from disnake.utils import get
from disnake.ext import commands, tasks
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import json

bot = commands.Bot(command_prefix="-", test_guilds=[906881394859470879, 939488113045159956])
bot.remove_command('help')
case_insensitive = True

@bot.event
async def on_ready():
    os.system("clear")
    print(f"{bot.user} is online, Servers in: {len(bot.guilds)}")


@bot.command(name="invite")
async def inviteDef(ctx):
  embed = disnake.Embed(title="Invite Querify", description="[click here!](https://discord.com/api/oauth2/authorize?client_id=936725976753254511&permissions=0&scope=bot)", color=0x8792c6)
  await ctx.send(embed=embed)


@bot.command(name="", aliases=["song", "track"])
async def querifyDef(ctx, *, sfSearch):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")))
    results = sp.search(q=sfSearch, type="track", limit=20, offset=0)
    try:
      await ctx.send(results['tracks']['items'][0]['external_urls']['spotify'])
    except IndexError:
      await ctx.send(f"No track found for `{sfSearch}`")

@bot.command(name="album")
async def albumDef(ctx, *, sfSearch):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")))
    results = sp.search(q=sfSearch, type="album", limit=20, offset=0)
    try:
      albumid = results['albums']['items'][0]['id']
      tracks = sp.album_tracks(album_id=albumid, limit=30, offset=0, market="US")

    #CREATE SONG LIST
      trackslist = ""
      for c in range(tracks['total']):
          name = tracks['items'][c]['name']
          if "*" in name: name = name.replace("*", "^")
          trackslist += f"{c + 1}. {name}\n"

      #DISCORD EMBED
      embed = disnake.Embed(
          title=results['albums']['items'][0]['artists'][0]['name'],
         color=0x8792c6)
      embed.set_thumbnail(url=results['albums']['items'][0]['images'][1]['url'])
      embed.add_field(name=results['albums']['items'][0]['name'],
                     value=f"{trackslist}**[LISTEN ON SPOTIFY]({results['albums']['items'][0]['external_urls']['spotify']})**",
                     inline=True)
      embed.set_footer(text=f"Querify | album requested by: {ctx.author.name}")
      await ctx.send(embed=embed)
    except IndexError:
      await ctx.send(f"No album found for `{sfSearch}`")


@bot.command(name="artist")
async def artistDef(ctx, *, sfSearch):
    #SPOTIPY SETUP
  sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
      client_id=os.getenv("SPOTIPY_CLIENT_ID"),
      client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")))
  artist = sp.search(q=sfSearch, type="artist", limit=20, offset=0)
  try:
    artistid = artist['artists']['items'][0]['id']
    toptracks = sp.artist_top_tracks(artist_id=artistid, country="US")

    #PREPARE EMBED
    trackslist = ""
    
    for c in range(5):
        name = toptracks['tracks'][c]['name']
        if "*" in name: name = name.replace("*", "^")
        trackslist += f"{c + 1}. **[{name}]({toptracks['tracks'][c]['external_urls']['spotify']})**\n"
    genres = ", ".join(artist['artists']['items'][0]['genres'])
    followers1 = format(artist['artists']['items'][0]['followers']['total'],
                        ",")

    #DISCORD EMBED
    embed = disnake.Embed(title=artist['artists']['items'][0]['name'],
                          color=0x8792c6)
    embed.set_thumbnail(url=artist['artists']['items'][0]['images'][2]['url'])
    embed.add_field(name="General Information:",
                    value=f"Genres: `{genres}`\nFollowers: `{followers1}`\n Popularity: `{str(artist['artists']['items'][0]['popularity'])}/100`",inline=False)
    embed.add_field(name="Top 5 Songs:", value=trackslist, inline=False)
    embed.set_footer(text=f"Querify | artist requested by: {ctx.author.name}")
    await ctx.send(embed=embed)
  except IndexError:
    await ctx.send(f"No artist found for `{sfSearch}`")


@bot.command()
async def help(ctx):
    embed = disnake.Embed(title="Querify",
                          description="Use this bot to search Spotify and more! \nI'd like some feedback, give it [here](https://discord.gg/DxjC8Aqszc)",
                          color=0x8792c6)
    embed.add_field(
        name="Commands:",
        value=
        "`-track <title>` - search a track\n`-album <title>` - search a album\n`-artist <name>` - search a artist\n`-invite` - invite this bot",
        inline=True)
    embed.set_footer(text="Querify | a bot by gorgonzola#6770")
    await ctx.send(embed=embed)

COVEROPTIONS = commands.option_enum({"Artist":"artist","Album":"album","Track":"track"})
@bot.slash_command(name="cover", description="get a album's/ track's/ artist's picture on Spotify", guild_ids=[906881394859470879, 939488113045159956])
async def cover(inter, options: COVEROPTIONS, name: str):
  #SPOTIPY LOGIN
  sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
      client_id=os.getenv("SPOTIPY_CLIENT_ID"),
      client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")))
  call = sp.search(q=name.lower(), type=options, limit=5, offset=0)
  embed = disnake.Embed(title=f"{options.capitalize()} Cover", color=0x8792c6)
  try:
    #SETTINGS
    if options == "artist":
      at = call["artists"]["items"][0]
      imgurl, artistname, artisturl = at["images"][0]["url"], at["name"], at["external_urls"]["spotify"]
    if options == "album":
      a = call["albums"]["items"][0]
      imgurl, artistname, artisturl = a["images"][0]["url"], a["artists"][0]["name"], a["artists"][0]["external_urls"]["spotify"]
      embed.add_field(name="Album", value=f'{a["name"]}\n[listen on Spotify]({a["external_urls"]["spotify"]})')
    if options == "track":
      t = call["tracks"]["items"][0]
      imgurl, artistname, artisturl = t["album"]["images"][0]["url"], t["album"]["artists"][0]["name"], t["album"]["artists"][0]["external_urls"]["spotify"]
      embed.add_field(name="Track", value=f'{t["name"]}\n[**LISTEN ON SPOTIFY**]({t["external_urls"]["spotify"]})')
    #SEND RESULT
    embed.set_image(url=imgurl)
    embed.add_field(name="Artist", value=f"{artistname}\n[**SEE ON SPOTIFY**]({artisturl})")
    embed.set_footer(text=f"Querify | Requested by: {inter.author}")
    await inter.response.send_message(embed=embed)
  except IndexError:
    await inter.response.send_message(f"No {options} named `{name}` found.")
    
bot.run(os.getenv("TOKEN"))
