plugins {
    `kotlin-dsl`
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(libs.ortModel)
    implementation(libs.ortNuGetPackageManager)

    // Leave out the versions so that the same versions as in ORT are used.
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("com.squareup.okhttp3:okhttp")
    implementation("org.semver4j:semver4j")
}
