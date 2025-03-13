# Test Jira Connection

POST http://your-server:5000/bug

Headers:
Content-Type: application/json

Body:
{
    "summary": "Test Bug Ticket",
    "description": "This is a test bug to verify Jira integration.\n\nEnvironment: Test\nPriority: Medium"
}