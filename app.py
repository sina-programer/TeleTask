from flask import Flask, jsonify, request, make_response
import datetime as dt
import random
import string
import time

from database import Gap


def check_attributes(data: dict, attrs):
    """
    This function check that all necessary attributes there are in data

    NOTE: if you want to check that there are at least one of some attrs, you can send they in a list.  for example:
    check_attributes(data, ['first_necessary', ['second_optional1', 'second_optional2'], 'third_necessary'])
    but, must there is at least one of ['second_optional1', 'second_optional2']
    """

    for attr in attrs:
        if isinstance(attr, list):  # if <attr> is a list, existing one of them is enough
            if all(not data.get(a, None) for a in attr):
                return jsonify({'message': f"you have to enter at least one of {attr}"})

        elif not data.get(attr, None):
            return jsonify({'message': f"{attr} is invalid"})


def generate_code(length=8):
    def _random_generate():
        return ''.join(random.sample(string.ascii_letters, length))

    code = _random_generate()
    while Gap.select().where(Gap.code == code).exists():
        code = _random_generate()

    return code


def _create_channel():
    if result := check_attributes(request.args, ['username', 'phone_number', 'channel_title']):
        return result

    channel_code = generate_code()

    Gap.create(
        code=channel_code,
        username=request.args['username'],
        phone_number=f"+{request.args['phone_number'][1:]}",  # replace first space with plus
        task_type=request.args['task_type'],
        title=request.args['channel_title'],
        bio=request.args.get('channel_bio', ''),  # might there is not at all
        id='',
        status='pending',
        datetime=dt.datetime.now()
    )

    while Gap.select().where(Gap.code == channel_code, Gap.status == 'pending').exists():  # wait until but create
        time.sleep(3)

    channel = Gap.get(code=channel_code)

    if channel.status != 'failed':
        return make_response(
            jsonify({
                'task_type': channel.task_type,
                'message': '201 Channel created',
                'severity': "info",
                'id': channel.id,
                'title': channel.title,
                'bio': channel.bio
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Channel not created',
                "severity": "danger"
            }),
            500
        )


def _create_group():
    if result := check_attributes(request.args, ['username', 'phone_number', 'group_title']):
        return result

    group_code = generate_code()

    Gap.create(
        code=group_code,
        username=request.args['username'],
        phone_number=f"+{request.args['phone_number'][1:]}",  # replace first space with plus
        task_type=request.args['task_type'],
        title=request.args['group_title'],
        bio=request.args.get('group_bio', ''),  # might there is not at all
        id='',
        status='pending',
        datetime=dt.datetime.now()
    )

    while Gap.select().where(Gap.code == group_code, Gap.status == 'pending').exists():  # wait until but create
        time.sleep(3)

    group = Gap.get(code=group_code)

    if group.status != 'failed':
        return make_response(
            jsonify({
                'task_type': group.task_type,
                'message': '201 Group created',
                'severity': "info",
                'id': group.id,
                'title': group.title,
                'bio': group.bio
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Group Not Created',
                "severity": "danger"
            }),
            500
        )


def _create_both():
    if result := check_attributes(request.args, ['username', 'phone_number', 'channel_title', 'group_title']):
        return result

    group_code = generate_code()
    channel_code = generate_code()

    Gap.create(
        code=channel_code,
        username=request.args['username'],
        phone_number=f"+{request.args['phone_number'][1:]}",  # replace first space with plus
        task_type=1,
        title=request.args['channel_title'],
        bio=request.args.get('channel_bio', ''),  # might there is not at all
        id='',
        status='pending',
        datetime=dt.datetime.now()
    )

    Gap.create(
        code=group_code,
        username=request.args['username'],
        phone_number=f"+{request.args['phone_number'][1:]}",  # replace first space with plus
        task_type=2,
        title=request.args['group_title'],
        bio=request.args.get('group_bio', ''),  # might there is not at all
        id='',
        status='pending',
        datetime=dt.datetime.now()
    )

    while Gap.select().where(Gap.code == channel_code, Gap.status == 'pending').exists():  # wait until but create
        time.sleep(3)
    while Gap.select().where(Gap.code == group_code, Gap.status == 'pending').exists():  # wait until but create
        time.sleep(3)

    group = Gap.get(code=group_code)
    channel = Gap.get(code=channel_code)

    if group.status != 'failed' or channel.status != 'failed':
        return make_response(
            jsonify({
                'task_type': group.task_type,
                'message': '201 Channel and Group created',
                'title': group.title,
                'channel_id': channel.id,
                'channel_bio': channel.bio,
                'group_id': group.id,
                'group_bio': group.bio,
                'severity': "info"
            }),
            201
        )

    else:
        return make_response(
            jsonify({
                "message": '500 Not Created',
                "severity": "danger"
            }),
            500
        )


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "home"


@app.route('/create', methods=['GET', 'POST'])
def create():
    task_type = request.args.get('task_type', None)
    if not task_type:
        return jsonify({'message': 'Please enter task type!'})


    if task_type == '1':
        return _create_channel()

    elif task_type == '2':
        return _create_group()

    elif task_type == '3':
        return _create_both()

    else:
        return jsonify({"message": 'Please enter a valid task type!'})


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if result := check_attributes(request.args, ['username', 'phone_number', ['channel_id', 'group_id']]):
        return result


    added_chat_ids = bot.add_user(request.args)

    if added_chat_ids:
        return make_response(
            jsonify({
                "message": '200 user added',
                "added_chat_ids": str(added_chat_ids),
                "severity": "info"
                }),
            200
        )

    else:
        return make_response(
            jsonify({
                "message": '500 User Could Not Be Added',
                "severity": "danger"
                }),
            500
        )



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
