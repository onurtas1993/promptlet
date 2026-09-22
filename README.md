<table>
  <tr>
    <td>

<img src="./promptlet_client/icon.ico" width="128"/>
    </td>
    <td>

# Promptlet
This app exists for one reason: cheaper AI chat. Instead of paying fixed monthly subscription fees, you use your own API key through a proxy and pay only for what you use. No account creation, no cloud sync, no hidden services, and no unnecessary complexity. Just launch the app and start chatting.
    </td>
  </tr>
</table>

## Screenshots


<img src="https://raw.githubusercontent.com/onurtas1993/images/main/promptlet_screenshot1.png" />

<img src="https://raw.githubusercontent.com/onurtas1993/images/main/promptlet_screenshot2.png" />

 

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

## Tagged desktop builds

Pushing a version tag such as `v1.0.0` runs the Windows and Ubuntu build jobs in
GitHub Actions. Each job tests the app, builds a single-file PyInstaller executable,
smoke tests Qt startup, creates a GitHub Release for the tag, and attaches separate
Windows and Ubuntu ZIP files. Each ZIP contains the platform's single executable
and the GPL-3.0 `LICENSE` file. On Ubuntu, restore executable permission after
extracting if needed with `chmod +x Promptlet`. The executable
embeds the Qt `.ui` files and app icon; the Windows executable also uses that icon.
PyInstaller is a build tool installed only by the workflow.

## License

Promptlet is licensed under the GNU General Public License v3.0. See `LICENSE`.

## Local LM Studio

Start LM Studio's server separately. New settings default to the `openai`
provider and `http://127.0.0.1:1234`. Promptlet appends `/v1/chat/completions`,
so enter the server URL **without `/v1`**. Enter the exact model identifier from
LM Studio in Settings. No model is chosen automatically. Leave the API key blank
unless your server requires authentication.

For an existing configuration, use **Use local LM Studio defaults** in Settings,
enter your model ID, then Save. This button clears the previous model and API key.

## Optional AskTheBook integration

AskTheBook runs independently in its own repository. Enable it in Settings and
configure its HTTP URL (suggested default: `http://127.0.0.1:8000`). An optional
document-answer model ID is stored separately; blank means the backend default.
**Refresh prepared documents** lists the server's documents in the background,
using the URL currently entered in the dialog. Save persists the configuration.
No service requests occur automatically or while the integration is disabled.

Click **New Chat** in the sidebar, then choose **Normal Chat** or **Chat with PDF**. The
type is saved with the chat and cannot be switched within a conversation. Normal
chats send conversation history to the configured provider. PDF chats display an
explicit notice that each question is independent.

In a PDF chat, **Attach PDF** uploads a file and selects it when processing
finishes. **Refresh documents** loads previously prepared documents into the
selector. Choose one to ask independent questions. Open or create a separate
normal chat to use the existing provider. Each document request sends only the current
question, document ID, and optional model; no conversation history is sent.
AskTheBook currently generates answers through its independently configured LM
Studio server. Promptlet's normal-chat endpoint and API key do not apply to PDF
questions. Selecting an online normal-chat provider does not change AskTheBook's
generation backend; its current API accepts a model ID, not a provider endpoint.

Document answers include expandable sources and visible backend warnings, saved
with the chat. Document exchanges are excluded from normal-chat provider history.
The selected document is saved with its PDF chat; prepared documents remain on
the AskTheBook server. PDF chats never fall back to normal chat when no document
is selected or the integration is unavailable. No PDF processing runs in Promptlet.

Uploads and questions run in a background thread with a 30-minute read timeout.
There is no cancellation or automatic retry: a timeout or lost connection may
leave processing running. Refresh documents before uploading again, since repeated
uploads create separate documents. Busy/unavailable service errors do not prevent
returning to normal chat after the request finishes.

