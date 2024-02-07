#!/bin/bash

flask init-db
flask populate-db
flask run --debug -host=0.0.0.0