/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx.build;

import javax.annotation.Nonnull;

import org.gradle.api.Plugin;
import org.gradle.api.Project;
import org.gradle.api.file.FileCollection;
import org.gradle.api.provider.Provider;
import org.gradle.api.tasks.SourceSet;
import org.gradle.api.tasks.SourceSetContainer;
import org.gradle.api.tasks.TaskProvider;


public class BuildPlugin
    implements Plugin<Project>
{
    static final String DATA_FILE_PROPERTY = "licenselynx.datafile";



    @Override
    public void apply(@Nonnull final Project pRootProject)
    {
        final Project project = pRootProject.getRootProject();

        final TaskProvider<EnsureDataTask> ensureDataTaskProvider = project.getTasks().register("checkAndDownloadJson",
            EnsureDataTask.class);
        ensureDataTaskProvider.configure(t -> {
            t.getJsonDownloadUrl().set("https://licenselynx.org/json/latest/mapping.json");
            t.getJsonOutputFile().set(
                project.getLayout().getBuildDirectory().file("licenselynx/data/merged_data.json"));
            Provider<String> dataFileProperty = project.getProviders().gradleProperty(DATA_FILE_PROPERTY);
            t.getJsonInputProperty().set(dataFileProperty);
            t.getJsonInputFile().fileProvider(dataFileProperty.map(project::file));
        });

        final TaskProvider<CodeGeneratorTask> generateCodeTaskProvider = project.getTasks().register("generateJava",
            CodeGeneratorTask.class);
        generateCodeTaskProvider.configure(t -> {
            t.getJsonFile().set(ensureDataTaskProvider.flatMap(EnsureDataTask::getJsonOutputFile));
            t.getTemplateFiles().setFrom(getTemplateFiles(project));
            t.getGeneratedJavaDir().set(project.getLayout().getBuildDirectory().dir("licenselynx/java"));
        });
    }



    private FileCollection getTemplateFiles(@Nonnull final Project pProject)
    {
        SourceSetContainer sourceSets = pProject.getExtensions().getByType(SourceSetContainer.class);
        SourceSet templatesSourceSet = sourceSets.getByName("templates");
        return templatesSourceSet.getJava();
    }
}
