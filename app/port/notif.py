def generate_notifications_verb(old, new):
    expr = ""

    if old['version'] != new.version:
        expr += "Version updated from '{}' to '{}'".format(old['version'], new.version)

    if old['license'] != new.license:
        expr += " License changed from {} to {}.".format(old['license'], new.license)

    if old['replaced_by'] != new.replaced_by:
        expr += " Port became obsolete."

    return expr
