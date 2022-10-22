"""Config flow to configure Heatzy."""
import logging

from heatzypy import HeatzyClient
from heatzypy.exception import HeatzyException, AuthenticationFailed, HttpRequestFailed
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)

_LOGGER = logging.getLogger(__name__)


class HeatzyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Heatzy config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            try:
                self._async_abort_entries_match(
                    {CONF_USERNAME: user_input[CONF_USERNAME]}
                )
                api = HeatzyClient(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                await self.hass.async_add_executor_job(api.is_connected)
                await api.async_close()
            except AuthenticationFailed:
                errors["base"] = "invalid_auth"
            except HttpRequestFailed:
                errors["base"] = "cannot_connect"
            except HeatzyException:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=DOMAIN, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
