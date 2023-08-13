#!/usr/bin/python
# -*- coding: utf-8 -*-
import functions_framework


@functions_framework.http
def fetch_data(request):
    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if request_json and 'type' in request_json \
            and request_json['type'] == 'db':
            return "{'host':'35.223.139.236', 'user':'sheriff', 'pass':YiQ[{'</iG8-Eo1Y}"
        else:
            return 'Invalid request or missing parameters.'
    else:
        return 'Invalid method. This endpoint only accepts POST requests with valid type of creds you need in JSON format'
