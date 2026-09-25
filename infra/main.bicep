targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('App Service plan SKU name. Use Y1 for Consumption or EP1 for Premium.')
param appServiceSkuName string = 'EP1'

@description('App Service plan SKU tier. Use Dynamic for Consumption or ElasticPremium for Premium.')
param appServiceSkuTier string = 'ElasticPremium'

@description('Function app minimum elastic instance count for Premium plans.')
param minimumElasticInstanceCount int = 1

@description('Maximum function app scale-out limit. -1 means platform default.')
param functionAppScaleLimit int = 10

@description('Whether token auth is enabled at the application layer.')
param authEnabled bool = false

@description('Frontend origins allowed for CORS.')
param frontendAllowedOrigins array = [
  'https://your-frontend.example.com'
]

@description('Whether APIM should be provisioned in front of the Function App.')
param deployApiManagement bool = false

@secure()
@description('Initial bearer token value to store in Key Vault. Leave empty and set later if preferred.')
param authBearerToken string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${prefix}-logworkspace'
    applicationInsightsName: '${prefix}-appinsights'
    applicationInsightsDashboardName: '${prefix}-appinsights-dashboard'
  }
}

module storageAccount 'core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: resourceGroup
  params: {
    name: '${toLower(take(replace(prefix, '-', ''), 17))}storage'
    location: location
    tags: tags
  }
}

module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: resourceGroup
  params: {
    name: '${prefix}-plan'
    location: location
    tags: tags
    sku: {
      name: appServiceSkuName
      tier: appServiceSkuTier
    }
  }
}

module keyVault 'core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 20)}-kv'
    location: location
    tags: tags
    authSecretName: 'auth-bearer-token'
    authSecretValue: authBearerToken
  }
}

module functionApp 'core/host/functions.bicep' = {
  name: 'function'
  scope: resourceGroup
  params: {
    name: '${prefix}-function-app'
    location: location
    tags: union(tags, { 'azd-service-name': 'api' })
    alwaysOn: appServiceSkuTier == 'ElasticPremium'
    allowedOrigins: frontendAllowedOrigins
    keyVaultName: keyVault.outputs.name
    minimumElasticInstanceCount: appServiceSkuTier == 'ElasticPremium' ? minimumElasticInstanceCount : -1
    functionAppScaleLimit: functionAppScaleLimit
    appSettings: {
      AzureWebJobsFeatureFlags: 'EnableWorkerIndexing'
      APP_ENV: 'production'
      APP_NAME: 'fastapi-on-azure-functions'
      AUTH_ENABLED: string(authEnabled)
      AUTH_BEARER_TOKEN: !empty(authBearerToken) ? '@Microsoft.KeyVault(SecretUri=${keyVault.outputs.authSecretUri})' : ''
      CORS_ALLOW_ORIGINS: join(frontendAllowedOrigins, ',')
      CORS_ALLOW_CREDENTIALS: 'false'
      CORS_ALLOW_METHODS: '*'
      CORS_ALLOW_HEADERS: '*'
    }
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.10'
    storageAccountName: storageAccount.outputs.name
  }
}


module diagnostics 'core/host/app-diagnostics.bicep' = {
  name: '${name}-functions-diagnostics'
  scope: resourceGroup
  params: {
    appName: functionApp.outputs.name
    kind: 'functionapp'
    diagnosticWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
}

resource functionIdentitySecretUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionApp.outputs.identityPrincipalId)) {
  name: guid(keyVault.outputs.id, functionApp.outputs.identityPrincipalId, 'key-vault-secrets-user')
  scope: resourceGroup
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: functionApp.outputs.identityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

module autoscale 'core/monitor/autoscale.bicep' = if (appServiceSkuTier == 'ElasticPremium') {
  name: 'autoscale'
  scope: resourceGroup
  params: {
    name: '${prefix}-autoscale'
    location: location
    targetResourceId: appServicePlan.outputs.id
    minimumInstanceCount: minimumElasticInstanceCount
  }
}

module functionAlerts 'core/monitor/function-alerts.bicep' = {
  name: 'function-alerts'
  scope: resourceGroup
  params: {
    name: '${prefix}-function'
    location: location
    functionAppName: functionApp.outputs.name
  }
}

module apiManagement 'core/api/apim.bicep' = if (deployApiManagement) {
  name: 'apim'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 35)}-apim'
    location: location
    tags: tags
    functionAppUri: functionApp.outputs.uri
  }
}
