# Knora Library

This library offers classes and methods to manipulate a Knora based repository.
Most important it allow importing data by providing a methods to create new resources.

## Classes

### Knora

#### Knora()  
Creates an access object for Knora.  
```Knora(server, prefixes: Dict[str, str] = None)```  
- server: URL of the Knora API server
- prefixes: List of extra RDF-prefixes that are being used
- Example: ```con = Knora(args.server)```

#### login()  
This method performs a login and stored the access token. 
```login(email: str, password: str)```  
- email: Emailadress of user
- password: Password of user
- Example: ```con.login(args.user, args.password)```

#### logout()  
This method is used to logout from Knora and remove the access token.  
```logout()```
- Example: ```con.logout()```

#### get_existing_projects()  
Returns a list of all projects. Usually returns only the IRI's. If full ist true, returns all information.  
```get_existing_projects(full: bool = False)```  

#### get_project()  
Returns information about a project given its shortcode.  
```get_project(shortcode: str) -> dict```  

#### project_exists()  
Returns true if a project given by thee shortcode is existing.  
```project_exists(self, proj_iri: str) -> bool```  

#### create_project() 
This method is used to create a new project  
```python
create_project(
  shortcode: str,
  shortname: str,
  longname: str,
  descriptions: Optional[Dict[str, str]] = None,
  keywords: Optional[List[str]] = None,
  logo: Optional[str] = None) -> str
```
- shortcode: The Knora shortcode of the project
- shortname: The short name of the project
- longname: The long name of the project
- descriptions: [optional] Dict with the language short (e.g. "en", "de"...) as key
- keywords: [optional] List of keywords
- logo: [optional] Path to logo file


#### update_project()
This method is used to modify existing project data. All parameters except the shortcode (which cannot be changed)
are optional.  
```
update_project(
  shortcode: str,
  shortname: str,
  longname: str,
  descriptions: Optional[Dict[str, str]] = None,
  keywords: Optional[List[str]] = None,
  logo: Optional[str] = None) -> str
```
- shortcode: The Knora shortcode of the project
- shortname: The short name of the project
- longname: The long name of the project
- descriptions: Dict with the language short (e.g. "en", "de"...) as key
- keywords: List of keywords
- logo: Path to logo file
  
#### get_users()
Get all users  

#### get_user()
Get information about a specific user  
```get_user(user_iri: str)```
- user_iri: Knora IRI identifying the user

#### create_user()
Create a new user and returns it's new IRI.  
```
create_user(
  username: str,
  email: str,
  givenName: str,
  familyName: str,
  password: str,
  lang: str = "en")
```
- username: Username (shortname)
- email: Email address of user – is used to identify the user
- givenName: First name of the user
- familyName: Family name of the user
- password: Password
- lang: [optional] Language string of default language

#### add_user_to_project()
Add an existing user to a project.  
```
add_user_to_project(
  user_iri: str,
  project_iri: str)
```
- user_iri: IRI of the user
- project_iri: IRI of the project

#### get_existing_ontologies()
Get short information about all ontologies existing.  
```
get_existing_ontologies()
```

#### get_project_ontologies()
Returns the ontologiees of a given project.  
```
get_project_ontologies(
project_code: str) -> Optional[dict]
```
- project_code: Shortcode of project

#### ontology_exists()
Test, if an ontology exists.  
```
ontology_exists(onto_iri: str)
```
- onto_iri: IRI of the ontology

#### get_ontology_lastmoddate()
Get the last modification date of a given ontology.  
```
get_ontology_lastmoddate(self, onto_iri: str)
```
- onto_iri: IRI of the ontology

#### create_ontology()
Create a new ontology.  
```
create_ontology(
  onto_name: str,
  project_iri: str,
  label: str
) -> Dict[str, str]
```
- onto_name: Name of the ontology
- project_iri: IRI of the project the ontology belongs to
- returns: Dict with "onto_iri" and "last_onto_date"

#### delete_ontology()
Deletes the given ontology.  
```
delete_ontology(
  onto_iri: str
  last_onto_date = None)
```
- onto_iri: IRO of the ontology
- last_onto_date: Timestamp of last modfication of ontology. It cannot
be deleted if the given date is earlier than the actual last modification
date of the ontology.

#### get_ontology_graph()
Get the whole ontology as RDF (text/turtle).  
```
get_ontology_graph(
  shortcode: str,
  name: str)
```
- shortcode: Shortcode of the project
- name: Name of the ontology

#### create_res_class()
Create a new resource class.  


