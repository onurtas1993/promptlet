<table>
  <tr>
    <td width="144">
      <img src="./promptlet_client/icon.ico" width="128" alt="Promptlet icon" />
    </td>
    <td>

# Promptlet

**A lightweight desktop AI chat client that lets you use your own providers and pay only for what you use.**

Promptlet connects directly to OpenAI-compatible APIs, Anthropic, or a local LM Studio server. There is no Promptlet account, cloud sync, or subscription. Your settings and chat history stay on your computer.
    </td>
  </tr>
</table>

## What you can do

- Chat with OpenAI-compatible and Anthropic models.
- Chat with PDFs through the optional [AskTheBook](https://github.com/onurtas1993/askthebook) integration.
- Run private, local conversations with models served by LM Studio.
- Create separate conversations and keep their history on your computer.
- Adjust the assistant's personality and maximum response length. 

## See Promptlet in action

<img src="https://raw.githubusercontent.com/onurtas1993/images/main/promptlet_screenshot1.png" alt="Promptlet conversation view" />

<img src="https://raw.githubusercontent.com/onurtas1993/images/main/promptlet_screenshot2.png" alt="Promptlet settings view" />

## Get started

### Download the desktop app

Download the latest Windows or Ubuntu archive from [GitHub Releases](https://github.com/onurtas1993/promptlet/releases), extract it, and launch `Promptlet.exe` on Windows or `Promptlet` on Ubuntu.

On Ubuntu, you may need to restore executable permission after extracting:

```bash
chmod +x Promptlet
./Promptlet
```

## How to run

For **normal chat** with an online provider, launch Promptlet and configure your provider, model, base URL, and API key in **Settings**.

For **local chat** or **Chat with PDF**, start the required services in this order:

1. **Start LM Studio.** Download the LLM you want to use, load it, and start the local server. Keep LM Studio and the selected model running while you use Promptlet. The usual server URL is `http://127.0.0.1:1234`.
2. **Download and start AskTheBook.** Clone or download [AskTheBook](https://github.com/onurtas1993/askthebook), follow its installation and configuration instructions, and start its service. AskTheBook must remain running for PDF uploads and questions. Its suggested URL is `http://127.0.0.1:8000`.
3. **Launch Promptlet.** Start the downloaded application, or run `python -m promptlet_client` when working from source.
4. **Configure Promptlet.** Use the LM Studio URL and exact loaded model ID for local normal chat. Under **AskTheBook Integration**, enter the running AskTheBook service URL and, optionally, the model ID it should use for PDF answers.

> [!IMPORTANT]
> AskTheBook relies on its configured LM Studio server to generate PDF answers. LM Studio must already be running with the desired LLM loaded before you start asking questions about a document.

### Configure normal chat

Open **Settings** and choose a normal-chat provider:

- **OpenAI** for OpenAI-compatible endpoints, including LM Studio.
- **Anthropic** for the Anthropic Messages API.

Enter the provider's base URL, exact model identifier, and API key. A local LM Studio server usually does not require an API key. Save the settings, select **New Chat**, and choose **Normal Chat**.

> [!NOTE]
> Promptlet adds the provider API path for you. For LM Studio, enter a server URL such as `http://127.0.0.1:1234` without `/v1` and enter the exact loaded model identifier.

## Chat with a PDF

PDF chat is powered by **AskTheBook**, an optional companion service that prepares documents, retrieves relevant passages, and generates referenced answers. AskTheBook runs independently from Promptlet and must be installed, configured, and started separately.

1. Start the AskTheBook service. Its suggested local URL is `http://127.0.0.1:8000`.
2. In Promptlet **Settings**, enter that URL under **AskTheBook Integration**. Optionally enter a document-answer model ID; leave it blank to use the backend default.
3. Select **New Chat** > **Chat with PDF**.
4. Select **Attach PDF** to upload and prepare a new document, or **Refresh documents** to choose one already prepared by AskTheBook.
5. Ask a question. Expand the answer's sources when you need to see the supporting library references.

Each PDF question is independent: Promptlet sends AskTheBook only the current question, document ID, and optional model ID. Conversation history is not sent. A chat's type is fixed, so create a separate **Normal Chat** when you want a conversational exchange.

> [!IMPORTANT]
> PDF answers use the LM Studio server configured by AskTheBook. They do not use Promptlet's normal-chat provider, endpoint, or API key. Promptlet never processes PDFs itself.

## How Promptlet handles your data

- Promptlet stores settings and chat history locally in the `Promptlet` application-data directory.
- Normal chats send conversation history to the provider configured in Promptlet.
- PDF chats send only the current question and selected document information to the locally running AskTheBook.
- Prepared PDFs remain on the AskTheBook local server.
- Promptlet does not create an account or synchronize your chats through a Promptlet service.

Your selected online provider may have its own data-handling policy.

---

## Developer guide

Promptlet is a Python 3.13 desktop application built with PySide6. Its code follows an MVC-style separation, with repositories for local persistence, providers for model APIs, services for external integrations, and workers for non-blocking requests.

### Run from source

Create and activate a virtual environment, then install the dependencies:

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m promptlet_client
```

**Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m promptlet_client
```

### Run the tests

```bash
python -m unittest discover -s tests -v
```

In a headless Linux environment, set `QT_QPA_PLATFORM=offscreen` before running the tests.

### Project structure

```text
promptlet_client/
├── controller/   # Coordinates views, sessions, providers, and workers
├── model/        # Chat, message, history, and settings data models
├── provider/     # OpenAI-compatible and Anthropic API adapters
├── repository/   # JSON-backed settings and chat-history persistence
├── service/      # Prompt construction and AskTheBook HTTP boundary
├── view/         # PySide6 widgets, styles, and Qt Designer .ui files
└── worker/       # Background normal-chat and document operations
tests/            # Integration and document-chat tests
```

### Provider endpoints

Promptlet appends the appropriate path to the configured base URL:

| Provider setting | Request path | Authentication |
| --- | --- | --- |
| `openai` | `/v1/chat/completions` | Optional bearer token |
| `anthropic` | `/v1/messages` | Anthropic API key |

The OpenAI-compatible adapter sends `model`, `messages`, and `max_completion_tokens`. The Anthropic adapter sends `model`, `system`, `messages`, and `max_tokens`.

### AskTheBook integration details

AskTheBook is deliberately isolated behind `AskTheBookService`; PDF parsing, indexing, retrieval, and answer generation do not belong to this repository. Promptlet uses the companion service to:

- list prepared documents;
- upload a PDF for preparation; and
- ask one document-scoped question at a time.

Document answers, expandable sources, and backend warnings are saved in the PDF chat. Those exchanges are excluded from normal-provider history. If no document is selected or AskTheBook is unavailable, a PDF chat does not fall back to a normal provider.

## License

Promptlet is licensed under the [GNU General Public License v3.0](./LICENSE).
