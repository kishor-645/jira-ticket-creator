# JiraBug - Application Insights to Jira Integration

JiraBug is a Flask-based service that bridges Azure Application Insights with Jira, automatically creating and updating Jira tickets based on application exceptions. It helps development teams track and manage production issues efficiently.

## Features

- Automatic Jira ticket creation from App Insights exceptions
- PowerShell script generation for exception querying
- Exception deduplication and grouping
- Customizable Jira ticket fields
- Exception trend analysis
- Real-time exception monitoring
- Manual trigger support for exception processing
- Jira connection testing endpoint

## Configuration

### Required Environment Variables

```env
APPINSIGHTS_APP_ID=your_app_insights_id
APPINSIGHTS_API_KEY=your_api_key
JIRA_TOKEN=your_jira_api_token
JIRA_EMAIL=your_jira_email
JIRA_URL=your_jira_instance_url
JIRA_PROJECT=your_project_key
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
```

## API Endpoints

### 1. Create Jira Ticket from Exception (POST `/create`)

Creates a Jira ticket from exception details:

```bash
POST http://your-server:5000/create

Headers:
Content-Type: application/json

Body:
{
    "title": "NullReferenceException in UserService",
    "description": "Exception occurred in production",
    "exception_details": {
        "type": "System.NullReferenceException",
        "message": "Object reference not set to an instance of an object",
        "stackTrace": "at UserService.GetUser() in UserService.cs:line 45",
        "timestamp": "2024-01-20T10:30:00Z",
        "severity": "Error"
    },
    "labels": ["bug", "production"],
    "priority": "High"
}
```

### 2. Query App Insights Exceptions (GET `/appget`)

Retrieves exceptions from the last 24 hours:

```bash
GET http://your-server:5000/appget
```

### 3. Generate PowerShell Query Script (GET `/ps`)

Generates a PowerShell script for querying App Insights:

```bash
GET http://your-server:5000/ps
```

### 4. Test Jira Connection (POST `/bug`)

Tests Jira integration by creating a test ticket:

```bash
POST http://your-server:5000/bug

Headers:
Content-Type: application/json

Body:
{
    "summary": "Test Bug Ticket",
    "description": "This is a test bug to verify Jira integration.\n\nEnvironment: Test\nPriority: Medium"
}
```

### 5. Manual Exception Processing (POST `/trigger`)

Manually triggers exception processing from App Insights to Jira:

```bash
POST http://your-server:5000/trigger

Headers:
Content-Type: application/json

Body:
{
    "hours": 24  # Optional: Number of hours to look back (default: 24)
}
```

Response format:
```json
{
    "status": "completed",
    "summary": {
        "total_exceptions": 10,
        "tickets_created": 3,
        "exceptions_skipped": 7,
        "errors": 0
    },
    "error_details": null,
    "timestamp": "2024-01-20T15:30:00Z"
}
```

## Postman Collection

Import this collection for testing:

```json
{
  "info": {
    "name": "JiraBug API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Jira Ticket",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "{{base_url}}/create"
        },
        "body": {
          "mode": "raw",
          "raw": "{\n    \"title\": \"Test Exception\",\n    \"description\": \"Test description\",\n    \"exception_details\": {\n        \"type\": \"TestException\",\n        \"message\": \"Test error message\",\n        \"stackTrace\": \"Test stack trace\",\n        \"timestamp\": \"{{$isoTimestamp}}\",\n        \"severity\": \"Error\"\n    },\n    \"labels\": [\"test\"],\n    \"priority\": \"Medium\"\n}"
        }
      }
    },
    {
      "name": "Get Exceptions",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/appget"
        }
      }
    },
    {
      "name": "Get PowerShell Script",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/ps"
        }
      }
    }
  ]
}
```

## Usage Examples

### 1. Creating a Jira ticket using curl:
```bash
curl -X POST http://your-server:5000/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Exception",
    "description": "Critical error in payment service",
    "exception_details": {
        "type": "PaymentException",
        "message": "Payment gateway timeout",
        "stackTrace": "at PaymentService.ProcessPayment()",
        "timestamp": "2024-01-20T10:30:00Z",
        "severity": "Error"
    },
    "labels": ["production", "payment"],
    "priority": "High"
  }'
```

### 2. Testing Jira connection:
```bash
curl -X POST http://your-server:5000/bug \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Test Bug",
    "description": "Testing Jira integration"
  }'
```

### 3. Manually triggering exception processing:
```bash
# Process last 24 hours
curl -X POST http://your-server:5000/trigger

# Process last 48 hours
curl -X POST http://your-server:5000/trigger \
  -H "Content-Type: application/json" \
  -d '{"hours": 48}'
```

### 4. Using the PowerShell script:
1. Access `/ps` endpoint
2. Copy the script content
3. Run in PowerShell
4. View exceptions in grid view and CSV export

## Response Formats

### Success Response:
```json
{
    "status": "success",
    "jira_ticket": "PROJ-123",
    "message": "Jira ticket created successfully"
}
```

### Error Response:
```json
{
    "status": "error",
    "error": "Error description",
    "code": "ERROR_CODE"
}
```

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables
5. Run the application:
   ```bash
   python app.py
   ```

## Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Run tests:
   ```bash
   pytest
   ```

## Best Practices

1. Always include stack traces in exception details
2. Use meaningful titles and descriptions
3. Add relevant labels for better categorization
4. Set appropriate priority levels
5. Test Jira connection using `/bug` endpoint before deployment
6. Use manual trigger (`/trigger`) for testing and backfilling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## Troubleshooting

### Common Issues:

1. Jira Connection Issues:
   - Verify JIRA_EMAIL and JIRA_TOKEN are correct
   - Test connection using `/bug` endpoint
   - Check Jira API permissions

2. App Insights Issues:
   - Verify APPINSIGHTS_APP_ID and APPINSIGHTS_API_KEY
   - Test using `/appget` endpoint
   - Check query timeframe

3. Azure Storage Issues:
   - Verify AZURE_STORAGE_CONNECTION_STRING
   - Check table creation permissions
   - Ensure storage account is accessible
