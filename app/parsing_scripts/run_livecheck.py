import io
import subprocess

from port.models import Port, LiveCheck


def run_livecheck_all():
    for port in Port.objects.all().only('id', 'name'):
        try:
            output = subprocess.run(["port", "livecheck", port.name], stdout=subprocess.PIPE).stdout.decode('utf-8')
        except OSError:
            continue
        obj, created = LiveCheck.objects.get_or_create(port_id=port.id)
        obj.result = None
        lines = io.StringIO(output)
        for line in lines:
            if "seems to have been updated" in line:
                obj.result = line
        obj.save()
    return


def run_livecheck_port(name):
    try:
        port = Port.objects.get(name=name)
    except Port.DoesNotExist:
        return
    try:
        output = subprocess.run(["port", "livecheck", port.name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    except OSError:
        return
    lines = io.StringIO(output)
    obj, created = LiveCheck.objects.get_or_create(port_id=port.id)
    obj.result = None
    for line in lines:
        if "seems to have been updated" in line:
            obj.result = line
    obj.save()
    return
