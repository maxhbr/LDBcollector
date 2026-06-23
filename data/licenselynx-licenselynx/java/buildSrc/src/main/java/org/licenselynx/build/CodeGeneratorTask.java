/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx.build;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.annotation.Nonnull;
import javax.inject.Inject;

import groovy.json.JsonSlurper;
import org.gradle.api.DefaultTask;
import org.gradle.api.GradleException;
import org.gradle.api.Project;
import org.gradle.api.file.ConfigurableFileCollection;
import org.gradle.api.file.DirectoryProperty;
import org.gradle.api.file.RegularFileProperty;
import org.gradle.api.tasks.CacheableTask;
import org.gradle.api.tasks.InputFile;
import org.gradle.api.tasks.InputFiles;
import org.gradle.api.tasks.OutputDirectory;
import org.gradle.api.tasks.PathSensitive;
import org.gradle.api.tasks.PathSensitivity;
import org.gradle.api.tasks.TaskAction;


@CacheableTask
public class CodeGeneratorTask
    extends DefaultTask
{
    private static final String INSERTION_MARKER = "/* --- CODEGEN INSERTS HERE --- */";

    /** Java limits the bytecode per method, so we create multiple methods, each with this many put() statements */
    private static final int MAP_INIT_BATCH_SIZE = 500;

    private static final Pattern CUSTOM_ORG_PATTERN =
        Pattern.compile("m\\.put\\(Organization\\.(\\w+?), CustomOrgXxxMap.getLicenseMap\\(\\)\\);");

    private final RegularFileProperty jsonFile;

    private final ConfigurableFileCollection templateFiles;

    private final DirectoryProperty generatedJavaDir;



    private static class LynxMappingException
        extends Exception
    {
        public LynxMappingException()
        {
            super();
        }
    }



    private interface LynxWriter
    {
        void accept(PrintWriter pWriter)
            throws LynxMappingException;
    }



    @Inject
    public CodeGeneratorTask(@Nonnull final Project pProject)
    {
        jsonFile = pProject.getObjects().fileProperty();
        templateFiles = pProject.getObjects().fileCollection();
        generatedJavaDir = pProject.getObjects().directoryProperty();
        setDescription("Generate Java code from the data file.");
    }



    @TaskAction
    public void execute()
    {
        final Map<String, Object> fullJson = parseJsonFile();
        final Set<String> mapNames = fullJson.keySet();

        for (final String mapName : mapNames) {
            final Map<String, Object> innerMap = selectMap(fullJson, mapName);
            if ("stableMap".equals(mapName)) {
                generateMapClass(mapName, innerMap, generatedJavaDir.get().getAsFile(),
                    templateFiles.filter(f -> "StableMap.java".equals(f.getName())).getSingleFile());
            }
            else if ("riskyMap".equals(mapName)) {
                generateMapClass(mapName, innerMap, generatedJavaDir.get().getAsFile(),
                    templateFiles.filter(f -> "RiskyMap.java".equals(f.getName())).getSingleFile());
            }
            else {
                generateMapClass(mapName, innerMap, generatedJavaDir.get().getAsFile(),
                    templateFiles.filter(f -> "CustomOrgXxxMap.java".equals(f.getName())).getSingleFile());
            }
        }

        generateCustomOrgHolder(generatedJavaDir.get().getAsFile(),
            templateFiles.filter(f -> "CustomOrgMap.java".equals(f.getName())).getSingleFile());
    }



    @Nonnull
    @SuppressWarnings("unchecked")
    private Map<String, Object> parseJsonFile()
    {
        final Object result;
        try {
            result = new JsonSlurper().parse(jsonFile.get().getAsFile());
        }
        catch (RuntimeException e) {
            throw new GradleException("Failed to parse JSON file: " + jsonFile.get(), e);
        }
        if (!(result instanceof Map)) {
            throw new GradleException("Failed to parse JSON file, result is not a Map: " + jsonFile.get());
        }
        return (Map<String, Object>) result;
    }



    @Nonnull
    @SuppressWarnings("unchecked")
    private Map<String, Object> selectMap(@Nonnull final Map<String, Object> pFullJson, @Nonnull final String pMapName)
    {
        Object inner = pFullJson.get(pMapName);
        if (!(inner instanceof Map)) {
            throw new GradleException(pMapName + " is missing from " + jsonFile.get().getAsFile().getName());
        }
        return (Map<String, Object>) inner;
    }



    @SuppressWarnings("ResultOfMethodCallIgnored")
    private File getOutputFilename(@Nonnull final String pMapName, @Nonnull final File pOutputDir,
        @Nonnull final File pTemplateJavaFile)
    {
        String name = isCustomMap(pMapName)
            ? ("CustomOrg" + Character.toUpperCase(pMapName.charAt(0)) + pMapName.substring(1) + "Map.java")
            : pTemplateJavaFile.getName();
        File result = new File(new File(pOutputDir, "org/licenselynx"), name);
        result.getParentFile().mkdirs();
        return result;
    }



    private boolean isCustomMap(@Nonnull final String pMapName)
    {
        return !"stableMap".equals(pMapName) && !"riskyMap".equals(pMapName);
    }



    private void generateMapClass(@Nonnull final String pMapName, @Nonnull final Map<String, Object> pInnerMap,
        @Nonnull final File pOutputDir, @Nonnull final File pTemplateJavaFile)
    {
        String templateContent = readTemplate(pTemplateJavaFile);
        templateContent = templateContent.replaceAll("CustomOrgXxxMap",
            "CustomOrg" + Character.toUpperCase(pMapName.charAt(0)) + pMapName.substring(1) + "Map");

        int markerIndex = templateContent.indexOf(INSERTION_MARKER);
        if (markerIndex < 0) {
            throw new GradleException("Marker not found in template: " + pTemplateJavaFile);
        }
        int classClosingIndex = templateContent.lastIndexOf('}');
        if (classClosingIndex < 0 || classClosingIndex <= markerIndex) {
            throw new GradleException("Class closing brace not found in template: " + pTemplateJavaFile);
        }
        final int markerLineStart = templateContent.lastIndexOf('\n', markerIndex) + 1;
        final String markerIndent = templateContent.substring(markerLineStart, markerIndex);
        String firstHalf = templateContent.substring(0, markerLineStart);
        String secondHalf = templateContent.substring(markerIndex + INSERTION_MARKER.length(), classClosingIndex);
        String classClosing = templateContent.substring(classClosingIndex);

        final List<String> sortedKeys = getSortedKeys(pInnerMap);
        final int batchCount = getBatchCount(sortedKeys);

        final File outputFile = getOutputFilename(pMapName, pOutputDir, pTemplateJavaFile);
        try {
            writeOutputFile(outputFile, writer -> {
                writer.print(firstHalf);
                printAddEntriesCalls(batchCount, markerIndent, writer);
                writer.print(secondHalf);
                printAddEntriesMethods(pInnerMap, sortedKeys, writer);
                writer.print(classClosing);
            });
        }
        catch (LynxMappingException e) {
            throw new GradleException(
                "Internal error: null value in " + pMapName + " of " + jsonFile.get().getAsFile().getName());
        }
    }



    private void generateCustomOrgHolder(@Nonnull final File pOutputDir, @Nonnull final File pTemplateJavaFile)
    {
        final String templateContent = readTemplate(pTemplateJavaFile);
        final String generatedContent = CUSTOM_ORG_PATTERN.matcher(templateContent)
            .replaceAll("m.put(Organization.$1, CustomOrg$1Map.getLicenseMap());");
        if (generatedContent.equals(templateContent)) {
            throw new GradleException("Failed to apply custom org substitutions to template: " + pTemplateJavaFile);
        }

        final File outputFile = new File(new File(pOutputDir, "org/licenselynx"), pTemplateJavaFile.getName());
        //noinspection ResultOfMethodCallIgnored
        outputFile.getParentFile().mkdirs();

        try {
            writeOutputFile(outputFile, writer -> writer.print(generatedContent));
        }
        catch (LynxMappingException e) {
            throw new GradleException("Internal error: null value in data");
        }
    }



    @Nonnull
    private String readTemplate(@Nonnull final File pTemplateJavaFile)
    {
        final String result;
        try {
            byte[] bytes = Files.readAllBytes(pTemplateJavaFile.toPath());
            result = new String(bytes, StandardCharsets.UTF_8);
        }
        catch (IOException e) {
            throw new GradleException("Failed to read template file: " + pTemplateJavaFile, e);
        }
        return result;
    }



    @Nonnull
    private List<String> getSortedKeys(@Nonnull final Map<String, Object> pInnerMap)
    {
        return pInnerMap.keySet().stream()
            .map(Objects::toString)
            .sorted()
            .collect(Collectors.toList());
    }



    private int getBatchCount(@Nonnull final List<String> pSortedKeys)
    {
        return (pSortedKeys.size() + MAP_INIT_BATCH_SIZE - 1) / MAP_INIT_BATCH_SIZE;
    }



    private void printAddEntriesCalls(final int pBatchCount, @Nonnull final String pIndent,
        @Nonnull final PrintWriter pWriter)
    {
        for (int i = 0; i < pBatchCount; ++i) {
            pWriter.println(String.format("%saddEntries%02d(m);", pIndent, i));
        }
    }



    private void printAddEntriesMethods(@Nonnull final Map<String, Object> pInnerMap,
        @Nonnull final List<String> pSortedKeys, @Nonnull final PrintWriter pWriter)
        throws LynxMappingException
    {
        final int batchCount = getBatchCount(pSortedKeys);

        for (int i = 0; i < batchCount; ++i) {
            final int fromIndex = i * MAP_INIT_BATCH_SIZE;
            final int toIndex = Math.min(fromIndex + MAP_INIT_BATCH_SIZE, pSortedKeys.size());

            pWriter.println("\n\n");
            pWriter.println(String.format(
                "    private static void addEntries%02d(final Map<String, LicenseObject> pMap)", i));
            pWriter.println("    {");
            printPutStatements(pInnerMap, pSortedKeys.subList(fromIndex, toIndex), pWriter);
            pWriter.println("    }");
        }
    }



    private void printPutStatements(@Nonnull final Map<String, Object> pInnerMap,
        @Nonnull final List<String> pSortedKeys, @Nonnull final PrintWriter pWriter)
        throws LynxMappingException
    {
        for (String foundStr : pSortedKeys) {
            Object targetObject = pInnerMap.get(foundStr);

            String targetId = null;
            String targetSrc = null;

            if (targetObject instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<Object, Object> targetMap = (Map<Object, Object>) targetObject;
                targetId = Objects.requireNonNull(targetMap.get("id"), "id is null in " + foundStr).toString();
                targetSrc = Objects.requireNonNull(targetMap.get("src"), "src is null in " + foundStr).toString();
            }
            else {
                throw new GradleException(foundStr + " refers to invalid data");
            }

            final String dataSourceCode = buildDataSourceCode(targetSrc);

            pWriter.println(
                "        " + "pMap.put(\"" + escapeJava(foundStr) + "\", "
                    + "new LicenseObject(\"" + escapeJava(targetId) + "\", "
                    + dataSourceCode + "));"
            );
        }
    }



    private String buildDataSourceCode(@Nonnull final String pTargetSrc)
        throws LynxMappingException
    {
        final String result;
        if ("spdx".equals(pTargetSrc)) {
            result = "LicenseSource.Spdx";
        }
        else if ("scancode-licensedb".equals(pTargetSrc)) {
            result = "LicenseSource.ScancodeLicensedb";
        }
        else {
            result = "CanonicalSourceDeserializer.fromValue(\"" + escapeJava(pTargetSrc) + "\")";
        }
        return result;
    }



    private void writeOutputFile(@Nonnull final File pOutputFile, LynxWriter pWritingFunc)
        throws LynxMappingException
    {
        try (
            FileOutputStream fos = new FileOutputStream(pOutputFile);
            BufferedOutputStream bos = new BufferedOutputStream(fos);
            OutputStreamWriter osw = new OutputStreamWriter(bos, StandardCharsets.UTF_8);
            PrintWriter writer = new PrintWriter(osw))
        {
            pWritingFunc.accept(writer);
        }
        catch (IOException e) {
            throw new GradleException("Failed to write output file: " + pOutputFile, e);
        }
    }



    private String escapeJava(String value)
        throws LynxMappingException
    {
        if (value == null) {
            throw new LynxMappingException();
        }
        return value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }



    @Nonnull
    @InputFile
    @PathSensitive(PathSensitivity.RELATIVE)
    public RegularFileProperty getJsonFile()
    {
        return jsonFile;
    }



    @Nonnull
    @InputFiles
    @PathSensitive(PathSensitivity.RELATIVE)
    public ConfigurableFileCollection getTemplateFiles()
    {
        return templateFiles;
    }



    @Nonnull
    @OutputDirectory
    public DirectoryProperty getGeneratedJavaDir()
    {
        return generatedJavaDir;
    }
}
