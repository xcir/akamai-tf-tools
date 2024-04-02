#!/bin/bash
usage_exit() {
  cat << EOF 1>&2
Usage: $0 [property name] [property ver(option)]
EOF
  exit 1
}
SCRIPT_DIR=$(cd $(dirname $0); pwd)

AK_PROP=${1}
if [[ -z "${1}" ]] ; then
  usage_exit
fi

if [ -n "${2}" ]; then
  AK_PROP_VER="--version ${2}"
fi

TMP_PROP_PATH="${SCRIPT_DIR}/tmp_${AK_PROP}"
if [ -e "${TMP_PROP_PATH}" ]; then
  rm -rf ${TMP_PROP_PATH}
fi
mkdir ${SCRIPT_DIR}/tmp_${AK_PROP}

akamai terraform --section default export-property --tfworkpath ${TMP_PROP_PATH} $AK_PROP_VER $AK_PROP
if test $? -ne 0; then
  sleep 5
  echo "### Retry"
  akamai terraform --section default export-property --tfworkpath ${TMP_PROP_PATH} $AK_PROP_VER $AK_PROP
  if test $? -ne 0; then
    rm -rf ${TMP_PROP_PATH}
    echo "### \"$AK_PROP\" is eroor"
    exit 1
  fi
fi

AK_CONTRACT=`grep '"ctr_' ${TMP_PROP_PATH}/variables.tf |cut -d '"' -f2`
AK_GROUP=`grep '"grp_' ${TMP_PROP_PATH}/variables.tf |cut -d '"' -f2`
AK_VER=` find ${TMP_PROP_PATH}/ -type f -name '*.json' -exec grep -H 'propertyVersion' {} +|sed -e 's/.*propertyVersion.: \([0-9]\+\).*/\1/'`
if [ -d ${SCRIPT_DIR}/props/${AK_CONTRACT}/${AK_GROUP}/${AK_PROP} ]; then
  rm -rf ${SCRIPT_DIR}/props/${AK_CONTRACT}/${AK_GROUP}/${AK_PROP}
fi

mkdir -p ${SCRIPT_DIR}/props/${AK_CONTRACT}/${AK_GROUP}
mv ${TMP_PROP_PATH} ${SCRIPT_DIR}/props/${AK_CONTRACT}/${AK_GROUP}/${AK_PROP}

echo "---------------------------------------------"
printf "%12s | %s\n" "ContractID" ${AK_CONTRACT}
printf "%12s | %s\n" "GroupID" ${AK_GROUP}
printf "%12s | %s\n" "Property" ${AK_PROP}
printf "%12s | %s\n" "PropertyVer" ${AK_VER}
echo "---------------------------------------------"

