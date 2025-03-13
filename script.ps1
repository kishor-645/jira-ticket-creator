# Set your Application Insights App ID and API Key
$appId = "2b879665-6e20-4614-8001-b02148edcae7"
$apiKey = "oq03y6vdtszo760ri4hhnkhqvyczfum2syesuvsj"

# Define the query with time filter and projection
$query = @"
exceptions
| where timestamp >= ago(24h)
| project timestamp, problemId, details=message
| order by timestamp desc
"@

# URL encode the query string using System.Net.WebUtility
$encodedQuery = [System.Net.WebUtility]::UrlEncode($query)

# Construct the full API URL
$url = "https://api.applicationinsights.io/v1/apps/$appId/query?query=$encodedQuery"

Write-Output "Querying Application Insights with URL: $url"

# Invoke the REST method to call the API
try {
    $response = Invoke-RestMethod -Uri $url -Headers @{ "X-Api-Key" = $apiKey } -Method Get
    Write-Output "Response received from Application Insights:"
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Error "Failed to fetch data from Application Insights: $_"
}
