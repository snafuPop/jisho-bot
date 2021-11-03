import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from dinteractions_Paginator import Paginator
from builtins import bot
import urllib.parse
from random import choice
from googletrans import Translator
import aiohttp

translator = Translator()

class Language(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  def generate_footer(self, user, embed):
    embed.set_footer(text = "Requested by " + str(user), icon_url = user.avatar_url)

  def generate_error_msg(self, error):
    embed = discord.Embed(title = str(type(error).__name__), description = ":no_entry: " + str(error))
    embed.set_thumbnail(url = "https://4.bp.blogspot.com/-iLWX4m_Pht8/XDXcK2opNnI/AAAAAAABRHg/KkSa_pjFcygNx7-v-5AC12TFp08xNXlIgCLcBGAs/s800/sick_panic_man.png")
    return embed

  def generate_no_results_found_msg(self, term):
    embed = discord.Embed(title = "No results found!", description = "No results found for **{}**.".format(term))
    embed.set_thumbnail(url = "https://4.bp.blogspot.com/-Xce-5TfWV2E/XDXcmL1iOzI/AAAAAAABRLQ/RlZsBIYJvRUisHAZ1XnvbCiEgNQceq9LACLcBGAs/s800/pose_ukkari_man.png")
    return embed

  @cog_ext.cog_slash(name = "jisho", description = "Looks up a word on jisho.org", 
    options = [
      create_option(
        name = "term",
        description = "English, Japanese, Romaji, words, or text.",
        option_type = 3,
        required = True)])
  async def jisho(self, ctx, term: str = None):
    await ctx.defer()
    url = "http://jisho.org/api/v1/search/words?keyword=" + urllib.parse.quote(term, encoding = "utf-8")
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          data = await response.json()
    except Exception as error:
      embed = self.generate_error_msg(error)
      self.generate_footer(ctx.author, embed)
      await ctx.send(embed = embed)
      return

    results = data["data"]
    if not results:
      embed = self.generate_no_results_found_msg(term)
      self.generate_footer(ctx.author, embed)
      await ctx.send(embed = embed)
      return

    embeds = []
    count = 1
    for entries in results[:3]:
      embed = discord.Embed(title = "Results for \"{}\"".format(term), color = ctx.author.color)
      embed.set_thumbnail(url = "https://pbs.twimg.com/profile_images/378800000741890744/43702f3379bdb7d0d725b70ae9a5bd59_400x400.png")

      info = ""
      if "word" in entries["japanese"][0]:
        word = entries["japanese"][0]["word"]
        reading = " (" + entries["japanese"][0]["reading"] +  ") "
      else:
        word = ""
        reading = entries["japanese"][0]["reading"]

      entry_list = []
      last_particle = ""
      for entry in entries["senses"]:
        single_entry = []

        # sometimes particles are null, meaning they adopt the previous, non-blank particle
        if entry["parts_of_speech"]:
          particle = ", ".join(entry["parts_of_speech"])
          single_entry.append(particle)
          last_particle = particle
        else:
          single_entry.append(last_particle)

        # combining definitions
        single_entry.append("; ".join(entry["english_definitions"]))
        entry_list.append(single_entry)

      # storing it into info
      for entry in entry_list:
        if len(entry[0]) != 0:
          info += "\n**{}:** {}".format(entry[0], entry[1])
        else:
          info += "\n{}".format(entry[1])

      # adding a link to the actual jisho page

      info += "\n"
      if len(entries["jlpt"]) != 0:
        info += "\n**jlpt:** {}".format("".join(entries["jlpt"]))
      if len(entries["tags"]) != 0:
        info += "\n**Tags:** {}".format(", ".join(entries["tags"]))
      info += "\n[More Information](https://jisho.org/word/{})".format(word)

      # formally adding it to a field
      embed.add_field(name = "{} {}".format(word, reading), value = info, inline = False)


      self.generate_footer(ctx.author, embed)
      embeds.append(embed)

      count += 1

    paginated_embed = Paginator(bot = self.bot, ctx = ctx, pages = embeds, authorOnly = True)
    await paginated_embed.start()
    #await ctx.send(embed = embed)


def setup(bot):
  bot.add_cog(Language(bot))
