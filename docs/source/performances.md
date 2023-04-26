<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Monitoring performances

Using the `docker-compose.yml` file, by setting `HERMINE_PROFILING` to `True`
in your `.env` file, or by setting `ENABLE_PROFILING` env variable if you use
Django development server, you can enable profiling of every requests through
[Silk](https://github.com/jazzband/django-silk).

Results can be accessed at `/silk/` by any user with the `is_superuser` flag 
("Superuser status" in the Django admin interface).