# Python-based JUnit publisher for Azure DevOps Testing Plan Integration

Azure DevOps currently has a very minimalistic integration for automated tests, and a lot of manual setup needs to be done to bring in testing data into ADO for tracking.

This tool automates publishing JUnit test results (any language, testing framework) to Azure DevOps allowing automated tests results can be tracked on AzureDevOps too. 

## How-to run
- Clone this repo.
- [Optional] Create a virtual environment with `python -m venv venv` (or however your Python is setup)
- Install dependencies with `pip install -r requirements.txt`
- Create a config file `config.json`. Refer to the structure of the config file below.
- `cd src`
- Run `python -m testpublisher -S ../config.json` (adjust the path according to your structure)

## Config file
```
{
    "scan_folder": "string",  // Folder to scan for test results. Default: "../coverage_files/"
    "organization": "string",  // Azure DevOps Organization
    "project": "string",  // Azure DevOps Project
    "area_path": "string",  // Area Path of the testing plan
    "iteration_path": "string",  // Iteration Path of the current sprint
    "pat": "string", // Personal Access Token - Generate on ADO 
    "plan_name": "string", // Plan Name
    "log_level": "DEBUG | INFO | WARNING | CRITICAL"  // And others used by Python's logging library
}
```

## Next steps
- Build this into a pip package.
- Fill in current iteration name and number.
- Add a config for creating Test Suites.
- Group certain operations (like search and fetch) to reduce API calls.
- Extract API calls into another layer to reduce code duplication and improve adaptibility.

## Contributing
Contributions are welcome! Please feel free to submit a pull request if you have suggestions for improving the project.<br/>
If there's a better way to do this, please let me know!

## Inspired by 
- https://stackoverflow.com/a/77361403/11509674
- https://github.com/bryanbcook/azdevops-testplan-extension
