import os
import sys
import json
import discord
import asyncio
import boto3
import click

client = discord.Client()

instance_map = {}

@click.command()
@click.argument('instance_map_file', type=click.Path(exists=True))
def main(instance_map_file):
    ec2 = boto3.resource('ec2', region_name='us-west-1')

    global instance_map
    try:
        with open(instance_map_file, "r") as f:
            instance_map_json = json.load(f)
    except FileNotFoundError as e:
        print(e)
        exit()

    if len(instance_map_json) == 0:
        raise Exception("Empty Instance Map")

    for instance_name, instance_id in instance_map_json.items():
        instance_map[instance_name] = ec2.Instance(instance_id)

    client.run(os.environ['AWSDISCORDTOKEN'])


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
        target_instance_name = message.content.split()[1]

        if target_instance_name in instance_map:
            target_instance = instance_map[target_instance_name]

            if 'stop' in message.content:
                if turnOffInstance(target_instance):
                    await channel.send("AWS Instance stopping")
                else:
                    await channel.send('Error stopping AWS Instance')
            elif 'start' in message.content:
                if turnOnInstance(target_instance):
                    await channel.send('AWS Instance starting')
                else:
                    await channel.send('Error starting AWS Instance')
            elif 'status' in message.content:
                await channel.send('AWS Instance status is: ' + getInstanceState(target_instance))

        else:
            await channel.send(f"Could not find {target_instance}")


def turnOffInstance(instance):
    try:
        instance.stop(False, False)
        return True
    except Exception as e:
        print(e)
        return False


def turnOnInstance(instance):
    try:
        instance.start()
        return True
    except Exception as e:
        print(e)
        return False


def getInstanceState(instance):
    return instance.state['Name']


def rebootInstance(instance):
    try:
        instance.reboot()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    main()
