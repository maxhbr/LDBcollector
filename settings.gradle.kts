rootProject.name = "ORT Scripting Environment"

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }

    versionCatalogs {
        create("ortLibs") {
            from("org.ossreviewtoolkit:version-catalog:62.1.0")
        }
    }
}
