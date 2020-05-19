import io
import subprocess

from port.models import Port, LiveCheck


def run_livecheck_all():
    for port in Port.objects.all().only('id', 'name'):
        run_livecheck_port(port)
    return


def run_livecheck_port(port):
    try:
        output = subprocess.run(["port", "livecheck", port.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = output.stdout.decode('utf-8')
        error = output.stderr.decode('utf-8')
    except OSError:
        return
    result_lines = io.StringIO(result)
    error_lines = io.StringIO(error)

    # Get or create the Livecheck object and initialise values
    obj, created = LiveCheck.objects.get_or_create(port_id=port.id)
    obj.result = None
    obj.error = None
    obj.has_updates = False

    for line in result_lines:
        if line.startswith(port.name + " seems to"):
            obj.result = line
            obj.has_updates = True

    for line in error_lines:
        if line.startswith("Error:"):
            obj.error = line
    obj.save()
    return
