#!/bin/bash
usage_exit() {
  cat << EOF 1>&2
Usage: $0 [property name] [property ver(option)]
EOF
  exit 1
}

AK_PROP=${1}
if [[ -z "${1}" ]] ; then
  usage_exit
fi

if [ -n "${2}" ]; then
  AK_PROP_VER="--version ${2}"
fi

if test 0 -ne `ls -d props/ctr_*/${AK_PROP} 2> /dev/null |wc -l`; then
  echo "\"$AK_PROP\" is exists"
  exit 1
fi

if [ -e "tmp_$AK_PROP" ]; then
  rm -rf tmp_$AK_PROP
fi
mkdir tmp_$AK_PROP

akamai terraform --section default export-property --tfworkpath tmp_$AK_PROP $AK_PROP_VER $AK_PROP 
if test $? -ne 0; then
  sleep 5
  echo "### Retry"
  akamai terraform --section default export-property --tfworkpath tmp_$AK_PROP $AK_PROP_VER $AK_PROP 
  if test $? -ne 0; then
    rm -rf tmp_$AK_PROP
    echo "### \"$AK_PROP\" is eroor"
    exit 1
  fi
fi
AK_CONTRACT=`grep '"ctr_' tmp_$AK_PROP/variables.tf |cut -d '"' -f2`
AK_GID=`grep '"grp' tmp_$AK_PROP/variables.tf |cut -d '"' -f2`
mkdir -p props/$AK_CONTRACT/$AK_GID
mv tmp_$AK_PROP props/$AK_CONTRACT/$AK_GID/$AK_PROP

echo "---------------------------------------------"
printf "%10s | %s\n" "ContractID" ${AK_CONTRACT}
printf "%10s | %s\n" "GroupID" ${AK_GID}
printf "%10s | %s\n" "Property" ${AK_PROP}
echo "---------------------------------------------"

