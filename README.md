---
page_type: sample
languages:
- azdeveloper
- python
- bicep
products:
- azure
- azure-functions
urlFragment: fastapi-on-azure-functions
name: Using FastAPI Framework with Azure Functions
description: This is a sample Azure Function app created with the FastAPI framework.
---
<!-- YAML front-matter schema: https://review.learn.microsoft.com/en-us/help/contribute/samples/process/onboarding?branch=main#supported-metadata-fields-for-readmemd -->

# Using FastAPI Framework with Azure Functions

Azure Functions supports WSGI and ASGI-compatible frameworks with HTTP-triggered Python functions. This can be helpful if you are familiar with a particular framework, or if you have existing code you would like to reuse to create the Function app. The following is an example of creating an Azure Function app using FastAPI.

## Prerequisites

You can develop and deploy a function app using either Visual Studio Code or the Azure CLI. Make sure you have the required prerequisites for your preferred environment:

* [Prerequisites for VS Code](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python#configure-your-environment)
* [Prerequisites for Azure CLI](https://docs.microsoft.com/azure/azure-functions/create-first-function-cli-python#configure-your-local-environment)

## Setup

Clone or download [this sample's repository](https://github.com/Azure-Samples/fastapi-on-azure-functions/), and open the `fastapi-on-azure-functions` folder in Visual Studio Code or your preferred editor (if you're using the Azure CLI).

## Using FastAPI Framework in an Azure Function App

The code in the sample folder has already been updated to support use of the FastAPI. Let's walk through the changed files.

The `requirements.txt` file has an additional dependency of the `fastapi` module:

```
azure-functions
fastapi
```


The file host.json includes the a `routePrefix` key with a value of empty string.

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
        "routePrefix": ""
    }
  }
}
```


The root folder contains `function_app.py` which initializes an `AsgiFunctionApp` using the imported `FastAPI` app:

```python
import azure.functions as func

from WrapperFunction import app as fastapi_app

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
```

In the `WrapperFunction` folder, the `__init__.py` file defines a FastAPI app in the typical way (no changes needed):

```python
import azure.functions as func

import fastapi

app = fastapi.FastAPI()

@app.get("/sample")
async def index():
    return {
        "info": "Try /hello/Shivani for parameterized route.",
    }


@app.get("/hello/{name}")
async def get_name(name: str):
    return {
        "name": name,
    }
```

## Running the sample

### Testing locally

1. (Optional, recommended) Run the first-time setup script:

    ```bash
    bash ./setup.sh
    ```

    This creates `.venv`, installs Python dependencies, and pre-downloads the Azure Functions extension bundle (when `func` is installed).

2. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

3. Run the command below to install the necessary requirements.

    ```log
    python -m pip install -r requirements.txt
    ```

4. If you are using VS Code for development, click the "Run and Debug" button or follow [the instructions for running a function locally](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python#run-the-function-locally). Outside of VS Code, follow [these instructions for using Core Tools commands directly to run the function locally](https://docs.microsoft.com/azure/azure-functions/functions-run-local?tabs=v4%2Cwindows%2Cpython%2Cportal%2Cbash#start).

5. Once the function is running, test the function at the local URL displayed in the Terminal panel:
```log
Functions:
        http_app_func: [GET,POST,DELETE,HEAD,PATCH,PUT,OPTIONS] http://localhost:7071//{*route}
```

    ```log
    Functions:
            WrapperFunction: [GET,POST] http://localhost:7071/{*route}
    ```

    Try out URLs corresponding to the handlers in the app, both the simple path and the parameterized path:

    ```
    http://localhost:7071/sample
    http://localhost:7071/hello/YourName
    ```

### Environment, Auth, and CORS configuration

The function app supports environment-driven behavior using these app settings:

- `APP_ENV` (default: `development`)
- `APP_NAME` (default: `fastapi-on-azure-functions`)
- `AUTH_ENABLED` (`true`/`false`, default: `false`)
- `AUTH_BEARER_TOKEN` (required when `AUTH_ENABLED=true`)
- `CORS_ALLOW_ORIGINS` (comma-separated, default: `*`)
- `CORS_ALLOW_CREDENTIALS` (`true`/`false`, default: `false`)
- `CORS_ALLOW_METHODS` (comma-separated, default: `*`)
- `CORS_ALLOW_HEADERS` (comma-separated, default: `*`)

When auth is enabled, requests to `/sample` and `/hello/{name}` must include an `Authorization` header with the configured bearer token.

### Production Azure infrastructure defaults

The infrastructure templates now default to a production-ready baseline:

- Premium Functions plan (`EP1`, `ElasticPremium`)
- System-assigned managed identity for the Function App
- Key Vault for storing auth token secrets
- CORS restricted via `frontendAllowedOrigins` infra parameter
- Autoscale profile for Premium plans
- Function App metric alerts for `Http5xx` and `AverageResponseTime`
- Optional API Management (`deployApiManagement`, default `false`)

To stay near a cost-sensitive setup (around low hundreds/month), keep:

- `minimumElasticInstanceCount` at `1`
- `deployApiManagement` as `false` unless needed
- `functionAppScaleLimit` to a controlled value (for example `10`)

If `authBearerToken` is left empty during deployment, set it later in Key Vault and restart the function app.

### Deploying to Azure

There are three main ways to deploy this to Azure:

* [Deploy with the VS Code Azure Functions extension](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python#publish-the-project-to-azure). 
* [Deploy with the Azure CLI](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?tabs=azure-cli%2Cbash%2Cbrowser#create-supporting-azure-resources-for-your-function).
* Deploy with the Azure Developer CLI: After [installing the `azd` tool](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=localinstall%2Cwindows%2Cbrew), run `az login`, `azd auth login`, and `azd up` in the root of the project. You can also run `azd pipeline config` to set up a CI/CD pipeline for deployment.

All approaches will provision a Function App, Storage account (to store the code), and a Log Analytics workspace.

![Azure resources created by the deployment: Function App, Storage Account, Log Analytics workspace](./readme_diagram.png)

### Testing in Azure

After deployment, test these different paths on the deployed URL: 

```
http://<FunctionAppName>.azurewebsites.net/sample
http://<FunctionAppName>.azurewebsites.net/hello/Foo
```
You can call the URL endpoints using your browser (GET requests) or one one of these HTTP test tools:

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
- `POST/GET /universes` and `GET /universes/{universe_id}` for isolated lore universes
- `POST/GET /characters` for universe-scoped character creation
- `POST/GET /stories` with continuity checks and optional crossover support
- `POST /merch-designs` for hoodie/t-shirt design workflow metadata
- `POST /image-edits` for image-edit requests against existing assets
- `GET /assets`, `GET /assets/{asset_id}`, and `POST /assets/{asset_id}/versions/{version}/restore` for asset version history

Calling the restore endpoint is intentionally non-idempotent: each call creates additional version-history entries (checkpoint + restore event).

Important: these routes currently use process-local in-memory state, so data resets on restart and is not shared across scaled-out instances.
They are intended as scaffolding for a future persistent backend.
