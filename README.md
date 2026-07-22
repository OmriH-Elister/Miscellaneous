# Miscellaneous

A collection of Windows administration utilities, networking experiments, and
historical learning exercises.

The repository is organized by maintenance status so visitors can distinguish
supported utilities from experimental and archived work.

## Structure

### [active/](active/)

Utilities that are currently presented as usable:

- [EventEntriesDeleter.ps1](active/EventEntriesDeleter.ps1) — removes selected
  Windows Event Log entries.
- [Temporary file cleaner.xml](active/Temporary%20file%20cleaner.xml) — a
  Windows Task Scheduler definition for routine temporary-file cleanup and
  maintenance.

Review every command and adapt paths and privileges to your environment before
running these utilities.

### [experiments/](experiments/)

Proofs of concept and exploratory networking tools:

- **CLINAV-EXDRES** — three iterations of a command-line-controlled browser and
  external DNS resolution/relay experiment.
- **apn_brute_usernames.bat** — a small APN-profile username probing experiment.

These files are experimental, unsupported, and may disable important security
protections or behave unexpectedly. Use them only on systems and networks you
own or are explicitly authorized to test.

### [archive/](archive/)

Obsolete learning exercises retained for historical reference, including the
DirEnum and non-working mkdirls scripts. See [archive/README.md](archive/README.md).

## Project status

Files under `active/` remain available as utilities, but this repository is not
distributed as a single application. Files under `experiments/` and
`archive/` should not be treated as production-ready software.

## License

See [LICENSE](LICENSE).
