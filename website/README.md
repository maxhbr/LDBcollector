# License Lynx

## License Lynx Web API

The License Lynx Web API simulates an API environment but functions as a file directory hosted on GitLab Pages. 
To maintain compatibility with this structure, any entry containing a / must be replaced with an _. 
Below are the instructions for making this replacement in both Windows and Linux systems.

The API call format is: `/api/license/{license_name}`


### Usage Instructions
#### Windows
To replace / with _ in a string using PowerShell, use the following command. Note that double quotes are necessary:

```bash
"license w/ slash" -replace '/', '_'
```

#### Linux
For Linux, you can achieve the same replacement using sed. The following command demonstrates this:

```bash
echo license w/ slash | sed 's/\//_/g'
```

## License

Unless otherwise noted, the contents of the website is licensed under [CC-BY-4.0](LICENSE.md).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED