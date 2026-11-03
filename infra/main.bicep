// Holdmate board on Azure Container Apps (Consumption = ~free for demo).
// Deploy tomorrow with the commands in infra/README.md.
param location string = resourceGroup().location
param image string // e.g. ghcr.io/kizouker/adaptive-ivr-board:v0.3.2
param containerPort int = 80
param budgetEur int = 5
param alertEmail string // budget alerts go here; budgets mail, they never auto-delete

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
      scale: {
        minReplicas: 0
        maxReplicas: 2
      }
    }
  }
}

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'holdmate-monthly-cap'
  properties: {
    category: 'Cost'
    amount: budgetEur
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: '2026-11-01'
    }
    notifications: {
      half: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 50
        contactEmails: [alertEmail]
      }
      almost: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: [alertEmail]
      }
      over: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: [alertEmail]
      }
    }
  }
}

output fqdn string = app.properties.configuration.ingress.fqdn
