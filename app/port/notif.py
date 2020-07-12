from datetime import datetime, timezone


def generate_notifications_verb(old, new):
    expr = ""

    if old['version'] != new.version:
        expr += "Version updated from '{}' to '{}'".format(old['version'], new.version)

        # update the version_updated_at field
        new.version_updated_at = datetime.now(timezone.utc)
        new.save()

    if old['license'] != new.license:
        expr += " License changed from {} to {}.".format(old['license'], new.license)

    if old['replaced_by'] != new.replaced_by:
        expr += " Port became obsolete."

    return expr
