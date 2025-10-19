#!/usr/bin/env python3
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv('AWS_REGION', 'us-west-2')
dynamodb = boto3.resource('dynamodb', region_name=region)

# Test Users
users_table = dynamodb.Table('recruitment_users')
test_users = [
    {
        'user_id': 'user123',
        'name': 'Taro Yamada',
        'email': 'taro@example.com',
        'skills': ['Python', 'AWS', 'Machine Learning'],
        'experience': '5 years',
        'preferences': {'location': 'Tokyo', 'remote': True}
    },
    {
        'user_id': 'user456',
        'name': 'Hanako Sato',
        'email': 'hanako@example.com',
        'skills': ['JavaScript', 'React', 'Node.js'],
        'experience': '3 years',
        'preferences': {'location': 'Osaka', 'remote': False}
    }
]

print("Loading test users...")
for user in test_users:
    users_table.put_item(Item=user)
    print(f"  ✓ {user['name']}")

# Test Jobs
jobs_table = dynamodb.Table('recruitment_jobs')
test_jobs = [
    {
        'job_id': 'job001',
        'title': 'Senior Software Engineer',
        'company': 'Tech Corp',
        'location': 'Tokyo',
        'requirements': ['Python', 'AWS', '5+ years'],
        'description': 'Build scalable cloud applications'
    },
    {
        'job_id': 'job002',
        'title': 'Frontend Developer',
        'company': 'Web Solutions',
        'location': 'Osaka',
        'requirements': ['React', 'TypeScript', '3+ years'],
        'description': 'Create modern web interfaces'
    }
]

print("Loading test jobs...")
for job in test_jobs:
    jobs_table.put_item(Item=job)
    print(f"  ✓ {job['title']} at {job['company']}")

# Test GitHub Profiles
github_table = dynamodb.Table('recruitment_github_profiles')
test_profiles = [
    {
        'user_id': 'user123',
        'username': 'taro-dev',
        'repos': ['ml-pipeline', 'aws-lambda-tools'],
        'languages': ['Python', 'Go'],
        'contributions': 1250
    }
]

print("Loading test GitHub profiles...")
for profile in test_profiles:
    github_table.put_item(Item=profile)
    print(f"  ✓ {profile['username']}")

print("\n✅ Test data loaded successfully")
