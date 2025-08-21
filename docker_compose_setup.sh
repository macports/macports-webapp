#!/bin/bash

set -euo pipefail

# Add ports data
docker compose run -w /code/app webapp python3 manage.py update-portinfo --type=full

# Add builders
docker compose exec db psql -U postgres -d webapp -c "
  INSERT INTO builder (id, name, display_name, natural_name) VALUES
  (1, '10.15_x86_64', '10.15', 'Catalina'),
  (2, '11_x86_64', '11', 'Big Sur'),
  (3, '12_x86_64', '12', 'Monterey')
  ON CONFLICT DO NOTHING;
"

# Fetch build history
docker compose run -d -w /code/app webapp python3 manage.py fetch-build-history

# Run livecheck
docker compose run -d -w /code/app webapp sh -c 'port -d selfupdate && python3 manage.py run-full-livecheck'

# Add a solr schema and generate index
docker compose exec -w /code/app webapp python3 manage.py build_solr_schema \
    --configure-directory=/code/app/data/solr/macports/conf
docker compose exec -w /code/app webapp python3 manage.py build_solr_schema -r RELOAD_CORE
docker compose run -d -w /code/app webapp python3 manage.py rebuild_index --noinput
