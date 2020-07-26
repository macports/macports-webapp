import io
import subprocess

from port.models import Port


def populate_variant_descriptions_all_ports():
    for port in Port.objects.all().only('id', 'name'):
        poulate_variant_descriptions(port)
    return


def populate_variant_descriptions_ports(ports):
    for port in ports:
        poulate_variant_descriptions(port)
    return


def poulate_variant_descriptions(port):
    try:
        output = subprocess.run(["port", "variants", port.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = output.stdout.decode('utf-8')
    except OSError:
        return

    result_lines = io.StringIO(result)
    cached_variants = port.variants.all()
    for line in result_lines:
        line = line.strip()
        for variant in cached_variants:
            search_string = "{}:".format(variant.variant)

            if line.startswith("[+]{}".format(search_string)):
                variant.description = "[default] {}".format(line[len(search_string) + 4:])
                variant.save()
                break

            if line.startswith(search_string):
                variant.description = line[len(search_string)+1:]
                variant.save()
                break
