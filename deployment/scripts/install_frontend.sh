#!/usr/bin/env bash -x
AZURE_URL_BASE='https://csbe84f90ab76c8x42efx95a.blob.core.windows.net'
FALLBACK_BRANCH='integration'

echo "**********************************"
echo env
echo "**********************************"

#check if BRANCH env variable exists
if [ -z "$BRANCH" ]; then
    BRANCH=`git rev-parse --symbolic-full-name --abbrev-ref HEAD`
fi

#check if BUILD env variable exists
if [ -z "$BUILD" ]; then
    echo "trying ... ${AZURE_URL_BASE}/${BRANCH}/manifest.txt"
    BUILD=`curl -s ${AZURE_URL_BASE}/${BRANCH}/manifest.txt`
else
    BUILD="build-${BUILD}.tar.gz"
fi
echo "BUILD: ${BUILD}"


if [[ $BUILD = *"NotFound"* ]]; then
    echo "no branch or manifest, falling back"
    BRANCH=$FALLBACK_BRANCH
    echo "BRANCH: ${BRANCH} (fallback)"
    echo "trying ... ${AZURE_URL_BASE}/${BRANCH}/manifest.txt"
    BUILD=`curl -s ${AZURE_URL_BASE}/${BRANCH}/manifest.txt`
fi

echo "BRANCH: ${BRANCH}"
echo "BUILD: ${BUILD}"

echo "downloading ..."
echo "trying ... ${AZURE_URL_BASE}/${BRANCH}/${BUILD}"
curl -s -o "/tmp/${BUILD}" "${AZURE_URL_BASE}/${BRANCH}/${BUILD}"

echo "putting things in place ..."
rm -rf ../../frontend/static/*
tar zxvf "/tmp/${BUILD}" -C ../../frontend/ --wildcards '*static*'
tar zxvf "/tmp/${BUILD}" -C ../../frontend/templates/ --wildcards '*index.html*'

DATE=`date +"%Y-%m-%d %H:%M"`

echo "timestamping ..."
echo "" >> ../../frontend/templates/index.html
echo "<!-- BRANCH: ${BRANCH} -->" >> ../../frontend/templates/index.html
echo "<!-- BUILD: ${BUILD} -->" >> ../../frontend/templates/index.html
echo "<!-- INSTALLED: ${DATE} -->" >> ../../frontend/templates/index.html

echo $DATE
