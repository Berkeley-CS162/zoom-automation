# Zoom Automation

Repository to store Python scripts that automate tasks in Zoom.

## Rationale

Most of these scripts utilize Selenium instead of interfacing with the Zoom API. 

Though updates to the Zoom web interface may break some behavior and require updates, using the Zoom API requires the application to be approved by Zoom and/or UC Berkeley, and the official Zoom API [limits you to 100 meeting API requests per day](https://marketplace.zoom.us/docs/api-reference/rate-limits#daily-meeting-createupdate-requests).

## Using Selenium

+ Install the Selenium package: `pip install selenium`
+ Download a [Selenium WebDriver](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/) for the browser and browser version you intend on using, and place it somewhere in your path.
