from flask import Flask, jsonify, request, make_response

import bot


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "home"


@app.route('/create', methods=['GET', 'POST'])
def create():
    request_data = request.get_json()

    if 'task_type' not in request_data:
        return jsonify({'message': 'Task type can not be empty'})

    task_type = int(request_data['task_type'])

    if request.method == 'POST':
        if task_type == 1:  # create channel
            if 'username' not in request_data:
                return jsonify({'message': 'username can not be empty'})

            if 'phone_number' not in request_data:
                return jsonify({"message": 'phone number can not be empty'})

            if 'channel_title' not in request_data:
                return jsonify({"message": 'channel can not be empty'})

            username = request_data['username']
            phone_number = request_data['phone_number']
            channel_title = request_data['channel_title']
            channel_bio = request_data['channel_bio'] if 'channel_bio' in request_data else ''

            if len(username) == 0:
                return jsonify({"message": 'username can not be an empty string'})

            if len(phone_number) == 0:
                return jsonify({"message": 'phone_number can not be an empty string'})

            if len(channel_title) == 0:
                return jsonify({"message": 'channel_title can not be an empty string'})


            channel_id = bot.create_channel(request_data)

            if channel_id:
                response = make_response(
                    jsonify({
                        "message": '201 Channel created',
                        "channel_id": channel_id,
                        "severity": "info"
                        }),
                    201
                )

            else:
                response = make_response(
                    jsonify({
                        "message": '500 Channel not created',
                        "severity": "danger"
                        }),
                    500
                )

        if task_type == 2:  # create group
            if 'group_title' not in request_data:
                return jsonify({"message": 'Group title can not be empty'})

            if 'username' not in request_data:
                return jsonify({"message": 'username can not be empty'})

            if 'phone_number' not in request_data:
                return jsonify({"message": 'Phone number can not be empty'})

            username = request_data['username']
            phone_number = request_data['phone_number']
            group_title = request_data['group_title']
            group_bio = request.json.get('group_bio') if 'group_bio' in request_data else ''

            if len(username) == 0:
                return jsonify({"message": 'username can not be an empty string'})

            if len(phone_number) == 0:
                return jsonify({"message": 'phone_number can not be an empty string'})

            if len(group_title) == 0:
                return jsonify({"message": 'group_title can not be an empty string'})


            group_id = bot.create_group(request_data)

            if group_id:
                response = make_response(
                    jsonify({
                        "message": '201 Group created',
                        "group_id": group_id,
                        "severity": "info"
                        }),
                    201
                )

            else:
                response = make_response(
                    jsonify({
                        "message": '500 Group Not Created',
                        "severity": "danger"
                        }),
                    500
                )

        if task_type == 3:  # create both
            if 'group_title' not in request_data:
                return jsonify({"message": 'group_title can not be empty'})

            if 'channel_title' not in request_data:
                return jsonify({"message": 'channel_title can not be empty'})

            if 'username' not in request_data:
                return jsonify({"message": 'username can not be empty'})

            if 'phone_number' not in request_data:
                return jsonify({"message": 'phone_number can not be empty'})

            username = request_data['username']
            phone_number = request_data['phone_number']
            channel_title = request_data['channel_title']
            channel_bio = request_data['channel_bio'] if 'channel_bio' in request_data else ''
            group_title = request_data['group_title']
            group_bio = request.json.get('group_bio') if 'group_bio' in request_data else ''

            if len(username) == 0:
                return jsonify({"message": 'username can not be an empty string'})

            if len(phone_number) == 0:
                return jsonify({"message": 'phone_number can not be an empty string'})

            if len(group_title) == 0:
                return jsonify({"message": 'group_title can not be an empty string'})

            if len(channel_title) == 0:
                return jsonify({"message": 'channel_title can not be an empty string'})


            channel_id, group_id = bot.create_both(request_data)

            if channel_id or group_id:
                response = make_response(
                    jsonify({
                        "message": '201 Channel and Group created',
                        "channel_id": channel_id,
                        "group_id": group_id,
                        "severity": "info"
                        }),
                    201
                )

            else:
                response = make_response(
                    jsonify({
                        "message": '500 Not Created',
                        "severity": "danger"
                        }),
                    500
                )

        return response


    else:
        return jsonify({'message': 'method not supported :('})


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    request_data = request.get_json()

    if ('channel_id' not in request_data) and ('group_id' not in request_data):
        return jsonify({'message': 'Please enter a channel/group id'})

    if request.method == 'POST':
        if 'username' not in request_data:
            return jsonify({'message': 'username can not be empty'})

        if 'phone_number' not in request_data:
            return jsonify({"message": 'phone number can not be empty'})

        username = request_data['username']
        phone_number = request_data['phone_number']
        group_id = int(request_data['group_id']) if 'group_id' in request_data else 0
        channel_id = int(request_data['channel_id']) if 'channel_id' in request_data else 0

        if len(username) == 0:
            return jsonify({"message": 'username can not be an empty string'})

        if len(phone_number) == 0:
            return jsonify({"message": 'phone_number can not be an empty string'})

        if len(group_id) == 0 and len(channel_id) == 0:
            return jsonify({"message": 'You must at least enter one id/channel or group'})

        added_ids = bot.add_user(request_data)

        if added_ids:
            response = make_response(
                jsonify({
                    "message": '200 user added',
                    "added_ids": added_ids,
                    "severity": "info"
                    }),
                200
            )

        else:
            response = make_response(
                jsonify({
                    "message": '500 User Could Not Be Added',
                    "severity": "danger"
                    }),
                500
            )

        return response


    else:
        return jsonify({'message': 'method not supported :('})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
