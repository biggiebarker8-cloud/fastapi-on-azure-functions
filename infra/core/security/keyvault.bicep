metadata description = 'Creates an Azure Key Vault and an optional auth bearer token secret.'
param name string
param location string = resourceGroup().location
param tags object = {}
param authSecretName string = 'auth-bearer-token'
@secure()
param authSecretValue string = ''

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
  }
}

resource authSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(authSecretValue)) {
  name: authSecretName
  parent: keyVault
  properties: {
    value: authSecretValue
  }
}

output id string = keyVault.id
output name string = keyVault.name
output vaultUri string = keyVault.properties.vaultUri
output authSecretUri string = '${keyVault.properties.vaultUri}secrets/${authSecretName}'
