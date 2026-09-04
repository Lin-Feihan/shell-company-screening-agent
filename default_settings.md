# Default Settings

This document defines the task-level inputs and reusable default settings for the Deep Research Agent for Shell Company Screening.

These settings describe the client mandate and transaction requirements for a specific research run.

## Settings

| Field ID | Setting | Type | Required Input | Default | Description |
|---|---|---|---|---|---|
| `client_name` | Client Name | Text | Yes | — | Name of the client or organization commissioning the shell company screening task. |
| `target_market` | Target Listed Market | Text | Yes | — | Listed market or jurisdiction in which shell company candidates should be identified. |
| `research_cutoff_date` | Research Cut-off Date | Date | No | Run date | Latest date up to which information should be considered. An explicit date should be provided when reproducibility is required. |
| `spac_included` | SPAC Included | Boolean | No | False | Determines whether SPACs are included as potential listed-platform candidates. |
| `de_spac_included` | De-SPAC Included | Boolean | No | False | Determines whether De-SPAC transactions are included as an eligible transaction structure. |
| `control_requirement` | Control Requirement | Long text | No | Relatively high level of effective control preferred | Describes the client's desired level of ownership or effective control and any relevant flexibility in the control path. |
| `capital_structure_preference` | Capital Structure Preference | Long text | No | Relatively clean capital structure preferred | Describes preferences regarding convertible bonds, legacy financing instruments, or other capital-structure complexity. |
| `warrant_dilution_preference` | Warrant and Dilution Preference | Long text | No | Clear and manageable dilution structure preferred | Describes acceptable warrant, option, convertible-security, or other potential dilution structures. |
| `reporting_compliance_requirement` | Reporting, Legal and Regulatory Requirement | Long text | No | Current reporting and no material unresolved legal or regulatory issues | Defines expectations regarding financial reporting, audit status, litigation, regulatory investigations, suspension risk, and other compliance matters. |
| `historical_financing_preference` | Historical Financing Preference | Long text | No | Relatively clean financing history preferred | Describes preferences regarding historical financing, including highly dilutive or otherwise problematic financing arrangements. |
| `market_cap_requirement` | Market Capitalization Requirement | Long text | No | No fixed threshold | Defines any market-capitalization requirement. By default, market capitalization is used as a reference for transaction scale and economics rather than as a hard exclusion criterion. |
| `post_acquisition_plan` | Post-Acquisition Plan | Long text | No | Control acquisition followed by restructuring and potential asset injection | Describes the intended use of the listed platform after control acquisition. |
| `additional_requirements` | Additional Client Requirements | Long text | No | — | Any additional transaction constraints, preferences, exclusions, or client-specific requirements not covered by the standard settings above. |
