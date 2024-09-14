version_gte() {
    # $1: Current version
    # $2: Expected version
    # Returns 0 if current version is greater than or equal to the expected version
    [ "${2}" = "$(printf "%b\n" "${1}" "${2}" | sort -V | head -n1)" ]
}

command_exists() {
    # $1: The name of a command to check the presence of
    if ! command -v "${1}" &> /dev/null
	  then
	      echo "Command '${1}' not found"
	      exit 1
	  fi
}

$*