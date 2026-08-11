from flask import Blueprint, render_template, abort
from db import get_active_trackers, get_tracker_by_slug

tracker_bp = Blueprint("tracker", __name__)

@tracker_bp.route("/")
def box_office_hub():
    trackers = get_active_trackers()
    return render_template("tracker_hub.html", trackers=trackers)

@tracker_bp.route("/<slug>/")
@tracker_bp.route("/<slug>")
def tracker_detail(slug):
    movie = get_tracker_by_slug(slug)
    if not movie:
        abort(404)
    return render_template("tracker_detail.html", movie=movie)
