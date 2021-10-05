import os, sys

import discord
import asyncio
import boto3

client = discord.Client()

ec2 = boto3.resource('ec2', region_name='us-west-1')

# TODO: create a click interface
instance = ec2.Instance(sys.argv[1])

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------')

@client.event
async def on_message(message):
    print(message)
    memberIDs = (member.id for member in message.mentions)
    if client.user.id in memberIDs and message.channel.name == "minecraft-upper":
        print(message.content)
        channel = message.channel
        if 'stop' in message.content:
            if turnOffInstance():
                await channel.send("AWS Instance stopping")
            else:
                await channel.send('Error stopping AWS Instance')
        elif 'start' in message.content:
            if turnOnInstance():
                await channel.send('AWS Instance starting')
            else:
                await channel.send('Error starting AWS Instance')
        elif 'status' in message.content:
            await channel.send('AWS Instance status is: ' + getInstanceState())

def turnOffInstance():
    try:
        instance.stop(False, False)
        return True
    except:
        return False

def turnOnInstance():
    try:
        instance.start()
        return True
    except Exception as e:
        print(e)
        return False

def getInstanceState():
    return instance.state['Name']

def rebootInstance():
    try:
        instance.reboot()
        return True
    except:
        return False


client.run(os.environ['AWSDISCORDTOKEN'])
