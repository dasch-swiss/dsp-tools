# Names that vulture reports for this package alone, but that are used by dsp-tools or by Protocol implementations.
from typing import Any

_: Any = None

# Protocol attributes: declared in a Protocol, set by the live client or read by dsp-tools.
_.children
_.details
_.error_code
_.error_message
_.internal_filename
_.listinfo
_.status

# Live client classes: instantiated by dsp-tools only.
_.AuthenticationClientLive
_.DataImportClientLive
_.ListCreateClientLive
_.ListGetClientLive
_.MigrationExportClientLive
_.MigrationImportClientLive
_.OntologyCreateClientLive
_.ProjectClientLive
_.ResourceClientLive
_.ValueClientLive

# Client methods: declared in a Protocol, implemented by a live client, called by dsp-tools only.
_.add_list_node
_.add_user_as_project_admin
_.add_user_as_project_member
_.add_user_to_custom_groups
_.create_new_doap
_.create_new_group
_.create_new_list
_.delete_class_mapping
_.delete_doap
_.delete_export
_.delete_import
_.delete_property_mapping
_.get_all_groups
_.get_all_list_iris_and_names
_.get_all_lists_and_nodes
_.get_all_users
_.get_default_data_authorship
_.get_download
_.get_knora_api
_.get_last_modification_date
_.get_licenses_of_a_project
_.get_ontologies
_.get_project_doaps
_.get_project_iri
_.get_resource
_.get_resource_metadata
_.get_status
_.ingest
_.post_copyright_holders
_.post_export
_.post_import
_.post_new_class
_.post_new_ontology
_.post_new_project
_.post_new_property
_.post_new_user
_.post_new_value
_.post_resource
_.post_resource_cardinalities
_.put_class_mapping
_.put_property_mapping
_.replace_existing_value
_.retrieve_mapping_generator
_.set_resource_side_legal_info
_.trigger_ingest_process
_.upload_file
