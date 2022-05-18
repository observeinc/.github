#!/usr/bin/env bash
set -o errexit
set -o pipefail

ERROR() { echo "::error::$*"; }
INFO() { echo "::info::$*"; }
DEBUG() { test -z "$VERBOSE" || echo "::debug::$*"; }

if [[ -z $OBSERVE_CUSTOMER || -z $OBSERVE_DOMAIN || -z $OBSERVE_USER_EMAIL || -z $OBSERVE_USER_PASSWORD ]]; then
  ERROR 'one or more OBSERVE_ environment variables are undefined'
  exit 1
fi

REPO_DIRECTORY="${GITHUB_WORKSPACE:-$PWD}"

if [[ $# -lt 1 ]]; then ERROR "usage error"; fi # Requires 1+ arguments
DIR="$1"
shift

CMD="terraform -chdir=${REPO_DIRECTORY}/${DIR}"

cleanup() {
    if [ "$1" != "0" ]; then
        ERROR "encountered an error, running terraform destroy for cleanup"
        ERROR "exit code $1 occurred on line $2"
    fi
    ${CMD} destroy -auto-approve -input=false
}

${CMD} init
trap 'cleanup $? $LINENO' EXIT
${CMD} apply -auto-approve -input=false
