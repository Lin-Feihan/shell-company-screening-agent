# Default Settings

This document defines the default settings for a shell company screening task, which can be customized for each client mandate.

## Settings

| Field ID | Setting | Type | Required Input | Default | Description |
|---|---|---|---|---|---|
| `client_name` | Client Name | Text | Yes | — | Name of the client or organization commissioning the shell company screening task. |
| `target_market` | Target Listed Market | Text | Yes | — | Listed market or jurisdiction in which shell company candidates should be identified. |
| `research_cutoff_date` | Research Cut-off Date | Date | No | Run date | Latest date up to which information should be considered. An explicit date can be provided when a fixed research cut-off is required. |
| `control_requirement` | Control Requirement | Long text | No | Not specified | Describes any client requirement regarding ownership, effective control, or the desired control path. |
| `capital_structure_preference` | Capital Structure Preference | Long text | No | Not specified | Describes any client preference regarding convertible bonds, legacy financing instruments, or other capital-structure complexity. |
| `warrant_dilution_preference` | Warrant and Dilution Preference | Long text | No | Not specified | Describes any client preference regarding warrants, options, convertible securities, or other potential dilution. |
| `reporting_compliance_requirement` | Reporting, Legal and Regulatory Requirement | Long text | No | Not specified | Describes any client-specific requirements regarding reporting, audit status, litigation, regulatory matters, suspension risk, or other compliance issues. |
| `historical_financing_preference` | Historical Financing Preference | Long text | No | Not specified | Describes any client preference regarding historical financing arrangements. |
| `market_cap_requirement` | Market Capitalization Requirement | Long text | No | No fixed threshold | Defines any market-capitalization requirement. If no threshold is specified, market capitalization is treated as a reference for transaction scale and economics rather than as a hard filter. |
| `transaction_objective` | Transaction Objective | Long text | No | Not specified | Describes the intended transaction objective and planned use of the listed platform. |
| `additional_requirements` | Additional Client Requirements | Long text | No | — | Any additional transaction constraints, preferences, exclusions, or client-specific requirements not covered above. |
| `additional_context` | Additional Context | Long text | No | — | Optional background information or non-public context that may help the agent interpret the client mandate. |
