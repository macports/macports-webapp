import io
import subprocess

from port.models import Port


def get_notes_all_ports():
    # Limiting the fields that are selected
    # This ensures that the updated_at field does not get updated
    # Because changes to a port's notes are not considered as an update
    for port in Port.objects.all().only('name', 'notes'):
        get_notes(port)
    return


def get_notes(port):
    try:
        output = subprocess.run(["port", "notes", port.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = output.stdout.decode('utf-8')
    except OSError:
        return

    result_lines = io.StringIO(result)

    # maintain linebreaks in the field that is saved to database using
    port.notes = "<br>".join(result_lines)
    port.save()
