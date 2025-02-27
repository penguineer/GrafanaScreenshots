# Grafana Screenshots

> Login to a Grafana Dashboard, take a screenshot and send to MQTT topic


## Configuration

Configuration is done using environment variables:

* `MQTT_BROKER_URL`: The URL of the MQTT broker.
* `MQTT_TOPIC`: The MQTT topic to publish the screenshot data to.
* `GRAFANA_DASHBOARD_URL`: The URL of the Grafana dashboard to capture screenshots from.
* `GRAFANA_USERNAME`: The username to log in to the Grafana dashboard.
* `GRAFANA_PASSWORD`: The password to log in to the Grafana dashboard.
* `WINDOW_WIDTH`: The width of the browser window for capturing screenshots. Default is '1280'.
* `WINDOW_HEIGHT`: The height of the browser window for capturing screenshots. Default is '1024'.
* `CHROME_PROFILE`: Path to a Chrome profile directory to use for the browser. Default is `/app/chrome-profile`.

These environment variables can be set in your system's environment variable settings, or in the script that calls your Python script. For local development, you can also set these variables in a `.env` file and use a tool like `python-dotenv` to load them.


## Maintainers

* Stefan Haun ([@penguineer](https://github.com/penguineer))


## Contributing

PRs are welcome!

If possible, please stick to the following guidelines:

* Keep PRs reasonably small and their scope limited to a feature or module within the code.
* If a large change is planned, it is best to open a feature request issue first, then link subsequent PRs to this issue, so that the PRs move the code towards the intended feature.


## License

[MIT](LICENSE.txt) © 2024 Stefan Haun and contributors
