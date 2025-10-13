# Hermine-data

This repo is meant to host shared data (licences and compliance actions) related to the Hermine project.
It is still very much a work in progress.

Default licence for this repo is  ODbL-1.0.

Download the latest [shared.json](https://gitlab.com/hermine-project/community-data/-/releases/permalink/latest/downloads/shared.json) file and refer to [Hermine's documentation](https://docs.hermine-foss.org/reference_data.html) to import them in your Hermine instance.

If you want to get the data in an importable form even if they have not been released yet:

- Clone this repository
- From the root folder of the repo :

```shell
python to_dist.py
```

This will generate a `shared.json` in the `dist` folder, that you can use like the one you would get from the link above.
