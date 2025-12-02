#!/usr/bin/env python3
"""
IAM Security Detector Lambda

This script scans recent CloudTrail management logs in a configured S3 bucket
and detects events of interest such as root console sign-ins, repeated failed
console login attempts, and access key age issues. It publishes alerts to SNS.

Environment variables expected:
- S3_BUCKET
- SNS_TOPIC_ARN
- ACCESS_KEY_MAX_AGE_DAYS (optional, default 90)
- FAILED_LOGIN_THRESHOLD (optional, default 5)
"""

import boto3
import gzip
import json
import io
import os
import datetime

S3_BUCKET = os.environ.get('S3_BUCKET')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
ACCESS_KEY_MAX_AGE_DAYS = int(os.environ.get('ACCESS_KEY_MAX_AGE_DAYS', '90'))
FAILED_LOGIN_THRESHOLD = int(os.environ.get('FAILED_LOGIN_THRESHOLD', '5'))

s3 = boto3.client('s3')
sns = boto3.client('sns')
iam = boto3.client('iam')


def publish_alert(subject, message):
    print(f"Publishing alert: {subject}")
    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)


def list_recent_trail_objects(hours=2):
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=S3_BUCKET)
    keys = []
    for page in pages:
        for obj in page.get('Contents', []) or []:
            # obj['LastModified'] is timezone-aware in boto3; normalize
            lm = obj['LastModified']
            if lm.tzinfo is not None:
                lm = lm.replace(tzinfo=None)
            if lm >= cutoff:
                keys.append(obj['Key'])
    return keys


def read_cloudtrail_file(key):
    resp = s3.get_object(Bucket=S3_BUCKET, Key=key)
    gz = gzip.GzipFile(fileobj=io.BytesIO(resp['Body'].read()))
    data = json.load(gz)
    return data


def check_root_signin(event):
    # ConsoleLogin events have eventName ConsoleLogin
    if event.get('eventName') == 'ConsoleLogin':
        identity = event.get('userIdentity', {})
        if identity.get('type') == 'Root':
            return True
    return False


def check_failed_logins(events):
    counts = {}
    for ev in events:
        if ev.get('eventName') == 'ConsoleLogin':
            outcome = ev.get('errorMessage', '')
            user = ev.get('userIdentity', {}).get('userName', 'UNKNOWN')
            # CloudTrail for failed logins often has responseElements == null and errorMessage
            if (not ev.get('responseElements')) or ('Failed authentication' in outcome) or ('failure' in outcome.lower()):
                counts[user] = counts.get(user, 0) + 1
    return counts


def check_access_key_age(user):
    findings = []
    try:
        keys = iam.list_access_keys(UserName=user).get('AccessKeyMetadata', [])
        for k in keys:
            create_date = k['CreateDate'].replace(tzinfo=None)
            age = (datetime.datetime.utcnow() - create_date).days
            if age >= ACCESS_KEY_MAX_AGE_DAYS:
                findings.append((user, k['AccessKeyId'], age))
    except iam.exceptions.NoSuchEntityException:
        pass
    return findings


def lambda_handler(event, context):
    print('Lambda invoked with event:', json.dumps(event)[:1000])
    keys = list_recent_trail_objects(hours=2)
    all_events = []
    for k in keys:
        try:
            data = read_cloudtrail_file(k)
            for rec in data.get('Records', []):
                all_events.append(rec)
        except Exception as e:
            print(f'Error reading {k}: {e}')

    # 1) Root login detection
    for ev in all_events:
        if check_root_signin(ev):
            subject = 'ALERT: Root console sign-in detected'
            message = json.dumps(ev, default=str, indent=2)
            publish_alert(subject, message)

    # 2) Failed login clustering
    failed = check_failed_logins(all_events)
    for user, count in failed.items():
        if count >= FAILED_LOGIN_THRESHOLD:
            subject = f'ALERT: {count} failed console logins for user {user}'
            message = f'Detected {count} failed console login attempts in the last window for user {user}.'
            publish_alert(subject, message)

    # 3) Access key age checks for users seen in logs (example)
    seen_users = set()
    for ev in all_events:
        uid = ev.get('userIdentity', {}).get('userName')
        if uid:
            seen_users.add(uid)

    for user in seen_users:
        findings = check_access_key_age(user)
        for u, keyid, age in findings:
            subject = f'ALERT: Access key {keyid} for {u} is {age} days old'
            message = f'Access key {keyid} for user {u} is {age} days old (threshold {ACCESS_KEY_MAX_AGE_DAYS}). Consider rotating or disabling.'
            publish_alert(subject, message)

    return {'status': 'done', 'processed_files': len(keys)}
