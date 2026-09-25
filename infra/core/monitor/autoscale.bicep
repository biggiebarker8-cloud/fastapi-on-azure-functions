metadata description = 'Adds autoscale rules for an Azure App Service plan.'
param name string
param location string = resourceGroup().location
param targetResourceId string
param minimumInstanceCount int = 1
param maximumInstanceCount int = 5
param defaultInstanceCount int = 1

resource autoscaleSettings 'Microsoft.Insights/autoscalesettings@2022-10-01' = {
  name: name
  location: location
  properties: {
    name: name
    enabled: true
    targetResourceUri: targetResourceId
    profiles: [
      {
        name: 'cpu-based-autoscale'
        capacity: {
          minimum: string(minimumInstanceCount)
          maximum: string(maximumInstanceCount)
          default: string(defaultInstanceCount)
        }
        rules: [
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: targetResourceId
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: 70
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: targetResourceId
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT10M'
              timeAggregation: 'Average'
              operator: 'LessThan'
              threshold: 30
            }
            scaleAction: {
              direction: 'Decrease'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT10M'
            }
          }
        ]
      }
    ]
  }
}
