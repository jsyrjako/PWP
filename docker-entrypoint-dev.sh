#!/bin/bash

flask init-db
flask populate-db
flask --app bikinghub run --debug -host=0.0.0.0