# File: flow_helpers.py
"""Helpers for the KidsChores integration's Config and Options flow.

Provides schema builders and input-processing logic for internal_id-based management.
"""

import uuid
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector, config_validation as cv

from .const import (
    ACHIEVEMENT_TYPE_STREAK,
    ACHIEVEMENT_TYPE_TOTAL,
    CHALLENGE_TYPE_DAILY_MIN,
    CHALLENGE_TYPE_TOTAL_WITHIN_WINDOW,
    CONF_ENABLE_MOBILE_NOTIFICATIONS,
    CONF_ENABLE_PERSISTENT_NOTIFICATIONS,
    CONF_MOBILE_NOTIFY_SERVICE,
    CONF_POINTS_LABEL,
    CONF_POINTS_ICON,
    DOMAIN,
    DEFAULT_POINTS_MULTIPLIER,
    DEFAULT_POINTS_LABEL,
    DEFAULT_POINTS_ICON,
    FREQUENCY_DAILY,
    FREQUENCY_MONTHLY,
    FREQUENCY_NONE,
    FREQUENCY_WEEKLY,
)


def build_points_schema(
    default_label=DEFAULT_POINTS_LABEL, default_icon=DEFAULT_POINTS_ICON
):
    """Build a schema for points label & icon."""
    return vol.Schema(
        {
            vol.Required(CONF_POINTS_LABEL, default=default_label): str,
            vol.Optional(
                CONF_POINTS_ICON, default=default_icon
            ): selector.IconSelector(),
        }
    )


def build_kid_schema(
    hass,
    users,
    default_kid_name="",
    default_ha_user_id=None,
    internal_id=None,
    default_enable_mobile_notifications=False,
    default_mobile_notify_service=None,
    default_enable_persistent_notifications=False,
):
    """Build a Voluptuous schema for adding/editing a Kid, keyed by internal_id in the dict."""
    user_options = [{"value": user.id, "label": user.name} for user in users]
    notify_options = _get_notify_services(hass)

    return vol.Schema(
        {
            vol.Required("kid_name", default=default_kid_name): str,
            vol.Optional("ha_user"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=user_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            vol.Required(
                CONF_ENABLE_MOBILE_NOTIFICATIONS,
                default=default_enable_mobile_notifications,
            ): bool,
            vol.Optional(CONF_MOBILE_NOTIFY_SERVICE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=notify_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            vol.Required(
                CONF_ENABLE_PERSISTENT_NOTIFICATIONS,
                default=default_enable_persistent_notifications,
            ): bool,
            vol.Required("internal_id", default=internal_id or str(uuid.uuid4())): str,
        }
    )


def build_parent_schema(
    hass,
    users,
    kids_dict,
    default_parent_name="",
    default_ha_user_id=None,
    default_associated_kids=None,
    default_enable_mobile_notifications=False,
    default_mobile_notify_service=None,
    default_enable_persistent_notifications=False,
    internal_id=None,
):
    """Build a Voluptuous schema for adding/editing a Parent, keyed by internal_id in the dict."""
    user_options = [{"value": user.id, "label": user.name} for user in users]
    kid_options = [
        {"value": kid_id, "label": kid_name} for kid_name, kid_id in kids_dict.items()
    ]
    notify_options = _get_notify_services(hass)

    return vol.Schema(
        {
            vol.Required("parent_name", default=default_parent_name): str,
            vol.Optional("ha_user_id"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=user_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            vol.Optional(
                "associated_kids", default=default_associated_kids or []
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=kid_options,
                    translation_key="associated_kids",
                    multiple=True,
                )
            ),
            vol.Required(
                CONF_ENABLE_MOBILE_NOTIFICATIONS,
                default=default_enable_mobile_notifications,
            ): bool,
            vol.Optional(CONF_MOBILE_NOTIFY_SERVICE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=notify_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            vol.Required(
                CONF_ENABLE_PERSISTENT_NOTIFICATIONS,
                default=default_enable_persistent_notifications,
            ): bool,
            vol.Required("internal_id", default=internal_id or str(uuid.uuid4())): str,
        }
    )


def build_chore_schema(kids_dict, default=None):
    """Build a schema for chores, referencing existing kids by name.

    Uses internal_id for entity management.
    """
    default = default or {}
    chore_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))

    kid_choices = {k: k for k in kids_dict}

    return vol.Schema(
        {
            vol.Required("chore_name", default=chore_name_default): str,
            vol.Optional(
                "chore_description", default=default.get("description", "")
            ): str,
            vol.Required(
                "default_points", default=default.get("default_points", 5)
            ): vol.Coerce(float),
            vol.Required(
                "assigned_kids", default=default.get("assigned_kids", [])
            ): cv.multi_select(kid_choices),
            vol.Required(
                "shared_chore", default=default.get("shared_chore", False)
            ): bool,
            vol.Required(
                "allow_multiple_claims_per_day",
                default=default.get("allow_multiple_claims_per_day", False),
            ): bool,
            vol.Required(
                "partial_allowed", default=default.get("partial_allowed", False)
            ): bool,
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required(
                "recurring_frequency",
                default=default.get("recurring_frequency", FREQUENCY_NONE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        FREQUENCY_NONE,
                        FREQUENCY_DAILY,
                        FREQUENCY_WEEKLY,
                        FREQUENCY_MONTHLY,
                    ],
                    translation_key="recurring_frequency",
                )
            ),
            vol.Optional("due_date", default=default.get("due_date")): vol.Any(
                None, selector.DateTimeSelector()
            ),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


def build_badge_schema(default=None):
    """Build a schema for badges, keyed by internal_id in the dict."""
    default = default or {}
    badge_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))
    points_multiplier_default = default.get(
        "points_multiplier", DEFAULT_POINTS_MULTIPLIER
    )

    return vol.Schema(
        {
            vol.Required("badge_name", default=badge_name_default): str,
            vol.Optional(
                "badge_description", default=default.get("description", "")
            ): str,
            vol.Required(
                "threshold_type",
                default=default.get("threshold_type", "points"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=["points", "chore_count"],
                    translation_key="threshold_type",
                )
            ),
            vol.Required(
                "threshold_value", default=default.get("threshold_value", 10)
            ): vol.Coerce(float),
            vol.Required(
                "points_multiplier",
                default=points_multiplier_default,
            ): vol.All(vol.Coerce(float), vol.Range(min=1.0)),
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


def build_reward_schema(default=None):
    """Build a schema for rewards, keyed by internal_id in the dict."""
    default = default or {}
    reward_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))

    return vol.Schema(
        {
            vol.Required("reward_name", default=reward_name_default): str,
            vol.Optional(
                "reward_description", default=default.get("description", "")
            ): str,
            vol.Required("reward_cost", default=default.get("cost", 10.0)): vol.Coerce(
                float
            ),
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


def build_achievement_schema(kids_dict, chores_dict, default=None):
    """Build a schema for achievements, keyed by internal_id."""
    default = default or {}
    achievement_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))

    kid_choices = {k: k for k in kids_dict}

    chore_options = []
    for chore_id, chore_data in chores_dict.items():
        chore_name = chore_data.get("name", f"Chore {chore_id[:6]}")
        chore_options.append({"value": chore_id, "label": chore_name})

    return vol.Schema(
        {
            vol.Required("name", default=achievement_name_default): str,
            vol.Optional("description", default=default.get("description", "")): str,
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required(
                "assigned_kids", default=default.get("assigned_kids", [])
            ): cv.multi_select(kid_choices),
            vol.Required(
                "type", default=default.get("type", ACHIEVEMENT_TYPE_STREAK)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": ACHIEVEMENT_TYPE_STREAK, "label": "Chore Streak"},
                        {"value": ACHIEVEMENT_TYPE_TOTAL, "label": "Chore Total"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            # If type == "chore_streak", let the user choose the chore to track:
            vol.Optional(
                "selected_chore_id", default=default.get("selected_chore_id")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=chore_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            # For non-streak achievements the user can type criteria freely:
            vol.Optional("criteria", default=default.get("criteria", "")): str,
            vol.Required(
                "target_value", default=default.get("target_value", 1)
            ): vol.Coerce(float),
            vol.Required(
                "reward_points", default=default.get("reward_points", 0)
            ): vol.Coerce(float),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


def build_challenge_schema(kids_dict, chores_dict, default=None):
    """Build a schema for challenges, keyed by internal_id."""
    default = default or {}
    challenge_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))

    kid_choices = {k: k for k in kids_dict}

    chore_options = []
    for chore_id, chore_data in chores_dict.items():
        chore_name = chore_data.get("name", f"Chore {chore_id[:6]}")
        chore_options.append({"value": chore_id, "label": chore_name})

    return vol.Schema(
        {
            vol.Required("name", default=challenge_name_default): str,
            vol.Optional("description", default=default.get("description", "")): str,
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required(
                "assigned_kids", default=default.get("assigned_kids", [])
            ): cv.multi_select(kid_choices),
            vol.Required(
                "type", default=default.get("type", CHALLENGE_TYPE_DAILY_MIN)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {
                            "value": CHALLENGE_TYPE_DAILY_MIN,
                            "label": "Minimum Chores per Day",
                        },
                        {
                            "value": CHALLENGE_TYPE_TOTAL_WITHIN_WINDOW,
                            "label": "Total Chores within Period",
                        },
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            # If type == "chore_streak", let the user choose the chore to track:
            vol.Optional(
                "selected_chore_id", default=default.get("selected_chore_id")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=chore_options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    multiple=False,
                )
            ),
            # For non-streak achievements the user can type criteria freely:
            vol.Optional("criteria", default=default.get("criteria", "")): str,
            vol.Required(
                "target_value", default=default.get("target_value", 1)
            ): vol.Coerce(float),
            vol.Required(
                "reward_points", default=default.get("reward_points", 0)
            ): vol.Coerce(float),
            vol.Optional("start_date", default=default.get("start_date")): vol.Any(
                None, selector.DateTimeSelector()
            ),
            vol.Optional("end_date", default=default.get("end_date")): vol.Any(
                None, selector.DateTimeSelector()
            ),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


def build_penalty_schema(default=None):
    """Build a schema for penalties, keyed by internal_id in the dict.

    Stores penalty_points as positive in the form, converted to negative internally.
    """
    default = default or {}
    penalty_name_default = default.get("name", "")
    internal_id_default = default.get("internal_id", str(uuid.uuid4()))

    # Display penalty points as positive for user input
    display_points = abs(default.get("points", 1)) if default else 1

    return vol.Schema(
        {
            vol.Required("penalty_name", default=penalty_name_default): str,
            vol.Optional(
                "penalty_description", default=default.get("description", "")
            ): str,
            vol.Required("penalty_points", default=display_points): vol.All(
                vol.Coerce(float), vol.Range(min=0.1)
            ),
            vol.Optional(
                "icon", default=default.get("icon", "")
            ): selector.IconSelector(),
            vol.Required("internal_id", default=internal_id_default): str,
        }
    )


# ----------------- HELPERS -----------------


# Penalty points are stored as negative internally, but displayed as positive in the form.
def process_penalty_form_input(user_input: dict) -> dict:
    """Ensure penalty points are negative internally."""
    data = dict(user_input)
    data["points"] = -abs(data["penalty_points"])
    return data


# Get notify services from HA
def _get_notify_services(hass: HomeAssistant) -> list[dict[str, str]]:
    """Return a list of all notify.* services as [{'value': 'notify.foo', 'label': 'notify.foo'}, ...]."""
    services_list = []
    all_services = hass.services.async_services()
    if "notify" in all_services:
        for service_name in all_services["notify"].keys():
            fullname = f"notify.{service_name}"
            services_list.append({"value": fullname, "label": fullname})
    return services_list
