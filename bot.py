from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest, InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import InputChannel, InputPeerChannel
from telethon import TelegramClient, events, sync
import datetime as dt
import logging
import time

from database import Gap

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


def create_channel(query):
    try:
        user = client.get_input_entity(query.username)

        channel = client(CreateChannelRequest(query.title, query.bio, megagroup=False))
        channel_id = channel.__dict__["chats"][0].__dict__["id"]
        channel_link = client(
            ExportChatInviteRequest(
                peer=client.get_entity(channel_id),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=1
            )
        ).link

        client(InviteToChannelRequest(channel=channel_id, users=[user]))
        client.edit_admin(channel_id, user, is_admin=True, add_admins=False, invite_users=False)

        Gap.update(id=channel_id, link=channel_link, status='done').where(Gap.code == query.code).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception(f"Unexpected Error")

    finally:
        Gap.update(status='failed').where(Gap.code == query.code, Gap.status != 'done').execute()


def create_group(query):
    try:
        user = client.get_input_entity(query.username)

        group = client(CreateChannelRequest(query.title, query.bio, megagroup=True))
        group_id = group.__dict__["chats"][0].__dict__['id']
        group_link = client(
            ExportChatInviteRequest(
                peer=client.get_entity(group_id),
                legacy_revoke_permanent=True,
                expire_date=None,
                usage_limit=1
            )
        ).link

        client(InviteToChannelRequest(channel=group_id, users=[user]))
        client.edit_admin(group_id, user, is_admin=True, add_admins=False)

        Gap.update(id=group_id, link=group_link, status='done').where(Gap.code == query.code).execute()

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")

    finally:
        Gap.update(status='failed').where(Gap.code == query.code, Gap.status != 'done').execute()


def add_user(data):
    action_username = data['username']
    channel_id = int(data['channel_id'])
    group_id = int(data['group_id'])

    try:
        username = action_username  # if action_username.startswith('@') else '@'+action_username
        user_to_add = client.get_entity(username)
        added_chat_ids = {}

        if channel_id:
            client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
            added_chat_ids['channel'] = channel_id

        if group_id:
            client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))
            added_chat_ids['group'] = group_id

        return added_chat_ids

    except PeerFloodError:
        logging.exception("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        time.sleep(900)

    except UserPrivacyRestrictedError:
        logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

    except Exception:
        logging.exception("Unexpected Error")


if __name__ == '__main__':
    while True:
        if (new_queries := Gap.select().where(Gap.status == 'pending')).exists():
            for query in new_queries:
                if query.task_type == 1:
                    create_channel(query)

                elif query.task_type == 2:
                    create_group(query)


        time.sleep(3)
