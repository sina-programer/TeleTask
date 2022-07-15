from utils import *

from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
import logging

logging.basicConfig(
    format='%(asctime)s - %(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

# with TelegramClient('teletask', api_id, api_hash) as clinet :
#    client.send_message('tiyea', "run")

client = TelegramClient('teletask', api_id, api_hash)
client.start()
a = client.is_user_authorized()
logging.debug(f'user is authorized: {a}')


while True:
    time.sleep(5)

    newest_action = list(actions_collection.find({'status': 'waiting'}))
    logging.debug(f'length of newest_action {len(newest_action)}')

    for action in newest_action:
        logging.info(action)
        action_type = action['type']

        if action_type == 1:
            action_username = action['username']
            channel_title = action['channel_title']
            channel_bio = action['channel_bio']

            try:
                username = action_username  # if action_username.startswith('@') else '@'+action_username
                user_to_add = client.get_input_entity(username)
                createdChannel = client(CreateChannelRequest(channel_title, channel_bio, megagroup=False))
                channel_id = createdChannel.__dict__["chats"][0].__dict__["id"]
                client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
                client.edit_admin(channel_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)
                actions_collection.update_one(
                    {'_id': action['_id']},
                    {
                        '$set': {
                            'status': 'done',
                            'channel_id': channel_id,
                            'doneTime': datetime.now()
                        }
                    }
                )

                logging.info("Waiting 60 Seconds...")
                time.sleep(60)

            except PeerFloodError as fex:
                logging.exception(
                    "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
                )
                time.sleep(900)

            except UserPrivacyRestrictedError:
                logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

            except Exception as ex:
                logging.exception("Unexpected Error")


        elif action_type == 2:
            action_username = action['username']
            group_title = action['group_title']
            group_bio = action['group_bio']
            username = action_username  # if action_username.startswith('@') else '@' + action_username

            try:
                user_to_add = client.get_input_entity(username)
                createdGroup = client(CreateChannelRequest(group_title, group_bio, megagroup=True))
                group_id = createdGroup.__dict__["chats"][0].__dict__["id"]

                client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))
                client.edit_admin(group_id, user_to_add, is_admin=True, add_admins=False)
                actions_collection.update_one(
                    {'_id': action['_id']},
                    {
                        '$set': {
                            'status': 'done',
                            'group_id': group_id,
                            'doneTime': datetime.now()
                            }
                    }
                )

                logging.info("Waiting 60 Seconds...")
                time.sleep(60)

            except PeerFloodError as fex:
                logging.exception(
                    "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
                )
                time.sleep(900)

            except UserPrivacyRestrictedError:
                logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

            except Exception as ex:
                logging.exception("Unexpected Error")


        elif action_type == 3:
            action_username = action['username']
            channel_title = action['channel_title']
            channel_bio = action['channel_bio']
            group_title = action['group_title']
            group_bio = action['group_bio']

            try:
                username = action_username  # if action_username.startswith('@') else '@'+action_username
                createdChannel = client(CreateChannelRequest(channel_title, channel_bio, megagroup=False))
                createdGroup = client(CreateChannelRequest(group_title, group_bio, megagroup=True))
                user_to_add = client.get_input_entity(username)

                channel_id = createdChannel.__dict__["chats"][0].__dict__["id"]
                group_id = createdGroup.__dict__["chats"][0].__dict__["id"]

                client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))
                client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))

                actions_collection.update_one({'_id': action['_id']}, {'$set': {'status': 'done', 'channel_id': channel_id}})
                client.edit_admin(channel_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)
                client.edit_admin(group_id, user_to_add, is_admin=True, add_admins=False, invite_users=False)
                actions_collection.update_one(
                    {'_id': action['_id']},
                    {
                        '$set': {
                            'status': 'done',
                            'group_id': group_id,
                            'doneTime': datetime.now()
                            }
                    }
                )

                logging.info("Waiting 60 Seconds...")
                time.sleep(60)

            except PeerFloodError as fex:
                logging.exception(
                    "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
                )
                time.sleep(900)

            except UserPrivacyRestrictedError:
                logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

            except Exception as ex:
                logging.exception("Unexpected Error")

            channel_id = createdChannel.__dict__["chats"][0].__dict__["id"]
            group_id = createdGroup.__dict__["chats"][0].__dict__["id"]
            client(InviteToChannelRequest(channel=channel_id, users=[username]))
            client(InviteToChannelRequest(channel=group_id, users=[username]))
            actions_collection.update_one(
                {'_id': action['_id']},
                {
                    '$set': {
                        'status': 'done',
                        'channel_id': channel_id,
                        'group_id': group_id,
                        'doneTime': datetime.now()
                        }
                }
            )


        elif action_type == 4:
            action_username = action['username']
            channel_id = int(action['channel_id'])
            group_id = int(action['group_id'])

            try:
                username = action_username  # if action_username.startswith('@') else '@'+action_username
                user_to_add = client.get_entity(username)

                if channel_id:
                    client(InviteToChannelRequest(channel=channel_id, users=[user_to_add]))

                if group_id:
                    client(InviteToChannelRequest(channel=group_id, users=[user_to_add]))
                    actions_collection.update_one(
                        {'_id': action['_id']},
                        {
                            '$set': {
                                'status': 'done',
                                'doneTime': datetime.now()
                                }
                        }
                    )

                    logging.info("Waiting 60 Seconds...")
                    time.sleep(60)

            except PeerFloodError as fex:
                logging.exception(
                    "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
                )
                time.sleep(900)

            except UserPrivacyRestrictedError as err:
                logging.exception("The user's privacy settings do not allow you to do this. Skipping.")

            except Exception as ex:
                logging.exception("Unexpected Error")
