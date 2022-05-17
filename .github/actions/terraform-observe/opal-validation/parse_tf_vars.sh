#!/bin/bash

input="$(cat "$1")"

spaceless="${input//[$'\t\r\n ']/}"

var_configs=''

IFS=' ' read -r -a var_array <<< "${spaceless//'variable"'/ }"
for variable in "${var_array[@]}"
do 
	var_name="${variable%%\"*}"
	if [[ "$variable" == *"type=bool"* ]]; then
		if [[ "$variable" == *"default=true"* ]]; then
			var_configs="""${var_configs}
  ${var_name} = false"""
		elif [[ "$variable" == *"default=false"* ]]; then
			var_configs="${var_configs}
  ${var_name} = true"
		elif [[ "$variable" == *"default=null"* ]]; then
			var_configs="${var_configs}
  ${var_name} = true"
		fi
	fi
done

perl -pe "s/%%CUSTOM_VARIABLES%%/${var_configs}/g" main.tf.original > main.tf
