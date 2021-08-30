import re

from javascript import require, On, Once, globalThis
mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
v = require('vec3')
pvp = require('mineflayer-pvp').plugin

# Bot Config
BOT_OWNERS = ['Hoap', 'NatsueKunGz_XD']
BOT_USERNAME = 'Aoba'
BOT_PASSWORD = 'Core2'

AUTHME_ACTIVE = False
LOGIN_GATE = False

bot = mineflayer.createBot({
  'host': 'localhost',
  'port': 25565,
  'username': BOT_USERNAME,
  'version': '1.12.2'
})
mcData = require('minecraft-data')(bot.version)
movements = pathfinder.Movements(bot, mcData)

# Plugins
bot.loadPlugin(pathfinder.pathfinder)
bot.loadPlugin(require('mineflayer-armor-manager'))

# Chat Pattern
bot.addChatPatternSet(
	'server',
	[globalThis.RegExp("(.*) (.*) > (.*)")],
	{"parse":True}
)

bot.addChatPatternSet(
	'serverwhisper',
	[globalThis.RegExp("\[\[(.*)\] (.+) (-») (me)\] (.+)")],
	{"parse":True}
)

# Login Gate
@Once(bot, 'spawn')
def login(*args):
	print("I'm in.")
	if AUTHME_ACTIVE:
		bot.chat(f'/login {BOT_PASSWORD}')
	if LOGIN_GATE:
		bot.pathfinder.setMovements(movements)
		bot.pathfinder.setGoal(pathfinder.goals.GoalBlock(28, 68, 0))
		@Once(bot, 'goal_reached')
		def reached(*args):
			bot.setControlState('jump', True)
			bot.setControlState('jump', False)

# Server Messages
PREFIXES = ["!bot", "!all"]
@On(bot, 'chat:server')
@On(bot, 'chat:serverwhisper')
def cmd(*args):
	# Command
	cmdUsrname = args[2][0][1]
	cmdMessage = args[2][0][2]
	cmdMsgPart = cmdMessage.split(" ")
	if cmdUsrname in BOT_OWNERS and cmdMsgPart[0] in PREFIXES:
		if len(cmdMsgPart) == 1:
			bot.chat(f"Command detected, {BOT_OWNER}? Are you looking for something?")
		elif len(cmdMsgPart) >= 1:
			if cmdMsgPart[1] == "sudo":
				bot.chat(' '.join([str(x) for x in cmdMsgPart[2:]]))
			elif cmdMsgPart[1] == "disconnect":
				bot.quit()
			elif cmdMsgPart[1] == "spam":
				if len(cmdMsgPart) >= 4:
					for counter in range(1,int(cmdMsgPart[2])+1):
						bot.chat(' '.join([str(x) for x in cmdMsgPart[3:]]))
				else:
					bot.chat("Wrong usage!: <prefix> spam <times> <msg>")
			elif cmdMsgPart[1] == "dump":
				items = bot.inventory.items()
				for item in items:
					bot.tossStack(item)
			elif cmdMsgPart[1] == "adump":
				container = bot.inventory.containerItems()
				for item in container:
					bot.tossStack(item)
			elif cmdMsgPart[1] == "follow":
				if cmdMsgPart[2] == "me":
					target = bot.players[cmdUsrname].entity;
					if target:
						bot.pathfinder.setMovements(movements)
						bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 1), 1)
						bot.lookAt(target.position.plus(v(0, 1.62, 0)))
						bot.chat("OK!")
					elif not target:
						bot.chat("Where are you?")
				else:
					target = bot.players[cmdMsgPart[2]].entity;
					if target:
						bot.pathfinder.setMovements(movements)
						bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(target, 1), 1)
						bot.lookAt(target.position.plus(v(0, 1.62, 0)))
						bot.chat("OK!")
					elif not target:
						bot.chat("Where are you?")
			elif cmdMsgPart[1] == "follow_stop" or cmdMsgPart[1] == "route_stop":
					bot.pathfinder.setGoal(None)
					bot.chat("Alright, I'm done!")


	print(f"[USRINPUT] {cmdUsrname}: {cmdMessage}")

@On(bot, 'messagestr')
def stuff(this, message, messagePosition, jsonMsg):
	sv = re.match(r"(.*) (.*) > (.*)", message)
	if sv is None:
		print(f"[MESSAGES] {message}")
