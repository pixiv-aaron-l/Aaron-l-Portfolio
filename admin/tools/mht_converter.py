import base64
import re

from email import message_from_binary_file


# // an .mht file is basically an email: one text/html part (the page)
# // plus every image / stylesheet / font the page used, each one tagged
# // with the address it came from (Content-Location) or a cid: id.
# // Browsers will happily download that from a website but they will
# // NOT display it, so this stitches it back into a single normal HTML
# // page: every resource gets inlined as a data: URI exactly where the
# // page referenced it. No network, no extra files, just one string.


def _decode_html(part):

    payload = part.get_payload(
        decode=True
    ) or b""

    charset = part.get_content_charset() or "utf-8"

    try:

        return payload.decode(
            charset,
            errors="replace"
        )

    except LookupError:

        # // some archives name a charset python has never heard of.
        # // utf-8 with replacement characters beats crashing.

        return payload.decode(
            "utf-8",
            errors="replace"
        )


def _to_data_uri(content_type, payload):

    encoded = base64.b64encode(
        payload
    ).decode("ascii")

    return f"data:{content_type};base64,{encoded}"


def mht_to_html(path):

    """
    Returns the page inside an .mht/.mhtml file as one
    self-contained HTML string, or None if the file can't be read
    or doesn't contain an HTML page at all.
    """

    try:

        with open(
            path,
            "rb"
        ) as file:

            message = message_from_binary_file(
                file
            )

    except Exception:

        return None

    html = None

    # // every non-page part, remembered as (keys, content type, bytes).
    # // "keys" are all the ways the page might refer to it.

    resources = []

    for part in message.walk():

        if part.is_multipart():

            continue

        payload = part.get_payload(
            decode=True
        )

        if payload is None:

            continue

        content_type = part.get_content_type()

        # // the first text/html part is the page itself. Any later
        # // text/html parts (iframes inside the saved page) are kept
        # // as resources instead.

        if content_type == "text/html" and html is None:

            html = _decode_html(
                part
            )

            continue

        keys = []

        location = (
            part.get("Content-Location") or ""
        ).strip()

        content_id = (
            part.get("Content-ID") or ""
        ).strip().strip("<>")

        if location:

            keys.append(
                location
            )

        if content_id:

            keys.append(
                "cid:" + content_id
            )

        if not keys:

            continue

        resources.append(
            (
                keys,
                content_type,
                payload,
                part
            )
        )

    if html is None:

        return None

    # --------------------------------------------------------
    # step 1: everything that isn't CSS becomes a data URI first
    # --------------------------------------------------------

    replacements = []

    for keys, content_type, payload, part in resources:

        if content_type == "text/css":

            continue

        uri = _to_data_uri(
            content_type,
            payload
        )

        for key in keys:

            replacements.append(
                (key, uri)
            )

    # --------------------------------------------------------
    # step 2: CSS files can point at images/fonts themselves, so
    # those get their own references swapped before the CSS is
    # turned into a data URI too.
    # --------------------------------------------------------

    for keys, content_type, payload, part in resources:

        if content_type != "text/css":

            continue

        css = _decode_html(
            part
        )

        for key, uri in replacements:

            css = css.replace(
                key,
                uri
            )

        css_uri = _to_data_uri(
            "text/css",
            css.encode("utf-8")
        )

        for key in keys:

            replacements.append(
                (key, css_uri)
            )

    # --------------------------------------------------------
    # step 3: swap everything into the page. Longest address first
    # so "http://a/b.png?x=1" is never half-eaten by "http://a/b.png".
    # --------------------------------------------------------

    replacements.sort(
        key=lambda pair: len(pair[0]),
        reverse=True
    )

    for key, uri in replacements:

        html = html.replace(
            key,
            uri
        )

        if "&" in key:

            # // inside an HTML attribute a "&" is usually written
            # // "&amp;", so the same address can show up two ways.

            html = html.replace(
                key.replace(
                    "&",
                    "&amp;"
                ),
                uri
            )

    # --------------------------------------------------------
    # step 4: the result gets saved/served as utf-8, so any old
    # charset declaration inside the page has to go or the browser
    # would decode it wrongly.
    # --------------------------------------------------------

    html = re.sub(
        r"<meta[^>]+charset[^>]*>",
        "",
        html,
        flags=re.IGNORECASE
    )

    head_match = re.search(
        r"<head[^>]*>",
        html,
        flags=re.IGNORECASE
    )

    if head_match:

        position = head_match.end()

        html = (
            html[:position]
            + '<meta charset="utf-8">'
            + html[position:]
        )

    else:

        html = '<meta charset="utf-8">' + html

    return html
