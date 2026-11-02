// Holdmate board on Azure Container Apps (Consumption = ~free for demo).
// Deploy tomorrow with the commands in infra/README.md.
param location string = resourceGroup().location
param image string // e.g. ghcr.io/kizouker/adaptive-ivr-board:v0.3.2
param containerPort int = 80

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'holdmate-env'
  location: location
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'holdmate-board'
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: containerPort
      }
    }
    template: {
      containers: [
        {
          name: 'board'
          image: image
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
    }
  }
}

output fqdn string = app.properties.configuration.ingress.fqdn
