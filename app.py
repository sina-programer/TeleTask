from flask import Flask, jsonify, request, make_response

import bot


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


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "home"


@app.route('/create', methods=['GET', 'POST'])
def create():
    task_type = request.args.get('task_type', None)

    if task_type:
        try:
            task_type = int(task_type)

        except Exception:
            return jsonify({'message': 'Task type is not an integer!'})

    else:
        return jsonify({'message': 'Please enter task type!'})


    if request.method == 'POST':
        if task_type == 1:  # create channel

            if result := check_attributes(request.args, ['username', 'phone_number', 'channel_title']):
                return result

            channel_id = bot.create_channel(request.args)

            if channel_id:
                response = make_response(
                    jsonify({
                        "message": '201 Channel created',
                        "channel_id": str(channel_id),
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

            if result := check_attributes(request.args, ['username', 'phone_number', 'group_title']):
                return result

            group_id = bot.create_group(request.args)

            if group_id:
                response = make_response(
                    jsonify({
                        "message": '201 Group created',
                        "group_id": str(group_id),
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

            if result := check_attributes(request.args, ['username', 'phone_number', 'channel_title', 'group_title']):
                return result

            channel_id, group_id = bot.create_both(request.args)

            if channel_id or group_id:
                response = make_response(
                    jsonify({
                        "message": '201 Channel and Group created',
                        "channel_id": str(channel_id),
                        "group_id": str(group_id),
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
    if result := check_attributes(request.args, ['username', 'phone_number', ['channel_id', 'group_id']]):
        return result


    if request.method == 'POST':
        added_ids = bot.add_user(request.args)

        if added_ids:
            response = make_response(
                jsonify({
                    "message": '200 user added',
                    "added_ids": str(added_ids),
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
