# mspipelines docs

## Installation

Install ["quarto"](https://quarto.org/docs/get-started) 

## Module docs
The directory "modules/" was created using : 

```bash
bin/tools/docker/quarto/generate_documentation_qmd/generate_documentation_qmd \
  --input "." \
  --output "docs/modules" \
  --git_repo "czbiohub/mspipelines" \
  --git_tag "main_build" \
  --git_browse_url "https://github.com/czbiohub/mspipelines/blob/main" \
  ---verbose
```
