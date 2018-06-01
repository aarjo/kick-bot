import discord, asyncio
import secret
from queue import Queue

client = discord.Client()
q = Queue()

async def executeKick():
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(1)
        if q.empty():
            continue

        try:
            data = q.get()
            member = data[0]
            message_channel = data[1]
            if not member.voice.voice_channel:
                await client.send_message(message_channel, member.name + " isn't in a voice channel")
                continue

            channel = await client.create_channel(member.server, "kicked", type=discord.ChannelType.voice)
            await client.move_member(member, channel)
            voice = await client.join_voice_channel(channel)
            player = voice.create_ffmpeg_player('sound.mp3')
            player.start()

            count = 0
            length = 3

            while count < length:
                await asyncio.sleep(1)
                count += 1
            player.stop()
            await voice.disconnect()
            await client.delete_channel(channel)
            await client.send_message(message_channel, "Kicked " + member.name)
        except discord.Forbidden:
            print("Bot does not have required permissions")
            return
        except discord.NotFound:
            print("Channel not found")
            return
        except discord.HTTPException:
            print("Channel operations failed")
            return

@client.event
async def on_message(message):
    if message.content.startswith('!kick') and message.server:
        if(len(message.mentions) == 0):
            await client.send_message(message.channel, "You didn't specify any users")
            return
        
        for member in message.mentions:
            print("added " + member.name + " to q")
            q.put((member, message.channel))
            
            
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name="The Kicking Game"))
    
client.loop.create_task(executeKick())
client.run(secret.TOKEN)