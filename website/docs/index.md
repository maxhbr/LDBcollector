<div class="hero-section">
  <img src="assets/background.png" alt="LicenseLynx Hero Banner" class="hero-background">
  <div class="hero-content">
    <h1>LicenseLynx</h1>
    <a href="https://github.com/licenselynx/licenselynx" class="hero-button">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>
      Source Code
    </a>
  </div>
</div>

<div align="center"><img src="assets/licenselynx-simple-explanation-light.png#only-light" alt="LicenseLynx Workflow Explanation"></div>
<div align="center"><img src="assets/licenselynx-simple-explanation-dark.png#only-dark" alt="LicenseLynx Workflow Explanation"></div>

## Main features

<div class="grid cards" markdown>

- __Deterministic__

    Same Input → Same ID

- __10,000+ Mappings__
  
    Aliases + Variants

- __Libraries__
  
    Python • Java • TypeScript

- __Open data__
  
    GitHub, versioned

- __Frequent Updates__
  
    Auto-synced with SPDX & ScanCode

- __Free and Open-Source__
  
    Licensed under BSD-3-Clause
</div>

How can we map a license string found in the wild automatically and deterministically?
[**LicenseLynx**](https://github.com/licenselynx/licenselynx) is the answer to that!


We collect and match license strings found from SPDX, ScanCode LicenseDB, and OSI License List to its canonical identifier.
But this is just the starting point.
The most valuable data comes from the community with custom aliases for license identifiers which are not present in the license databases or license lists.



<!--
In today's software development landscape, managing licenses across various projects can be a daunting task.
Different projects often refer to the same license in multiple ways, leading to confusion and potential legal risks.  
LicenseLynx aims to solve this problem by bridging the gap between unknown or ambiguous license names and their canonical license names.
Additionally, we offer libraries for Python, Java, and TypeScript to streamline the process of mapping licenses to their canonical names,  
typically represented by SPDX IDs.
-->
## Getting started

For more information, head to the [FAQ](faq.md) and [How LicenseLynx works](licenselynxworks.md).  
Follow the page [Installation](installation.md) to install LicenseLynx and follow the page [Usage](usage.md) on how to use LicenseLynx in your projects.

## Key Features

- **Community-driven approach**: Custom mappings from the community enhance LicenseLynx to map more license aliases to its canonical identifiers
- **Aggregated data**: Collects license information and aliases from the license list of SPDX, ScanCode LicenseDB, and OSI into a single repository
- **SPDX Compliance**: Maps licenses to their canonical names using SPDX IDs if possible
- **Multi-Language Support**: Offers libraries in Python, Java, and TypeScript to use it with your projects

## Contributing

Want to help out?  
Check out the [Contributing](contribution.md) page for detailed information.
