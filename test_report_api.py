import asyncio
import httpx
import json

async def test_task_summary_report():
    """
    Test the task summary report API endpoint to see if it's working properly
    """
    base_url = "http://localhost:8000"
    
    # First, let's try to get an auth token (you'll need to replace with actual login)
    # For now, I'll assume you have a valid token
    
    # Sample request data for generating a task summary report
    report_request = {
        "report_type": "task_summary",
        "name": "Test Task Summary Report",
        "description": "Test report for task summary functionality",
        "start_date": None,
        "end_date": None,
        "project_key": None,
        "user_id": None,
        "is_public": False
    }
    
    # Headers (you'll need to replace with your actual JWT token)
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"  # Uncomment and add your token
    }
    
    print("Testing task summary report generation...")
    print(f"Sending request: {json.dumps(report_request, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/reports/generate",
                json=report_request,
                headers=headers
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                print("\nTask summary report generated successfully!")
                data = response.json()
                print(f"Report ID: {data.get('metadata', {}).get('id')}")
                print(f"Number of data points: {len(data.get('data', []))}")
                print(f"Summary: {data.get('summary')}")
            elif response.status_code == 422:
                print("\nValidation error - check the request format")
            elif response.status_code == 401:
                print("\nUnauthorized - need valid JWT token")
            else:
                print(f"\nUnexpected response status: {response.status_code}")
                
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    asyncio.run(test_task_summary_report())