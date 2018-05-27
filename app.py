import discord, asyncio
import secret

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('!kick') and message.server:
        server = message.server
        id = message.mentions[0].id if len(message.mentions) > 0 else "Not Found"
        if id == "Not Found":
            await client.send_message(message.channel, "Specified user not found")
            return
        
        member = message.mentions[0]
        channel = member.voice.voice_channel

        if not channel:
            await client.send_message(message.channel, "Specified user isn't in voice chat")
            return
        try:
            channel = await client.create_channel(server, "kicked", type=discord.ChannelType.voice)
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
            await client.send_message(message.channel, "Kicked " + member.name)
        except discord.Forbidden:
            print("Bot does not have required permissions")
        except discord.NotFound:
            print("Channel not found")
        except discord.HTTPException:
            print("Channel operations failed")
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(secret.TOKEN)