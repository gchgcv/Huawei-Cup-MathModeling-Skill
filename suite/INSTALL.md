# Suite Installation Contract

## Install Model

Install the complete `Huawei Cup Modeling Skills Suite`. Do not install only
`skills/huawei-cup-writing/` or `skills/huawei-cup-review/`, because both consume the
authoritative `shared/` tree through package-relative paths.

After Suite installation, Writing, Review, and the compatibility router may be enabled
or disabled independently. Disabling a component does not permit deleting or copying
Shared rules into another component.

## Authoritative Dependencies

- Shared Paper Quality Standard: `shared/paper-quality-standard`, version `1.0`.
- Project Facts Contract: `shared/contracts/project-facts.schema.json`, version `1`.
- Review Finding Contract: `shared/contracts/review-finding.schema.json`, version `1`.
- Paper Artifact Contract: `shared/contracts/paper-artifact-contract.md`, version `1`.

Run `python suite/validate_suite.py` after installation. Missing Shared files, paths that
escape the Suite root, component-version drift, or incompatible Shared versions return
`BLOCKED`. The validator never falls back to copied or Legacy rules.

The compatibility router is optional and disabled by default. Enable it only when the
old `huawei-cup-modeling` entry name must route paper/audit requests to the modular
components.
