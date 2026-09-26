# Python 3.10 and Azure Functions

This template creates an Azure Functions project with FastAPI and demonstrates how to use HTTP-triggered functions to route requests into an ASGI application.

## Running locally

Install Python 3.10, the Azure Functions Core Tools, and the dependencies from `requirements.txt`, then start the host with the Functions Core Tools.

## Testing in Azure

After deployment, test these different paths on the deployed URL:

```
http://<FunctionAppName>.azurewebsites.net/sample
http://<FunctionAppName>.azurewebsites.net/hello/Foo
```

You can call the URL endpoints using your browser (GET requests) or one of these HTTP test tools:

- [Visual Studio Code](https://code.visualstudio.com/download) with an [extension from Visual Studio Marketplace](https://marketplace.visualstudio.com/vscode)
- [PowerShell Invoke-RestMethod](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/invoke-restmethod)
- [Microsoft Edge - Network Console tool](https://learn.microsoft.com/microsoft-edge/devtools-guide-chromium/network-console/network-console-tool)
- [Bruno](https://www.usebruno.com/)
- [curl](https://curl.se/)

> [!CAUTION]
> For scenarios where you have sensitive data, such as credentials, secrets, access tokens,
> API keys, and other similar information, make sure to use a tool that protects your data
> with the necessary security features, works offline or locally, doesn't sync your data to
> the cloud, and doesn't require that you sign in to an online account. This way, you reduce
> the risk around exposing sensitive data to the public.

## Next Steps

Now you have a simple Azure Function App using the FastAPI framework, and you can continue building on it to develop more sophisticated applications.

To learn more about leveraging WSGI and ASGI-compatible frameworks, see [Web frameworks](https://docs.microsoft.com/azure/azure-functions/functions-reference-python?tabs=asgi%2Cazurecli-linux%2Capplication-level#web-frameworks).

## Karma creative API extensions

This sample now includes additional API routes for a creative assistant profile named `Karma`:

- When `AUTH_ENABLED=true`, these routes require an `Authorization` header containing the configured token value.
- `GET/PATCH /identity` for assistant identity, tone, and lore
- Identity includes an explicit authority rule: the user is the final decision-maker
- `GET/PUT /preferences` for full-profile updates to remembered likes, dislikes, and output preferences
- `POST /structure-thought` to transform non-linear input into a structured plan with direct feasibility feedback
- `GET /knowledge-bases` to list built-in knowledge bases
- `GET /knowledge-bases/{knowledge_base_id}` to retrieve a specific knowledge base (including alias lookup, for example `bytedance` -> `bytedanabe`)
- Built-in knowledge bases now include `bytedanabe`, `lark`, `wix`, `website-building`, `shopify`, `amazon`, and `sales-strategies-analytics`
- `POST/GET /universes` and `GET /universes/{universe_id}` for isolated lore universes
- `POST/GET /characters` for universe-scoped character creation
- `POST/GET /stories` with continuity checks and optional crossover support
- `POST /merch-designs` for `hoodie`/`tshirt` design workflow metadata
- `POST /image-edits` for image-edit requests against existing assets
- `GET /assets`, `GET /assets/{asset_id}`, and `POST /assets/{asset_id}/versions/{version}/restore` for asset version history
- `POST /plugins/drafts`, `POST /plugins/{id}/validate`, `POST /plugins/{id}/staging-test`, and `POST /plugins/{id}/approval-request` for plugin lifecycle
- `PATCH /plugins/{id}/version`, `PATCH /plugins/{id}/enabled`, `POST /plugins/{id}/rollback`, and `POST /plugins/{id}/kill` for controlled release and kill switch operations
- `POST /skills`, `GET /skills`, and `PATCH /skills/{id}/enabled` for skill registry with external-access approval gates
- `POST /approvals`, `GET /approvals`, and `POST /approvals/{id}/decision` for explicit owner approval workflows
- `POST /learning/events`, `GET /learning/events`, `POST /playbooks`, and `GET /playbooks` for self-learning event capture and playbook generation
- `POST /learning/policy/approval-request`, `GET /learning/policy`, and `PUT /learning/policy` for approval-gated learning-policy changes (`auto_approve_low_risk_tuning`)

Lifecycle notes for approval-gated plugin flows:

- Draft plugins must be validated and staged before `/plugins/{id}/approval-request` can succeed.
- Plugins cannot be enabled while an approval decision is pending, and enablement requires an approved publish or update request.
- Version updates are limited to already-live or rolled-back plugins; approved updates promote the plugin back to an enabled state.

Calling the restore endpoint is intentionally non-idempotent: each call creates additional version-history entries (checkpoint + restore event).

For approval-gated routes, actor identity comes from the request context: when auth is disabled the service reads `X-Actor-Id`, and when auth is enabled it uses the authenticated owner context and ignores caller-supplied `requested_by` fields.

These routes use an in-memory store intended as scaffolding for a future persistent backend, so data resets on restart and is not shared across scaled-out instances.
