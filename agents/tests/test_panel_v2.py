"""
Test Panel Discussion V2 System
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from current directory
load_dotenv('.env')

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from panel_discussion_strands_v2 import create_panel_discussion_strands_v2
from storage.rds_storage import create_rds_storage
from dataclasses import asdict


def test_panel_discussion():
    """Test the panel discussion system"""

    print("🚀 Testing Panel Discussion V2 System\n")

    # Initialize panel
    print("1️⃣ Initializing panel system...")
    panel = create_panel_discussion_strands_v2(
        model_id="anthropic.claude-3-haiku-20240307-v1:0"
    )
    print("✅ Panel initialized\n")

    # Initialize storage (skip if DB_HOST not accessible)
    storage = None
    if os.getenv('DB_HOST') and os.getenv('ENABLE_RDS', 'false').lower() == 'true':
        print("2️⃣ Initializing RDS storage...")
        try:
            storage = create_rds_storage(
                db_host=os.getenv('DB_HOST'),
                db_user=os.getenv('DB_USER'),
                db_password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME', 'glue'),
                db_port=int(os.getenv('DB_PORT', '5432')),
                s3_bucket=os.getenv('KB_S3_BUCKET', 'hackthon-knowledge-base'),
                region=os.getenv('AWS_REGION', 'us-west-2')
            )
            print("✅ Storage initialized\n")
        except Exception as e:
            print(f"⚠️  RDS not accessible (running in local mode): {e}\n")
            storage = None
    else:
        print("2️⃣ Skipping RDS storage (local test mode)\n")

    # Run discussion for a test country
    print("3️⃣ Running panel discussion for test country...")
    test_country = 'TEST'
    test_topic = 'Is this test country experiencing positive economic and social conditions?'

    # Simple test data
    test_data = {
        'news': [
            {'title': 'Economic growth reaches 3.5% this quarter'},
            {'title': 'New social programs improve quality of life'},
            {'title': 'Environmental initiatives show promising results'}
        ],
        'weather': {
            'description': 'Sunny',
            'temp': 22
        }
    }

    result = panel.start_discussion(
        country_code=test_country,
        topic=test_topic,
        country_data=test_data,
        max_rounds=5  # Maximum rounds (moderator will decide when to stop)
    )
    print("✅ Discussion completed\n")

    # Display results
    print("=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Country: {result.country_code}")
    print(f"Topic: {result.topic}")
    print(f"Final Mood: {result.final_mood.upper()}")
    print(f"Final Score: {result.final_score:.1f}/100")
    print(f"Total Turns: {result.total_turns}")
    print(f"Analyses: {len(result.analyses)}")
    print(f"Votes: {len(result.votes)}")
    print(f"Transcripts: {len(result.transcripts)}")
    print("=" * 60)
    print()

    # Save to RDS (if available)
    if storage:
        print("4️⃣ Saving to RDS...")
        try:
            discussion_id = storage.save_panel_result(result, test_country, skip_s3=True)
            print(f"✅ Saved to RDS with ID: {discussion_id}\n")
        except Exception as e:
            print(f"❌ Error saving to RDS: {e}\n")
    else:
        print("4️⃣ Skipping RDS save (local test mode)\n")

    print("🎉 Test completed!")

    return result


if __name__ == "__main__":
    test_panel_discussion()
