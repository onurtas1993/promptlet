"""AskTheBook HTTP boundary. PDF processing belongs to the separate server."""

from urllib.parse import urlsplit
from pathlib import Path

import requests


class AskTheBookService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.strip().rstrip("/")
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("Enter a valid AskTheBook HTTP service URL.")
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError("AskTheBook URL must not contain credentials, a query, or a fragment.")

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        try:
            request = requests.get if method == "GET" else requests.post
            response = request(f"{self.base_url}{endpoint}", timeout=(5, 30 if method == "GET" else 1800), **kwargs)
        except requests.Timeout as error:
            raise RuntimeError("AskTheBook timed out. Processing may still continue. Refresh documents before uploading again; repeated uploads create separate documents.") from error
        except requests.RequestException as error:
            raise RuntimeError("AskTheBook is unavailable or the connection was lost. Check its URL and that it is running. Processing may continue; refresh documents before repeating an upload.") from error

        if not response.ok:
            descriptions = {
                404: "Document or endpoint unavailable",
                409: "Service busy; try again when processing finishes",
                422: "Invalid input or incompatible settings",
                503: "Local processing or dependency failure",
            }
            try:
                detail = response.json().get("detail", "")
            except (ValueError, AttributeError):
                detail = ""
            if isinstance(detail, list):
                detail = "; ".join(
                    str(item.get("msg", item)) if isinstance(item, dict) else str(item)
                    for item in detail
                )
            description = descriptions.get(response.status_code, "Request failed")
            raise RuntimeError(f"AskTheBook: {description} (HTTP {response.status_code}). {detail}".strip())

        try:
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
            return data
        except ValueError as error:
            raise RuntimeError("AskTheBook returned an invalid JSON response.") from error

    @staticmethod
    def _valid_document(document) -> bool:
        return (isinstance(document, dict)
                and isinstance(document.get("document_id"), str)
                and bool(document["document_id"])
                and isinstance(document.get("name"), str))

    def upload_document(self, filename: str) -> dict:
        with open(filename, "rb") as file:
            document = self._request("POST", "/documents", files={"file": (Path(filename).name, file, "application/pdf")})
        if not self._valid_document(document):
            raise RuntimeError("AskTheBook returned an invalid upload response. Refresh documents before uploading again.")
        return document

    def ask(self, document_id: str, question: str, model: str = "") -> dict:
        payload = {"document_id": document_id, "question": question}
        if model.strip():
            payload["model"] = model.strip()
        result = self._request("POST", "/ask", json=payload)
        if (not isinstance(result.get("answer"), str)
                or not isinstance(result.get("sources", []), list)
                or any(not isinstance(source, dict) for source in result.get("sources", []))
                or not isinstance(result.get("warnings", []), list)):
            raise RuntimeError("AskTheBook returned an invalid answer response.")
        return result

    def list_documents(self) -> list[dict]:
        try:
            documents = self._request("GET", "/documents")["documents"]
            if not isinstance(documents, list) or any(
                not self._valid_document(item)
                for item in documents
            ):
                raise ValueError("Invalid documents")
            return documents
        except (ValueError, KeyError, TypeError) as error:
            raise RuntimeError("AskTheBook returned an invalid document list.") from error
