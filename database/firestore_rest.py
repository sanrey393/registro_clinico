# database/firestore_rest.py
# Cliente REST ligero para Cloud Firestore (compatible con la API de firebase-admin)
# Permite operar Firestore autenticado con el idToken del usuario sin requerir
# firebase_service_account.json en el equipo cliente.

import datetime
import json
import uuid
import requests


def _encode_value(val) -> dict:
    """Convierte un valor Python al formato TypedValue de Firestore REST v1."""
    if val is None:
        return {"nullValue": None}
    if isinstance(val, bool):
        return {"booleanValue": val}
    if isinstance(val, int):
        return {"integerValue": str(val)}
    if isinstance(val, float):
        return {"doubleValue": val}
    if isinstance(val, (datetime.datetime, datetime.date)):
        if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
            val = datetime.datetime(val.year, val.month, val.day)
        iso = val.isoformat()
        if not iso.endswith("Z") and "+" not in iso:
            iso += "Z"
        return {"timestampValue": iso}
    if isinstance(val, dict):
        return {"mapValue": {"fields": {str(k): _encode_value(v) for k, v in val.items()}}}
    if isinstance(val, (list, tuple)):
        return {"arrayValue": {"values": [_encode_value(v) for v in val]}}
    return {"stringValue": str(val)}


def _decode_value(typed: dict):
    """Convierte un TypedValue de Firestore REST v1 a tipo Python nativo."""
    if not isinstance(typed, dict):
        return typed
    if "nullValue" in typed:
        return None
    if "booleanValue" in typed:
        return bool(typed["booleanValue"])
    if "integerValue" in typed:
        return int(typed["integerValue"])
    if "doubleValue" in typed:
        return float(typed["doubleValue"])
    if "timestampValue" in typed:
        return typed["timestampValue"]
    if "stringValue" in typed:
        return typed["stringValue"]
    if "mapValue" in typed:
        fields = typed["mapValue"].get("fields", {})
        return {k: _decode_value(v) for k, v in fields.items()}
    if "arrayValue" in typed:
        vals = typed["arrayValue"].get("values", [])
        return [_decode_value(v) for v in vals]
    return None


def _encode_fields(data: dict) -> dict:
    return {str(k): _encode_value(v) for k, v in (data or {}).items()}


def _decode_doc(doc_json: dict) -> dict:
    fields = doc_json.get("fields", {})
    return {k: _decode_value(v) for k, v in fields.items()}


class _RestDocumentSnapshot:
    def __init__(self, doc_id: str, data: dict | None, exists: bool):
        self.id = doc_id
        self._data = data or {}
        self.exists = exists

    def to_dict(self) -> dict:
        return dict(self._data) if self.exists else {}


class _RestDocumentRef:
    def __init__(self, client, collection_name: str, doc_id: str):
        self._client = client
        self._col = collection_name
        self.id = doc_id

    @property
    def _doc_path(self) -> str:
        return f"projects/{self._client.project_id}/databases/(default)/documents/{self._col}/{self.id}"

    @property
    def _url(self) -> str:
        return f"{self._client.base_url}/{self._col}/{self.id}"

    def get(self) -> _RestDocumentSnapshot:
        resp = requests.get(self._url, headers=self._client._headers(), timeout=12)
        if resp.status_code == 404:
            return _RestDocumentSnapshot(self.id, None, False)
        resp.raise_for_status()
        return _RestDocumentSnapshot(self.id, _decode_doc(resp.json()), True)

    def set(self, data: dict, merge: bool = False):
        params = []
        if merge and data:
            params = [("updateMask.fieldPaths", str(k)) for k in data.keys()]
        resp = requests.patch(
            self._url,
            headers=self._client._headers(),
            params=params,
            json={"fields": _encode_fields(data)},
            timeout=12,
        )
        resp.raise_for_status()
        return resp.json()

    def update(self, data: dict):
        return self.set(data, merge=True)

    def delete(self):
        resp = requests.delete(self._url, headers=self._client._headers(), timeout=12)
        if resp.status_code != 404:
            resp.raise_for_status()
        return True


_OP_MAP = {
    "==": "EQUAL",
    "!=": "NOT_EQUAL",
    "<": "LESS_THAN",
    "<=": "LESS_THAN_OR_EQUAL",
    ">": "GREATER_THAN",
    ">=": "GREATER_THAN_OR_EQUAL",
    "in": "IN",
    "array_contains": "ARRAY_CONTAINS",
}


class _RestQuery:
    def __init__(self, client, collection_name: str):
        self._client = client
        self._col = collection_name
        self._filters = []
        self._orders = []
        self._limit = None

    def where(self, field: str, op: str, value):
        q = self._clone()
        q._filters.append((field, op, value))
        return q

    def order_by(self, field: str, direction: str = "ASCENDING"):
        q = self._clone()
        dir_norm = "DESCENDING" if str(direction).upper().startswith("DESC") else "ASCENDING"
        q._orders.append((field, dir_norm))
        return q

    def limit(self, n: int):
        q = self._clone()
        q._limit = int(n)
        return q

    def _clone(self):
        q = _RestQuery(self._client, self._col)
        q._filters = list(self._filters)
        q._orders = list(self._orders)
        q._limit = self._limit
        return q

    def stream(self):
        structured: dict = {"from": [{"collectionId": self._col}]}
        if len(self._filters) == 1:
            f, op, val = self._filters[0]
            structured["where"] = {
                "fieldFilter": {
                    "field": {"fieldPath": f},
                    "op": _OP_MAP.get(op, "EQUAL"),
                    "value": _encode_value(val),
                }
            }
        elif len(self._filters) > 1:
            structured["where"] = {
                "compositeFilter": {
                    "op": "AND",
                    "filters": [
                        {
                            "fieldFilter": {
                                "field": {"fieldPath": f},
                                "op": _OP_MAP.get(op, "EQUAL"),
                                "value": _encode_value(val),
                            }
                        }
                        for f, op, val in self._filters
                    ],
                }
            }

        if self._orders:
            structured["orderBy"] = [
                {"field": {"fieldPath": f}, "direction": d}
                for f, d in self._orders
            ]
        if self._limit is not None:
            structured["limit"] = self._limit

        url = f"https://firestore.googleapis.com/v1/projects/{self._client.project_id}/databases/(default)/documents:runQuery"
        resp = requests.post(
            url,
            headers=self._client._headers(),
            json={"structuredQuery": structured},
            timeout=15,
        )
        resp.raise_for_status()
        snaps = []
        for item in resp.json():
            doc = item.get("document")
            if not doc:
                continue
            doc_id = doc["name"].rsplit("/", 1)[-1]
            snaps.append(_RestDocumentSnapshot(doc_id, _decode_doc(doc), True))
        return snaps

    def get(self):
        return self.stream()


class _RestCollection(_RestQuery):
    def document(self, doc_id: str | None = None) -> _RestDocumentRef:
        return _RestDocumentRef(self._client, self._col, doc_id or uuid.uuid4().hex[:20])

    def add(self, data: dict):
        doc_id = uuid.uuid4().hex[:20]
        ref = self.document(doc_id)
        ref.set(data, merge=False)
        return None, ref


class _RestBatch:
    def __init__(self, client):
        self._client = client
        self._writes = []

    def set(self, doc_ref: _RestDocumentRef, data: dict, merge: bool = False):
        write = {
            "update": {
                "name": doc_ref._doc_path,
                "fields": _encode_fields(data),
            }
        }
        if merge and data:
            write["updateMask"] = {"fieldPaths": [str(k) for k in data.keys()]}
        self._writes.append(write)

    def update(self, doc_ref: _RestDocumentRef, data: dict):
        self.set(doc_ref, data, merge=True)

    def delete(self, doc_ref: _RestDocumentRef):
        self._writes.append({"delete": doc_ref._doc_path})

    def commit(self):
        if not self._writes:
            return []
        url = f"https://firestore.googleapis.com/v1/projects/{self._client.project_id}/databases/(default)/documents:commit"
        resp = requests.post(
            url,
            headers=self._client._headers(),
            json={"writes": self._writes},
            timeout=20,
        )
        resp.raise_for_status()
        self._writes.clear()
        return resp.json()


class FirestoreRestClient:
    """Cliente REST compatible con firebase_admin.firestore.client()."""

    def __init__(self, project_id: str, token_provider=None):
        self.project_id = project_id
        self._token_provider = token_provider
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"

    def set_token_provider(self, provider):
        self._token_provider = provider

    def _headers(self) -> dict:
        hdrs = {"Content-Type": "application/json"}
        if callable(self._token_provider):
            tok = self._token_provider()
            if tok:
                hdrs["Authorization"] = f"Bearer {tok}"
        return hdrs

    def collection(self, name: str) -> _RestCollection:
        return _RestCollection(self, name)

    def batch(self) -> _RestBatch:
        return _RestBatch(self)
