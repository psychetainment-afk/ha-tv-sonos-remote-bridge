"""Shared configuration constants."""
DOMAIN = "tv_volume_bridge"
DEFAULT_DEVICE = "Xiaomi RC Consumer Control"
EVENT_BUTTON = "tv_volume_bridge_button"
DEFAULT_BINDINGS = {
    "161": {"name": "green", "kind": "event"},
    "410": {"name": "yellow", "kind": "event"},
    "217": {"name": "blue", "kind": "event"},
    "416": {"name": "Netflix", "kind": "app", "package": "org.jellyfin.androidtv"},
    "150": {"name": "Xiaomi TV+", "kind": "app", "package": "org.jellyfin.androidtv"},
}
