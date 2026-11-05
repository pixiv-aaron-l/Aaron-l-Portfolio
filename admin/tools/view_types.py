import os


# // the one place that says which kinds of file get a "View" button.
# // Only things a browser can really show: text, html, pdf, images and
# // saved web pages (.mht). Everything else (zip, 7z, ...) is just
# // [ Download ]. The generator and the hosting page both use this, and
# // view_template.html has its own copy of the same lists (keep them in
# // step).

TEXT_VIEW_TYPES = (".txt", ".md", ".log", ".csv")

HTML_VIEW_TYPES = (".html", ".htm")

PDF_VIEW_TYPES = (".pdf",)

IMAGE_VIEW_TYPES = (".png", ".jpg", ".jpeg", ".gif", ".webp")

MHT_VIEW_TYPES = (".mht", ".mhtml")


def get_view_kind(filename):

    # // "page" = a saved web page that has to be rebuilt as a normal page
    # // before a browser can show it. None = nothing to view.

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension in TEXT_VIEW_TYPES:

        return "text"

    if extension in HTML_VIEW_TYPES:

        return "html"

    if extension in PDF_VIEW_TYPES:

        return "pdf"

    if extension in IMAGE_VIEW_TYPES:

        return "image"

    if extension in MHT_VIEW_TYPES:

        return "page"

    return None
