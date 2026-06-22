"""Entry point: build the app via the factory and run it.

Routes live in blueprints under focusedgroup/ (main, stock). Gunicorn uses
``app:app`` (see render.yaml); ``python app.py`` runs the dev server.
"""

import os

from focusedgroup import create_app

app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
