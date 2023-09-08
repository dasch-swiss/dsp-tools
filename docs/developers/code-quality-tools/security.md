[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Security Checks

## [Bandit](https://pypi.org/project/bandit/)

Finds common security issues in Python code.
For every single file, Bandit builds an AST, and runs plugins (i.e. tests) against the AST nodes.
Bandit supports many plugins (i.e. tests) to detect various security issues. 

## [Dependabot](https://docs.github.com/en/code-security/dependabot)

GitHub's built-in feature to keep the supply chain secure.
Dependabot monitors vulnerabilities in dependencies used in a project 
and keep the dependencies up-to-date.

## [CodeQL](https://codeql.github.com/)

Semantic code analysis engine by GitHub.
CodeQL lets you query code as though it were data. 
Write a query to find all variants of a vulnerability, eradicating it forever. 
Then share your query to help others do the same. 
CodeQL is free for research and open source,
and can be activated in the GitHub settings of a repository.

## [Gitleaks](https://gitleaks.io/)

Secret scanner for git repositories, available as GitHub action.

## [Pysa](https://pyre-check.org/docs/pysa-basics/)

Pysa is a feature of Facebook's type checker Pyre.
It performs taint analysis to identify potential security issues.
Tainted data is data that must be treated carefully. 
Pysa works by tracking flows of data from where they originate (sources) 
to where they terminate in a dangerous location (sinks). 
Example: User-controllable data that flows into an eval call 
leads to a remote code execution vulnerability. 
