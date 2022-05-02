plugins {
    `kotlin-dsl`
}

repositories {
    mavenCentral()
    maven("https://jitpack.io")
}

dependencies {
    implementation("com.github.oss-review-toolkit.ort:model:39d2cab6b0")

    // Leave out the versions so that the same versions as in ORT are used.
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("com.squareup.okhttp3:okhttp")
    implementation("com.vdurmont:semver4j")
}
