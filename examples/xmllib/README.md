# Guide To Try Out the New Concept of XML Helper Functions

## Installation

**Install Demo Version Of dsp-tools**

```
pip3 uninstall dsp-tools
```

```
pip3 install git+https://github.com/dasch-swiss/dsp-tools.git@wip/rdu-14-replace-linebreak-with-tag
```


## Ontology Specifics

**Classes:**
- `:Dog`

**Properties:**
- `:hasName` -> SimpleText (1-n)
- `:hasStreetAdress` -> RichText (1)

Optional:
- Image or IIIF-URI


## Finishing Up

**Re-Install dsp-tools**

```
pip3 uninstall dsp-tools
```

```
pip3 install dsp-tools
```