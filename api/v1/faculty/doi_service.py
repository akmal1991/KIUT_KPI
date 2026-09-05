"""Server-side Crossref lookup for the DOI auto-fill button in the Add
Result modal. Crossref has no authoritative quartile data (that's a paid
Scopus/SJR product this project doesn't have access to), so the response
never invents a quartile — the teacher still picks Q1-Q4 manually and the
reviewer confirms it, same as the review workflow already requires."""
import requests

CROSSREF_URL = 'https://api.crossref.org/works/{doi}'
REQUEST_TIMEOUT_SECONDS = 6


def _first(values):
    if not values:
        return None
    return values[0]


def _format_date(date_parts):
    if not date_parts or not date_parts.get('date-parts'):
        return None
    parts = date_parts['date-parts'][0]
    if not parts:
        return None
    year = parts[0]
    month = parts[1] if len(parts) > 1 else 1
    day = parts[2] if len(parts) > 2 else 1
    return f"{year:04d}-{month:02d}-{day:02d}"


def lookup_doi(doi):
    """Returns a dict of publication metadata for `doi`, or None if Crossref
    has no record (or the lookup failed) — callers treat None as a 404."""
    try:
        response = requests.get(CROSSREF_URL.format(doi=doi), timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    message = response.json().get('message', {})
    published = message.get('published-print') or message.get('published-online') or message.get('published')

    return {
        'doi': message.get('DOI', doi),
        'title': _first(message.get('title')),
        'journal': _first(message.get('container-title')),
        'issn': _first(message.get('ISSN')),
        'publisher': message.get('publisher'),
        'published_date': _format_date(published),
    }
