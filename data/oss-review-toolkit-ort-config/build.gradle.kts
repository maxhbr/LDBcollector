val javaLanguageVersion: String by project

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
    implementation(ortLibs.utils.script) // Contains all custom script definitions.
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(javaLanguageVersion)
    }
}

tasks.named<UpdateDaemonJvm>("updateDaemonJvm") {
    languageVersion = JavaLanguageVersion.of(javaLanguageVersion)
    vendor = JvmVendorSpec.ADOPTIUM
}
