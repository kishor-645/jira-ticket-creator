from flask import Flask, request, jsonify
import os
import requests
import json
import base64
from azure.data.tables import TableServiceClient
from datetime import datetime, timedelta

app = Flask(__name__)

def get_table_client():
    """Get or create Azure Table client for tracking processed exceptions."""
    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    table_service = TableServiceClient.from_connection_string(connection_string)
    table_client = table_service.get_table_client("processedExceptions")
    
    try:
        table_service.create_table("processedExceptions")
    except Exception:
        # Table already exists
        pass
    
    return table_client

def is_exception_processed(timestamp):
    """Check if an exception has already been processed based on its timestamp."""
    table_client = get_table_client()
    try:
        table_client.get_entity(partition_key="exceptions", row_key=timestamp)
        return True
    except Exception:
        return False

def mark_exception_processed(timestamp, problem_id):
    """Mark an exception as processed in Azure Table."""
    table_client = get_table_client()
    entity = {
        'PartitionKey': 'exceptions',
        'RowKey': timestamp,
        'ProblemId': problem_id,
        'ProcessedDate': datetime.utcnow().isoformat()
    }
    table_client.create_entity(entity=entity)

def query_app_insights():
    """Query Application Insights for exceptions data."""
    try:
        if 'APPINSIGHTS_APP_ID' not in os.environ:
            print("ERROR: APPINSIGHTS_APP_ID environment variable is not set")
            return []
        if 'APPINSIGHTS_API_KEY' not in os.environ:
            print("ERROR: APPINSIGHTS_API_KEY environment variable is not set")
            return []

        app_id = os.environ['APPINSIGHTS_APP_ID']
        api_key = os.environ['APPINSIGHTS_API_KEY']
        
        # Simplified query with no filters, just last 24h
        query = """
        exceptions
        | where timestamp >= ago(24h)
        | project timestamp, problemId, details=message
        | order by timestamp desc
        """
        
        url = f"https://api.applicationinsights.io/v1/apps/{app_id}/query"
        headers = {
            "X-Api-Key": api_key,
            "Accept": "application/json"
        }
        
        print(f"\nQuerying App Insights...")
        print(f"URL: {url}")
        print(f"Query:\n{query}")
        
        response = requests.get(
            url,
            headers=headers,
            params={"query": query},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return []
            
        data = response.json()
        print(f"\nRaw Response: {json.dumps(data, indent=2)}")
        
        if 'tables' not in data or not data['tables']:
            print("No tables in response")
            return []
            
        table = data['tables'][0]
        
        # Print column information
        if 'columns' in table:
            print("\nColumns:", [col['name'] for col in table['columns']])
        
        rows = table.get('rows', [])
        print(f"\nFound {len(rows)} exceptions")
        
        if rows:
            print("Sample first row:", rows[0])
        
        return rows
        
    except Exception as e:
        print(f"Query error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def create_jira_issue(summary, description, timestamp):
    """Create a Jira issue (Bug) with the given summary and description."""
    jira_url = "https://apeirosai.atlassian.net/rest/api/3/issue"
    jira_email = os.environ['JIRA_EMAIL']
    jira_api_token = os.environ['JIRA_API_TOKEN']
    auth = (jira_email, jira_api_token)
    
    # Add timestamp to the description
    full_description = f"Exception Time (UTC): {timestamp}\n\n{description}"
    
    payload = {
        "fields": {
            "project": {"key": "TES"},
            "summary": f"{summary} - {timestamp}",
            "description": full_description,
            "issuetype": {"name": "Bug"}
        }
    }
    response = requests.post(jira_url, json=payload, auth=auth)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {"error": "Could not parse response", "raw": response.text}
    
    print(f"Jira API response for issue '{summary}': Status Code {response.status_code}, "
          f"Response: {json.dumps(resp_json, indent=2)}")
    return response.status_code, resp_json

@app.route('/events', methods=['POST'])
def handle_eventgrid():
    """Handle incoming events and create Jira tickets for new exceptions."""
    events = request.get_json()
    
    if isinstance(events, list) and events and events[0].get('eventType') == 'Microsoft.EventGrid.SubscriptionValidationEvent':
        validation_code = events[0]['data']['validationCode']
        return jsonify({'validationResponse': validation_code})
    
    print("Received payload:", json.dumps(events, indent=2))
    
    exceptions = query_app_insights()
    print(f"Number of exceptions returned: {len(exceptions)}")
    
    created = 0
    skipped = 0
    errors = []
    
    for row in exceptions:
        if len(row) < 3:  # We need problemId, details, and timestamp
            print("Skipping row (not enough columns):", row)
            continue

        problem_id = row[0]
        details = row[1]
        timestamp = row[2]
        
        # Format timestamp to be valid for Azure Table Storage
        formatted_timestamp = timestamp.replace(':', '-').replace('.', '-')
        
        # Skip if this exact exception occurrence was already processed
        if is_exception_processed(formatted_timestamp):
            skipped += 1
            continue

        status, jira_response = create_jira_issue(
            summary=problem_id,
            description=details,
            timestamp=timestamp
        )
        
        if status == 201:
            created += 1
            mark_exception_processed(formatted_timestamp, problem_id)
        else:
            errors.append(jira_response)

    return jsonify({
        "message": f"Processed exceptions. Created {created} Jira bugs, skipped {skipped} already processed exceptions.",
        "errors": errors
    })

@app.route('/appget', methods=['GET'])
def get_app_insights_data():
    """Get endpoint to fetch and display App Insights data."""
    print("\n=== Starting /appget request ===")
    
    try:
        exceptions = query_app_insights()
        
        # Simplified response with minimal processing
        response_data = {
            "count": len(exceptions),
            "exceptions": [
                {
                    "timestamp": row[0],
                    "problemId": row[1],
                    "details": row[2]
                }
                for row in exceptions
            ],
            "query_time": datetime.utcnow().isoformat()
        }
        
        print(f"\nReturning {len(exceptions)} exceptions")
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in endpoint: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": error_msg,
            "count": 0,
            "exceptions": [],
            "query_time": datetime.utcnow().isoformat()
        })

@app.route('/ps', methods=['GET'])
def get_powershell_script():
    """Generate and return a PowerShell script using configured App Insights credentials."""
    app_id = os.environ.get('APPINSIGHTS_APP_ID')
    api_key = os.environ.get('APPINSIGHTS_API_KEY')
    
    if not app_id or not api_key:
        return "Error: App Insights credentials not configured", 500
    
    script = f'''
# PowerShell Script to Query Application Insights Exceptions
# Generated by JiraBug Service

$AppId = "{app_id}"
$ApiKey = "{api_key}"

$Query = @"
exceptions
| where timestamp >= ago(24h)
| project 
    timestamp,
    problemId,
    message,
    type,
    outerMessage,
    details=customDimensions,
    cloud_RoleName,
    operation_Name
| order by timestamp desc
"@

$Headers = @{{
    'X-Api-Key' = $ApiKey
    'Content-Type' = 'application/json'
}}

$Url = "https://api.applicationinsights.io/v1/apps/$AppId/query"

try {{
    Write-Host "`nQuerying Application Insights for exceptions in the last 24 hours..."
    Write-Host "URL: $Url`n"

    $Response = Invoke-RestMethod `
        -Uri $Url `
        -Headers $Headers `
        -Method Get `
        -Body @{{ 'query' = $Query }}

    if ($Response.tables.rows.Count -eq 0) {{
        Write-Host "No exceptions found in the last 24 hours"
    }} else {{
        Write-Host "Found $($Response.tables.rows.Count) exceptions`n"
        
        # Get column names
        $Columns = $Response.tables[0].columns.name
        
        # Format and display results as a table
        $Results = $Response.tables[0].rows | ForEach-Object {{
            $Row = $_
            $Properties = [ordered]@{{}}
            
            for ($i = 0; $i -lt $Columns.Count; $i++) {{
                $Properties[$Columns[$i]] = $Row[$i]
            }}
            
            New-Object PSObject -Property $Properties
        }}

        # Display results in a grid view
        $Results | Out-GridView -Title "Application Insights Exceptions"
        
        # Also save to CSV
        $DateTime = Get-Date -Format "yyyy-MM-dd_HH-mm"
        $CsvPath = ".\AppInsights_Exceptions_$DateTime.csv"
        $Results | Export-Csv -Path $CsvPath -NoTypeInformation
        Write-Host "Results saved to: $CsvPath"
    }}
}} catch {{
    Write-Host "Error occurred while querying Application Insights:"
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nStack Trace:"
    Write-Host $_.Exception.StackTrace -ForegroundColor Red
}}
'''
    
    # Return the script with proper content type
    return script, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
