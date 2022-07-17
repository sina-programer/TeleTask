from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest, InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import InputChannel, InputPeerChannel
from telethon import TelegramClient, events, sync
import datetime as dt
import logging
import time

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    format='%(asctime)s - %(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

client = TelegramClient(
    session=config['Bot']['session_name'],
    api_id=int(config['Bot']['api_id']),
    api_hash=config['Bot']['api_hash']
)
client.start()

logging.debug(f'is user authorized: {client.is_user_authorized()}')


def create_channel(data):
    action_username = data['username']
    channel_title = data['channel_title']
    channel_bio = data['channel_bio']

    try:
        username = action_username  # if action_username.startswith('@') else '@'+action_username
        user_to_add = client.get_input_entity(username)
        createdChannel = client(CreateChannelRequest(channel_title, channel_bio, megagroup=False))
        channel_id = createdChannel.__dict__["chats"][0].__dict__["id"]
        client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
        client.edit_admin(channel_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)

        return channel_id

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception(f"Unexpected Error")


def create_group(data):
    action_username = data['username']
    group_title = data['group_title']
    group_bio = data['group_bio']
    username = action_username  # if action_username.startswith('@') else '@' + action_username

    try:
        user_to_add = client.get_input_entity(username)
        createdGroup = client(CreateChannelRequest(group_title, group_bio, megagroup=True))
        group_id = createdGroup.__dict__["chats"][0].__dict__["id"]

        client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))
        client.edit_admin(group_id, user_to_add, is_admin=True, add_admins=False)

        return group_id

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


def create_both(data):
    action_username = data['username']
    channel_title = data['channel_title']
    channel_bio = data['channel_bio']
    group_title = data['group_title']
    group_bio = data['group_bio']

    try:
        username = action_username  # if action_username.startswith('@') else '@'+action_username
        createdChannel = client(CreateChannelRequest(channel_title, channel_bio, megagroup=False))
        createdGroup = client(CreateChannelRequest(group_title, group_bio, megagroup=True))
        user_to_add = client.get_input_entity(username)

        channel_id = createdChannel.__dict__["chats"][0].__dict__["id"]
        group_id = createdGroup.__dict__["chats"][0].__dict__["id"]

        client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
        client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))

        client.edit_admin(channel_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)
        client.edit_admin(group_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)

        return channel_id, group_id

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


def add_user(data):
    action_username = data['username']
    channel_id = int(data['channel_id'])
    group_id = int(data['group_id'])

    try:
        username = action_username  # if action_username.startswith('@') else '@'+action_username
        user_to_add = client.get_entity(username)
        added_ids = []

        if channel_id:
            client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
            added_ids.append(channel_id)

        if group_id:
            client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))
            added_ids.append(group_id)

        return added_ids

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")
