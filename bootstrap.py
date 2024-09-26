from reactpy import component, html

@component
def BootstrapCSS():
    return html.head(
        html.title("Asesor"),
        html.link({
            "rel": "stylesheet",
            "href": "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css",
            "crossorigin": "anonymous"
        })
    )
