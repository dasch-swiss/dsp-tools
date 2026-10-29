[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# The Project Admin Account for Production

Each project on a production server has one project admin account for data uploads.
DaSCH uses the project admin account for all work on the data of the project on production.


## Account Scheme

- Email: `<shortname>@admin.dasch.swiss`, where `<shortname>` is the
  [`shortname`](./data-model/json-project/overview.md#shortname) of the project.
- Role: project admin of the project.

DSP-APP shows the project admin account as the creator of the uploaded data.
If you make your own data model, agree on the username, given name and family name with DaSCH.


## Who Creates the Account

The person who sets up the data model also creates the account:

- If the DaSCH Research Data Unit (RDU) sets up the project, RDU creates the account and owns it.
- If you make your own data model, you create the account.

In both cases, add the account to the
[`users`](./data-model/json-project/overview.md#users) section of the JSON project file.
[`dsp-tools create`](./data-model/data-model-cli.md#create) then creates the account together with the project.
The account needs `":admin"` and `":member"` in its `projects`.
If you use [`excel2json`](./data-model/excel2json.md#the-json_headerxlsx), add the account to the "Users" sheet
with the role `projectadmin`.

On the prod-like servers `api.dasch.swiss`, `api.rdu.dasch.swiss` and `api.stage.dasch.swiss`,
`create` stops if the JSON project file has no such account.
`create` stops as well if the account has no admin rights in its `projects`.
On all other servers, `create` only shows a warning.
`create --validate-only` runs the same check, if `-s` is set to the target server.

If the project exists already, `create` still needs the account in the JSON project file.
If the account exists in DSP-APP already, write its `username` and `email` exactly as they are in DSP-APP.

Example of the account in the JSON project file:

```json
{
  "users": [
    {
      "username": "<agreed username>",
      "email": "<shortname>@admin.dasch.swiss",
      "givenName": "<agreed given name>",
      "familyName": "<agreed family name>",
      "password": "<password>",
      "lang": "en",
      "projects": [
        ":admin",
        ":member"
      ],
      "status": true
    }
  ]
}
```


## Use on Production

On production, a DaSCH system admin runs `create`, because `create` needs the credentials of a system admin.
After `create`, DaSCH uses the project admin account for these commands:

- [`xmlupload`](./data-file/data-file-commands.md#xmlupload)
- [`resume-xmlupload`](./data-file/data-file-commands.md#resume-xmlupload)
- [`upload-files`](./special-workflows/workflow-xmlupload.md#upload-files)
- [`ingest-files`](./special-workflows/workflow-xmlupload.md#ingest-files)
- [`ingest-xmlupload`](./special-workflows/workflow-xmlupload.md#ingest-xmlupload)
- [`mapping update`](./data-model/data-model-cli.md#mapping-update).


## Authorship of the Data

DSP-APP shows the project admin account as the creator of the data.
The creator is only the account that uploaded the data.
It does not show who made the data.
Because DaSCH uploads all data of the project with the same account,
the creator is the same for all resources.

The author is the person or the institution that made the content, for example
the researcher who transcribed a letter or the photographer of an image.
DSP does not get the authors from the account.
If the XML file gives no authorship, the data has no author in DSP.
Then the users of the data cannot see whom to give credit to, and cannot cite the authors correctly.
The project default `default_data_authorship` does not change this on its own:
`xmlupload` applies it only if the XML file tells it to.

Give the authorship, the copyright holder and the license in the legal metadata of the XML file:

- Multimedia assets: the attributes `authorship-id`, `copyright-holder` and `license`
  on [`<bitstream>`](./data-file/xml-data-file.md#bitstream) and [`<iiif-uri>`](./data-file/xml-data-file.md#iiif-uri).
- Resources: the attribute
  [`authorship-id`](./data-file/xml-data-file.md#resource-authorship-authorship-id-on-the-resource)
  on the `<resource>` element.
- Definitions of the authors: [`<authorship>`](./data-file/xml-data-file.md#defining-the-authorships).
- Project defaults: [`default_data_authorship`](./data-model/json-project/overview.md#default_data_authorship).
  The attribute [`use-project-default-resource-authorship`](./data-file/xml-data-file.md#the-root-element-knora)
  on the `<knora>` element applies the project default to all resources without their own `authorship-id`.

If you use the `xmllib`, see [Setting the Authorship of a Resource](./xmllib-docs/overview.md#setting-the-authorship-of-a-resource).
