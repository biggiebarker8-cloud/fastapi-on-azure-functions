metadata description = 'Creates an optional API Management instance with the Function App as backend.'
param name string
param location string = resourceGroup().location
param tags object = {}
param functionAppUri string
param skuName string = 'Consumption'
param publisherName string = 'Agency Platform'
param publisherEmail string = 'admin@example.com'

resource apiManagement 'Microsoft.ApiManagement/service@2022-08-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    capacity: 0
  }
  properties: {
    publisherName: publisherName
    publisherEmail: publisherEmail
  }
}

resource backend 'Microsoft.ApiManagement/service/backends@2022-08-01' = {
  name: 'function-backend'
  parent: apiManagement
  properties: {
    protocol: 'http'
    url: functionAppUri
  }
}

output name string = apiManagement.name
