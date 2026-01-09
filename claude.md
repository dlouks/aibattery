# Claude Code Guidelines

## Dependencies

When adding a new dependency to this project:

1. **Document installation requirements in README.md** - Any new dependency that requires local system setup or installation steps must be clearly documented in the README.md file.

2. **Include the following for each new dependency:**
   - What the dependency is and why it's needed
   - System-level prerequisites (e.g., native libraries, system packages)
   - Installation commands for different platforms (macOS, Linux, Windows) if applicable
   - Any environment variables or configuration required

3. **Example format for README.md:**
   ```markdown
   ## Prerequisites

   - Node.js >= 18.x
   - [New Dependency Name]: Install via `brew install <package>` (macOS) or `apt install <package>` (Linux)
   ```

This ensures that anyone cloning the repository can get the project running without hunting for undocumented setup steps.
