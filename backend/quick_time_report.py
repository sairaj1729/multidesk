import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"
REPORTS_ENDPOINT = "/api/reports"

def login_and_generate_report():
    """Login and generate time tracking report"""
    # First, let's try to login
    login_data = {
        "email": "sairaj@gmail.com",
        "password": "Sairaj@123"
    }
    
    try:
        print("🔐 Attempting login...")
        login_response = requests.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print("✅ Login successful!")
            
            # Generate time tracking report
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            report_data = {
                "name": f"Time Tracking Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "description": "Time estimation vs actual work hours analysis",
                "report_type": "time_tracking",
                "start_date": "2026-01-01T00:00:00",
                "end_date": "2026-12-31T23:59:59",
                "project_key": "SCRUM",
                "user_id": "",
                "status": None,
                "is_public": False
            }
            
            print("📊 Generating time tracking report...")
            report_response = requests.post(
                f"{BASE_URL}{REPORTS_ENDPOINT}",
                json=report_data,
                headers=headers
            )
            
            if report_response.status_code == 200:
                result = report_response.json()
                print("✅ Time tracking report generated successfully!")
                print(f"\n📋 Report Details:")
                print(f"   ID: {result['metadata']['id']}")
                print(f"   Name: {result['metadata']['name']}")
                print(f"   Type: {result['metadata']['type']}")
                print(f"   Created: {result['metadata']['created_at']}")
                
                print(f"\n📈 Summary:")
                summary = result['summary']
                print(f"   Total Estimated Hours: {summary.get('total_estimated_hours', 0)}")
                print(f"   Total Story Points: {summary.get('total_story_points', 0)}")
                print(f"   Total Tasks: {summary.get('total_tasks', 0)}")
                print(f"   Completed Tasks: {summary.get('completed_tasks', 0)}")
                print(f"   Completion Rate: {summary.get('completion_rate', 0)}%")
                
                print(f"\n📊 Data Points:")
                for point in result['data']:
                    print(f"   {point['label']}: {point['value']}")
                
                print(f"\n🎯 You can now view this report in the frontend!")
                print(f"   Report ID: {result['metadata']['id']}")
                return result['metadata']['id']
            else:
                print(f"❌ Failed to generate report: {report_response.status_code}")
                print(report_response.text)
                return None
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            # Let's try to see what users exist by checking the error
            if "Incorrect email or password" in login_response.text:
                print("📝 Note: The user credentials might be different.")
                print("💡 Try logging in through the frontend first to get valid credentials.")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 Time Tracking Report Generator")
    print("=" * 50)
    print("This script will generate a time tracking report for you!")
    print()
    
    report_id = login_and_generate_report()
    
    if report_id:
        print(f"\n🎉 Success! Time tracking report created with ID: {report_id}")
        print("📋 Next steps:")
        print("   1. Open the frontend application (http://localhost:8081)")
        print("   2. Navigate to the Reports section")
        print("   3. Find your newly created report")
        print("   4. View the time tracking analysis!")
    else:
        print("\n❌ Report generation failed.")
        print("💡 Troubleshooting tips:")
        print("   - Make sure the backend server is running on port 8000")
        print("   - Verify your user credentials are correct")
        print("   - Check if you can login through the frontend first")

if __name__ == "__main__":
    main()