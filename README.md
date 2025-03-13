# JiraBug - Application Insights to Jira Integration

JiraBug is a Flask-based service that bridges Azure Application Insights with Jira, automatically creating and updating Jira tickets based on application exceptions. It helps development teams track and manage production issues efficiently.

## Features

- Automatic Jira ticket creation from App Insights exceptions
- PowerShell script generation for exception querying
- Exception deduplication and grouping
- Customizable Jira ticket fields
- Exception trend analysis
- Real-time exception monitoring

## Configuration

### Required Environment Variables

```env
APPINSIGHTS_APP_ID=your_app_insights_id
APPINSIGHTS_API_KEY=your_api_key
JIRA_TOKEN=your_jira_api_token
JIRA_EMAIL=your_jira_email
JIRA_URL=your_jira_instance_url
JIRA_PROJECT=your_project_key
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

### 2. Using the PowerShell script:
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## License

MIT License