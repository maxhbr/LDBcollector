rootProject.name = "ORT Scripting Environment"

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }

    versionCatalogs {
        create("ortLibs") {
            from("org.ossreviewtoolkit:version-catalog:66.0.3")
        }
    }
}
