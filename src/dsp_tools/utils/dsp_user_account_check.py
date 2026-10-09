def is_correct_dsp_admin_account_email(shortname: str, email: str) -> bool:
    expected = f"{shortname}@admin.dasch.swiss"
    return email == expected
