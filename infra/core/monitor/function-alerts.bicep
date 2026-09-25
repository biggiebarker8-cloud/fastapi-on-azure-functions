metadata description = 'Creates metric alerts for Azure Function reliability and latency.'
param name string
param functionAppName string
param enabled bool = true

resource functionApp 'Microsoft.Web/sites@2022-03-01' existing = {
  name: functionAppName
}

resource high5xxAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${name}-5xx-alert'
  location: 'global'
  properties: {
    description: 'Alert when Function App HTTP 5xx count is elevated.'
    severity: 2
    enabled: enabled
    scopes: [
      functionApp.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'Http5xxThreshold'
          metricName: 'Http5xx'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Total'
        }
      ]
    }
    autoMitigate: true
    actions: []
  }
}

resource highLatencyAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${name}-latency-alert'
  location: 'global'
  properties: {
    description: 'Alert when Function App average response time is high.'
    severity: 3
    enabled: enabled
    scopes: [
      functionApp.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT10M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'AverageResponseTimeThreshold'
          metricName: 'AverageResponseTime'
          operator: 'GreaterThan'
          threshold: 2000
          timeAggregation: 'Average'
        }
      ]
    }
    autoMitigate: true
    actions: []
  }
}
