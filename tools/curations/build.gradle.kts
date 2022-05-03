import org.ossreviewtoolkit.tools.curations.GenerateAspNetCoreCurationsTask
import org.ossreviewtoolkit.tools.curations.GenerateAzureSdkForNetCurationsTask
import org.ossreviewtoolkit.tools.curations.GenerateDotNetRuntimeCurationsTask
import org.ossreviewtoolkit.tools.curations.VerifyPackageConfigurationsTask
import org.ossreviewtoolkit.tools.curations.VerifyPackageCurationsTask

tasks {
    register<GenerateAspNetCoreCurationsTask>("generateAspNetCoreCurations")
    register<GenerateAzureSdkForNetCurationsTask>("generateAzureSdkForNetCurations")
    register<GenerateDotNetRuntimeCurationsTask>("generateDotNetRuntimeCurations")

    register<VerifyPackageConfigurationsTask>("verifyPackageConfigurations")
    register<VerifyPackageCurationsTask>("verifyPackageCurations")
}
