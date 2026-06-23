plugins {
    id("org.gradle.toolchains.foojay-resolver-convention").version("1.0.0")
}

rootProject.name = "ORT Scripting Environment"

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }

    versionCatalogs {
        create("ortLibs") {
            from("org.ossreviewtoolkit:version-catalog:89.2.0")
        }
    }
}
