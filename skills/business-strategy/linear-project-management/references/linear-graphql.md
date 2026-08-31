# Linear GraphQL Reference

Endpoint: `https://api.linear.app/graphql`
Auth header: `Authorization: {LINEAR_ACCESS_TOKEN}`
Always query your workspace for status IDs first — they are not global constants.

## Statuses (fetch first)

```graphql
query { projectStatuses { nodes { id name } } }
```
Common names: `Backlog`, `Planned`, `In Progress`, `Completed`, `Canceled`.

## Discovery before create

```graphql
query FindIssue($title: String!) {
  issues(filter: { title: { contains: $title } }, first: 5) { nodes { id title } }
}
```

## Create issue

```graphql
mutation CreateIssue($title: String!, $teamId: String!, $description: String!) {
  issueCreate(input: { title: $title, teamId: $teamId, description: $description }) {
    success issue { id identifier }
  }
}
```

## Create project (set BOTH description and content)

```graphql
mutation CreateProject($name: String!, $description: String!, $content: String!) {
  projectCreate(input: { name: $name, description: $description, content: $content }) {
    success project { id }
  }
}
```

## Milestone / resource link

```graphql
mutation Milestone($projectId: String!, $name: String!, $description: String!) {
  projectMilestoneCreate(input: { projectId: $projectId, name: $name, description: $description }) {
    success milestone { id }
  }
}
mutation Resource($url: String!, $label: String!, $projectId: String!) {
  entityExternalLinkCreate(input: { url: $url, label: $label, projectId: $projectId }) {
    success { entity { id } }
  }
}
```

## Bulk state change (loop in the SDK, or N issueUpdate calls)

```graphql
mutation UpdateState($issueId: String!, $stateId: String!) {
  issueUpdate(id: $issueId, input: { stateId: $stateId }) { success }
}
```

Source of the API patterns (MIT): wrsmith108/linear-claude-skill —
https://github.com/wrsmith108/linear-claude-skill