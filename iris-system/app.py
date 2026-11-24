from flask import Flask
from db import close_connection, init_db
from controllers.zlecenia import zlecenia_bp


def create_app():
    init_db()
    app = Flask(__name__)
    app.teardown_appcontext(close_connection)
    app.register_blueprint(zlecenia_bp)

    # Aliasy endpointów dla zgodności z url_for('w01_index') itd. w szablonach
    for name in ("w01_index", "w02_form", "w03_success", "w04_status", "w05_tech"):
        app.add_url_rule(
            app.url_map._rules_by_endpoint.get(f"zlecenia.{name}", [None])[0].rule
            if f"zlecenia.{name}" in app.url_map._rules_by_endpoint
            else "/",
            endpoint=name,
            view_func=app.view_functions[f"zlecenia.{name}"],
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
