/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx.build;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import javax.annotation.Nonnull;
import javax.inject.Inject;

import org.gradle.api.DefaultTask;
import org.gradle.api.GradleException;
import org.gradle.api.Project;
import org.gradle.api.file.RegularFileProperty;
import org.gradle.api.provider.Property;
import org.gradle.api.tasks.CacheableTask;
import org.gradle.api.tasks.Input;
import org.gradle.api.tasks.InputFile;
import org.gradle.api.tasks.Optional;
import org.gradle.api.tasks.OutputFile;
import org.gradle.api.tasks.PathSensitive;
import org.gradle.api.tasks.PathSensitivity;
import org.gradle.api.tasks.TaskAction;


@CacheableTask
public class EnsureDataTask
    extends DefaultTask
{
    private final RegularFileProperty jsonInputFile;

    private final Property<String> jsonInputProperty;

    private final RegularFileProperty jsonOutputFile;

    private final Property<String> jsonDownloadUrl;



    @Inject
    public EnsureDataTask(@Nonnull final Project pProject)
    {
        jsonInputFile = pProject.getObjects().fileProperty();
        jsonInputProperty = pProject.getObjects().property(String.class);
        jsonOutputFile = pProject.getObjects().fileProperty();
        jsonDownloadUrl = pProject.getObjects().property(String.class);
        setDescription("Ensures that the data file is present, downloading it if necessary.");
    }



    @TaskAction
    public void execute()
    {
        final File dataDir = jsonOutputFile.get().getAsFile().getParentFile();

        checkInputFileReadable();
        createOutputDirectory(dataDir);

        if (jsonInputFile.isPresent()) {
            useProvidedJsonFile();
        }
        else {
            downloadMissingDataFile();
        }
    }



    private static void createOutputDirectory(final File pOutputDir)
    {
        try {
            Files.createDirectories(pOutputDir.toPath());
        }
        catch (IOException e) {
            throw new GradleException("Failed to create output directory: " + pOutputDir, e);
        }
    }



    private void checkInputFileReadable()
    {
        if (jsonInputProperty.isPresent()) {
            if (!jsonInputFile.isPresent()) {
                throw new GradleException(String.format("Bug: '%s' property specified, but no input file configured",
                    BuildPlugin.DATA_FILE_PROPERTY));
            }
            if (!jsonInputFile.get().getAsFile().canRead()) {
                throw new GradleException(String.format("Cannot read JSON file specified via '%s': %s",
                    BuildPlugin.DATA_FILE_PROPERTY, jsonInputFile.get().getAsFile()));
            }
        }
    }



    private void useProvidedJsonFile()
    {
        final File inputFile = jsonInputFile.get().getAsFile();
        getLogger().lifecycle("Using provided data file {}", inputFile);

        final File outputFile = jsonOutputFile.get().getAsFile();
        try {
            Files.copy(inputFile.toPath(), outputFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
        catch (IOException e) {
            throw new GradleException("Failed to copy provided data file", e);
        }
    }



    private void downloadMissingDataFile()
    {
        final File outputFile = jsonOutputFile.get().getAsFile();
        final String simpleName = outputFile.getName();

        getLogger().lifecycle("{} not found. Downloading from {} ...", simpleName, jsonDownloadUrl.get());

        try (
            FileOutputStream fos = new FileOutputStream(outputFile);
            BufferedOutputStream bos = new BufferedOutputStream(fos);
            InputStream inputStream = new URL(jsonDownloadUrl.get()).openStream())
        {
            byte[] buffer = new byte[16384];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                bos.write(buffer, 0, bytesRead);
            }
        }
        catch (IOException e) {
            throw new GradleException(getName() + " failed", e);
        }

        getLogger().lifecycle("Downloaded {} to {}", simpleName, jsonOutputFile.get());
    }



    @Nonnull
    @Optional
    @InputFile
    @PathSensitive(PathSensitivity.NONE)
    public RegularFileProperty getJsonInputFile()
    {
        return jsonInputFile;
    }



    @Input
    @Nonnull
    @Optional
    public Property<String> getJsonInputProperty()
    {
        return jsonInputProperty;
    }



    @Input
    @Nonnull
    public Property<String> getJsonDownloadUrl()
    {
        return jsonDownloadUrl;
    }



    @Nonnull
    @OutputFile
    public RegularFileProperty getJsonOutputFile()
    {
        return jsonOutputFile;
    }
}
