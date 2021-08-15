import discord, math, random, requests, os
import time, datetime, json, aiohttp
from discord_slash import SlashCommand, SlashContext
from threading import Thread
from discord.ext import commands, tasks
#constants
print("Is it working??")
trusted_users=[]
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
vote_threshold = 5
mathProblems={}
def d():
  global mathProblems
  with open("math_problems.json", "r") as file:
    mathProblems = json.load(fp=file)
  with open("trusted_users.txt", "r") as file:
    for line in file:
      trusted_users.append(int(str(line)))
  while True:
    time.sleep(60) 
    with open("math_problems.json", "w") as file:
      file.write(json.dumps(mathProblems))
    with open("trusted_users.txt", "w") as file2:
      for user in trusted_users:
        file2.write(str(user))
      
t = Thread(target=d)
t.run()
def generate_new_id():
  return random.randint(0, 10**20)
#bot = commands.AutoShardedBot(command_prefix="math_problems.")
bot = commands.Bot(command_prefix="math_problems.")
print(bot)
#@bot.event()
#async def on_command_failure(self,ctx,error):
#  print(error)
#  raise Exception("Testing!")
  
##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list 
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")
@bot.command(help="""Creates a new math problem
math_problems.new_problem <answer> <text>""",brief = "Adds a new math problem to the list!")
async def new_problem(ctx, answer, *args):
  global mathProblems
  question = "".join(args)
  if len(question) > 250:
    await ctx.channel.send("Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.")
  while True:
    problem_id = generate_new_id()
    if problem_id not in mathProblems.keys():
      break

  e = {"answer": answer, "voters": [], "author": ctx.message.author.id, "solvers":[], "question": question}
  mathProblems[problem_id] = e
  await ctx.channel.send("You have successfully made a math problem!")

@bot.command(help = """Sets the vote threshold for problem deletion to the specified value! (can only be used by trusted users)
math_problems.set_vote_threshold <threshold>""", brief = "Changes the vote threshold")
async def set_vote_threshold(ctx,threshold):
  global vote_threshold
  if ctx.message.author.id not in trusted_users:
    await ctx.channel.send("You aren't allowed to do this!")
  vote_threshold=threshold
  for problem in math_problems.keys():
    x = len(mathProblems[problem]["voters"])
    if x > vote_threshold:
      await ctx.channel.send(f"Successfully deleted problem #{problem} due to it having {x} votes, {x-threshold} more than the threshold!")
  await ctx.channel.send(f"The vote threshold has successfully been changed to {threshold}!")
@bot.command(help = "Vote for a problem to be deleted! Once a problem gets more votes than the threshold, it gets deleted! Specify the problem_id in order that I know what problem you want deleted.", brief = "Vote for the deletion of a bad problem using this command")
async def vote(ctx, problem_id):
  global mathProblems
  try:
    if ctx.message.author.id in mathProblems[problem_id]["voters"]:
      await ctx.channel.send("You have already voted for the deletion of this problem!")
      return
  except KeyError:
    await ctx.channel.send("This problem doesn't exist!")
    return
  mathProblems[problem_id]["voters"].append(ctx.channel.author.id)
  await ctx.channel.send("You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote.")
  if len(mathProblems[problem_id]["voters"] >= vote_threshold):
    mathProblems.pop(problem_id)
    await ctx.channel.send("This problem has surpassed the threshold and has been deleted!")
@bot.command(help = "Takes away your vote for the deletion of a problem (just specify problem id)",brief="Takes away a user's vote for the deletion of a problem")
async def unvote(ctx,problem_id):
  global mathProblems
  try:
    if ctx.message.author.id not in mathProblems[problem_id]["voters"]:
      await ctx.channel.send("You aren't voting for the deletion of this problem!")
      return
  except KeyError:
    await ctx.channel.send("This problem doesn't exist!")
    return
  mathProblems[problem_id][voters].pop(mathProblems[problem_id]["voters"].index(ctx.message.author.id))
  await ctx.channel.send("Successfully un-voted for the problem's deletion!")
@bot.command(help="""See if your answer is correct or not!
math_problems.check_answer <problem_id> <answer>""", brief = "See if you got it right on a math problem")
async def check_answer(ctx,problem_id,answer):
  global mathProblems
  try:
    if ctx.message.author.id not in mathProblems[problem_id]["solvers"]:
      await ctx.channel.send("You have already solved this problem!")
      return
  except KeyError:
    await ctx.channel.send("This problem doesn't exist!")
    return

  if mathProblems[problem_id]["answer"] != answer:
    await ctx.channel.send("Sorry..... but you got it wrong! You can vote for the deletion of this problem if it's wrong or breaks copyright rules.")
  else:
    await ctx.channel.send("Yay! You are right.")
    mathProblems[problem_id]["solvers"].append(ctx.message.author.id)
@bot.command(help = """List all problems stored with the bot! 
math_problems.list_all_problems <showSolvedProblems=False>
showSolvedProblems is whether or not to show solved problems. Cuts off after the 1931'st character.""", brief = "List all problems stored with the bot.")
async def list_all_problems(ctx, showSolvedProblems=False):
  e = ""
  e += "Problem Id \t Question \t numVotes \t numSolvers"
  for question in mathProblems.keys():
    if len(e) >= 1930:
      e += "The combined length of the questions is too long.... shortening it!"
      await ctx.channel.send(e[:1930])
      return
    elif not (showSolvedProblems) and ctx.message.author.id in mathProblems[questions]["solvers"]:
      continue
    e += "\n"
    e += question + "\t"
    e += mathProblems[question]["question"] + "\t"
    e += len(mathProblems[question]["voters"] + "\t")
    e += len(mathProblems[question]["solvers"])
@bot.command(help="""Deletes a question (either forcefully by a trusted user or deleting a problem submitted by the user who submitted this command
math_problems.delete_problem force <problem_id> 
for forcefully deleting problems **"force" is required!**
or
math_problems.delete_problem self <problem_id>
**self is required!**""", brief = "Deletes a question (either forcefully by a trusted user or deleting a problem submitted by the user who submitted this command")
async def delete_problem(ctx,selfE, problem_id):
  global mathProblems
  if selfE not in ["force", "self"]:
    await ctx.channel.send("Invalid first argument!")
    return
  if problem_id not in mathProblems.keys():
    await ctx.channel.send("That problem doesn't exist! Use math_problems.list_problems to list all problems!")
    return
  if selfE == "force":
    if ctx.message.author.id not in trusted_users:
      await ctx.channel.send("You aren't a trusted user!")
      return
    mathProblems.pop(problem_id)
  else:
    if mathProblems[problem_id]["author"] != ctx.message.author.id:
      await ctx.channel.send(f"You aren't the author of Problem #{problem_id}!")
      return
    mathProblems.pop(problem_id)
@bot.command(help="""Adds a trusted user (can only be used by trusted users)
math_problems.add_trusted_user <user_nick>""", brief = "Adds a trusted user (can only be used by trusted users)")
async def add_trusted_user(ctx,user_nick):
  if ctx.message.author.id not in trusted_users:
    await ctx.channel.send("You aren't a trusted user!")
    return
  s = ctx.message.server
  user_id = s.get_member_named(user_nick).id
  if user_id == None:
    await ctx.channel.send(f"{user_nick} isn't a valid nickname of a user!")
    return
  trusted_users.append(user_id)
  await ctx.channel.send(f"Successfully made {user_id.nick} a trusted user!")
@bot.command(help="""Removes a trusted user (can only be used by trusted users)
math_problems.remove_trusted_user <user_nick>""", brief = "Removes a trusted user (can only be used by trusted users)")
async def remove_trusted_user(ctx,user_nick):
  if ctx.message.author.id not in trusted_users:
    await ctx.channel.send("You aren't a trusted user!")
    return
  s = ctx.message.server
  e = s.get_member_named(user_nick)
  if user_id == None:
    await ctx.channel.send(f"{user_nick} isn't a valid nickname of a user!")
    return
  user_id = e.id
  if user_id not in trusted_users:
    await ctx.channel.send(f"{e.nick} isn't a trusted user!")
    return
  trusted_users.pop(trusted_users.index(user_id))
  await ctx.channel.send(f"Successfully made {user_id.nick} a trusted user!") 

bot.run(DISCORD_TOKEN)