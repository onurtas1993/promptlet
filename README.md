<table>
  <tr>
    <td>

<img src="./promptlet_client/icon.ico" width="128"/>
    </td>
    <td>

# Promptlet

A lightweight desktop chat client for LLMs that lets you use your own API keys instead of paying for subscriptions.

Supports cloud providers and local models through a very simple interface.
    </td>
  </tr>
</table>

## Screenshots


<table>
  <tr>
    <td>

<img width="100%" alt="Screenshot_20251228-101040-portrait-imageonline co-merged" src="https://raw.githubusercontent.com/onurtas1993/images/refs/heads/main/promptlet_screenshot1.png" />
    </td>
    <td>
<img width="100%" alt="Screenshot_20251228-101040-portrait-imageonline co-merged" src="https://raw.githubusercontent.com/onurtas1993/images/refs/heads/main/promptlet_screenshot2.png" />
    </td>
  </tr>
</table>
 

## Features

* Bring your own API key
* Supports Anthropic and OpenAI APIs including LM Studio
* Simple MVC desktop client

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

## Run

```bash
python -m promptlet_client
```

## Example Configuration

```json
{
    "provider": "anthropic",
    "api_key": "sk-opus-XXXXX",
    "base_url": "https://PROXY_OR_API_URL_HERE",
    "model": "claude-opus-4-8",
    "max_tokens": 4096
}
```

LM Studio example:

```json
{
    "provider": "openai",
    "api_key": "",
    "base_url": "http://127.0.0.1:1234",
    "model": "gemma-4-e2b-it"
}
```

## Project Structure

```text
promptlet_client/
├── controller/
├── model/
├── provider/
├── repository/
├── service/
├── view/
└── worker/
```
