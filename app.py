import discord, asyncio
import secret
from queue import Queue
from discord.ext.commands import Bot

client = Bot(command_prefix='!', description='Kick users from voice chat in a stylish fashion')
q = Queue()

async def executeKick():
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(1)
        if q.empty():
            continue

        try:
            data = q.get()
            members = data[0]
            message_channel = data[1]
            created = False
            voice_members = []

            for member in members:
                if not member.voice.voice_channel:
                    await client.send_message(message_channel, member.name + " isn't in a voice channel")
                    continue
                    
                if not created:
                        channel = await client.create_channel(member.server, "kicked", type=discord.ChannelType.voice)
                        voice = await client.join_voice_channel(channel)
                        player = voice.create_ffmpeg_player('sound.mp3')
                        created = True

                voice_members.append(member)
                await client.move_member(member, channel)
            
            if created:
                player.start()

                count = 0
                length = 3

                while count < length:
                    await asyncio.sleep(1)
                    count += 1
                player.stop()
                await voice.disconnect()
                await client.delete_channel(channel)
                await client.send_message(message_channel, "Kicked " + ', '.join(member.name for member in voice_members))
        except discord.Forbidden:
            print("Bot does not have required permissions")
            return
        except discord.NotFound:
            print("Channel not found")
            return
        except discord.HTTPException:
            print("Channel operations failed")
            return

@client.command(name='kick', pass_context=True)
async def kick(ctx):
    if ctx.message.server:
        if(len(ctx.message.mentions) == 0):
            await client.say("You didn't specify any users")
            return
        
        q.put((ctx.message.mentions, ctx.message.channel))

@client.command(name='kickchannel', aliases=['kickc'], pass_context=True)
async def kick_channel(ctx, arg):
    channel = discord.utils.get(ctx.message.server.channels, name=arg, type=discord.ChannelType.voice)
    if not channel:
        await client.say("Could not find a channel with the name " + arg)
        return
    if not channel.voice_members:
        await client.say(arg + " is empty")
        return

    q.put((channel.voice_members, ctx.message.channel))

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await client.send_message(ctx.message.channel, "You didn't specify a channel")
        return
    else:
        return

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="The Kicking Game"))
   
client.loop.create_task(executeKick())
client.run(secret.TOKEN)