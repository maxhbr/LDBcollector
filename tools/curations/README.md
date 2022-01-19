# Curations

This Gradle project contains tasks to manage package curations. For example, tasks that use heuristics to
generate VCS path curations for packages from large multi-module repositories which are tedious which would
otherwise be tedious to write by hand.

## Generating Curations

To list all generation tasks use:

```
./gradlew tasks --group "generate curations"
```

At this time all generation tasks use the GitHub API and therefore require GitHub credentials which need to be passed
as Gradle properties, for example: 

```
./gradlew -P githubUsername=[your username] -P githubToken=[your GitHub API token] generateAspNetCoreCurations 
```

To not add your GitHub token to your shell history, it is recommended to put it into an environment variable.
