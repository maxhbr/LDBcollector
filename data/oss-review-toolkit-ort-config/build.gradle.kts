plugins {
    `java-library`
}

repositories {
    mavenCentral()

    exclusiveContent {
        forRepository {
            maven("https://packages.atlassian.com/maven-external")
        }

        filter {
            includeGroupByRegex("(com|io)\\.atlassian\\..*")
            includeVersionByRegex("log4j", "log4j", ".*-atlassian-.*")
        }
    }
}

dependencies {
    implementation(ortLibs.evaluator) // Contains the script definition for \"*.rules.kts\" files.
    implementation(ortLibs.notifier)  // Contains the script definition for \"*.notifications.kts\" files.
    implementation(ortLibs.reporter)  // Contains the script definition for \"*.how-to-fix-text-provider.kts\" files.
}
