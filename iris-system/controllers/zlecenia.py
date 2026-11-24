from flask import Blueprint, render_template, request, redirect, url_for
from models.zlecenie import (
    pobierz_zlecenie_po_numerze,
    pobierz_szczegoly_zlecenia,
    utworz_zlecenie,
    anuluj_zlecenie,
    przyjmij_sprzet,
    pobierz_wszystkie_zlecenia,
)

zlecenia_bp = Blueprint("zlecenia", __name__)


@zlecenia_bp.route("/", methods=["GET", "POST"])
def w01_index():
    if request.method == "POST":
        numer = request.form.get("numer", "").strip()
        if pobierz_zlecenie_po_numerze(numer):
            return redirect(url_for("zlecenia.w04_status", numer=numer))
        return render_template("w01_index.html", error="Nieprawidłowy numer zlecenia")
    return render_template("w01_index.html")


@zlecenia_bp.route("/zgloszenie", methods=["GET", "POST"])
def w02_form():
    if request.method == "POST":
        ok, numer_zlecenia, error = utworz_zlecenie(request.form)
        if not ok:
            return render_template("w02_form.html", error=error)
        return redirect(url_for("zlecenia.w03_success", numer=numer_zlecenia))
    return render_template("w02_form.html")


@zlecenia_bp.route("/sukces/<numer>")
def w03_success(numer):
    return render_template("w03_success.html", numer=numer)


@zlecenia_bp.route("/status/<numer>", methods=["GET", "POST"])
def w04_status(numer):
    zlecenie = pobierz_szczegoly_zlecenia(numer)
    if not zlecenie:
        return render_template("w01_index.html", error="Nie znaleziono zlecenia.")

    if request.method == "POST":
        ok, error_msg = anuluj_zlecenie(numer)
        if ok:
            return redirect(url_for("zlecenia.w04_status", numer=numer))
        return render_template("w04_status.html", zlecenie=zlecenie, error=error_msg)

    return render_template("w04_status.html", zlecenie=zlecenie)


@zlecenia_bp.route("/panel-technika", methods=["GET", "POST"])
def w05_tech():
    message = None
    if request.method == "POST":
        numer = request.form.get("numer", "").strip()
        _, message = przyjmij_sprzet(numer)

    zlecenia = pobierz_wszystkie_zlecenia()
    return render_template("w05_tech.html", zlecenia=zlecenia, message=message)
