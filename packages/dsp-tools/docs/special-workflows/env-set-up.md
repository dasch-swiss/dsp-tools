# `.env` Options for `dsp-tools` Workflows

## Passwords in `excel2json` and `create`

To hide user passwords in the JSON the value `null` is allowed.

- `excel2json`: leave the cell for passwords empty
- JSON file example:

```json
{
    "username": "testerProjectAdmin",
    "email": "tester.projectadmin@test.org",
    "givenName": "Tester",
    "familyName": "Project Admin",
    "password": null,
    "lang": "de",
    "projects": [
        ":admin"
    ],
    "status": true
}
```

However, during the `create` command a password is required. 
To set a global default password for all users that do not have a password specified,
add the variable `DSP_USER_PASSWORD` to an `.env` file in your root directory. 
If you want to use it in GitHub workflows, add it to your repository secrets and enter in in the workflow yaml.
