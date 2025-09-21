#!/bin/bash

#
# build single processor from folder
# ./build.sh <proc-folder>
#
# build multiple processors
# ./build.sh <folder> <folder>
#
# print help and exit
# ./build.sh -h
#
# message output, confirm request, then build all
# ./build.sh
#
# build all without confirmation
# ./build.sh -y

# defining color codes
FAIL='\033[91m'
WARNING='\033[93m'
ENDC='\033[0m'

LANGUAGE="Python"
VENDOR="Trovent Security GmbH"

PREFIX="anx/processors/"

IGNOREFILE=".anxignore"

REGISTRY="registry.trovent.io"

show_help() {
    echo "Usage: $0 [options] [arguments]"
    echo
    echo "Options:"
    echo "  -h         Display this help message"
    echo "  -y         Enable yes flag"
    echo "  -f         Skip validation of MANIFEST and AUTHOR files"
    echo "  -p         Push image to registry after build"
    echo
    echo "Arguments:"
    echo "  arg1-argX  Folder names for processors to be built"
    echo
}

confirm_build() {
    read -p "Do you want to proceed building ALL processors? (y/n): " choice
    case "$choice" in
        y|Y ) return 0;;
        * ) return 1;;
    esac
}

get_version() {
    #
    # read version from _version.py
    #
    FOLDER=$1
    if [ -z "$FOLDER" ]; then
        echo "${FAIL}ERROR: cannot read version - no folder is given.${ENDC}" >&2
        exit 2
    fi

    if [ ! -e "$FOLDER" ]; then
        echo -e "${FAIL}ERROR: cannot read version - folder '$FOLDER' is not existing.${ENDC}\n" >&2
        exit 2
    fi

    if [ ! -d "$FOLDER" ]; then
        echo -e "${FAIL}ERROR: cannot read version - '$FOLDER' is not a folder.${ENDC}\n" >&2
        exit 2
    fi

    if [ ! -f ${FOLDER}/_version.py ]; then
        echo -e "${FAIL}ERROR: cannot read version - version file at '$FOLDER/_version.py' not found.${ENDC}\n" >&2
        echo -e "Copy file ${WARNING}'template/_version.py'${ENDC} into folder ${WARNING}'$FOLDER'${ENDC} and adjust the version number!\n" >&2
        exit 3
    fi

    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo "${FAIL}ERROR: Neither Python3 nor Python is installed.${ENDC}" >&2
        exit 4
    fi

    VERSION=$(${PYTHON_CMD} ${FOLDER}/_version.py)

    if [ -z "$VERSION" ]; then
        echo "${FAIL}ERROR: VERSION info empty.${ENDC}" >&2
        exit 5
    fi

    echo $VERSION
}

# Function to read content from a file
read_file() {
    local file_path=$1
    if [ -f "$file_path" ]; then
        cat "$file_path"
    else
        echo -e "${FAIL}ERROR: $file_path file not found.${ENDC}" >&2
        exit 1
    fi
}

build() {
    FOLDER=$1

    if [ -e $FOLDER/build.sh ]; then
        echo "found explicit build.sh in folder '$FOLDER'..."
        cd $FOLDER
        ./build.sh
        [ $? -eq 0 ] || exit 2
        cd ..
    else
        VERSION=$(get_version $FOLDER)
        NAME="${PREFIX}${FOLDER}"
        TIMESTAMP=$(date --rfc-3339=seconds)

        # Only read MANIFEST and AUTHOR if force flag is not set
        if [ "$force_flag" = false ]; then
            AUTHOR=$(read_file "${FOLDER}/AUTHOR")
            MANIFEST=$(read_file "${FOLDER}/MANIFEST")
            [ $? -eq 0 ] || exit 2
        fi

        if [ -e $FOLDER/icon.svg ]; then
            ICON=$(cat $FOLDER/icon.svg | base64 -w0)
        fi

        echo "building $NAME from folder $FOLDER with version $VERSION"
        echo "tagged without 'latest' to avoid conflicts with other languages"
        if [ "$force_flag" = false ]; then 
        docker build --tag="${NAME}:${VERSION}-${LANGUAGE,,}" \
            --label "anx.processor.version=$VERSION" \
            --label "anx.processor.manifest=$MANIFEST" \
            --label "anx.processor.author=$AUTHOR" \
            --label "org.opencontainers.image.base.language=$LANGUAGE" \
            --label "org.opencontainers.image.created=$TIMESTAMP" \
            --label "org.opencontainers.image.version=$VERSION" \
            --label "org.opencontainers.image.vendor=$VENDOR" \
            $( [ -n "$ICON" ] && echo "--label anx.processor.icon=$ICON" ) \
            $FOLDER
        else
        docker build --tag="${NAME}:${VERSION}-${LANGUAGE,,}" \
            --label "anx.processor.version=$VERSION" \
            --label "org.opencontainers.image.base.language=$LANGUAGE" \
            --label "org.opencontainers.image.created=$TIMESTAMP" \
            --label "org.opencontainers.image.version=$VERSION" \
            --label "org.opencontainers.image.vendor=$VENDOR" \
            $( [ -n "$ICON" ] && echo "--label anx.processor.icon=$ICON" ) \
            $FOLDER
        fi
        [ $? -eq 0 ] || exit 2

        # Push image to registry if push flag is set
        if [ "$push_flag" = true ]; then
            echo
            echo "Retagging $NAME:${VERSION}-${LANGUAGE,,} => $REGISTRY/$NAME:${VERSION}-${LANGUAGE,,}"
            docker tag "$NAME:${VERSION}-${LANGUAGE,,}" "$REGISTRY/$NAME:${VERSION}-${LANGUAGE,,}"
            echo
            echo "Pushing $REGISTRY/$NAME:${VERSION}-${LANGUAGE,,} to registry..."
            docker push "$REGISTRY/${NAME}:${VERSION}-${LANGUAGE,,}"
            [ $? -eq 0 ] || echo -e "${FAIL}ERROR: Failed to push image.${ENDC}" >&2
        fi
    fi
}


# Initialize variables
yes_flag=false
force_flag=false
push_flag=false

# Parse options
while getopts "hyp" opt; do
    case ${opt} in
        h )
            show_help
            exit 0
            ;;
        y )
            yes_flag=true
            ;;
        f )
            force_flag=true
            ;;
        p )
            push_flag=true
            ;;
        \? )
            echo "Invalid option: -$OPTARG" >&2
            show_help
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))


# Main script logic

PROCESSORS="$*"
if [ -z "$PROCESSORS" ]; then
    if [ "$yes_flag" = true ] || confirm_build; then
        PROCESSORS="base"
        echo "parsing ignorefile $IGNOREFILE"
        for DIR in $(find . -mindepth 1 -maxdepth 1 -type d -printf '%P\n');
        do
            RES=$(sed -n /^${DIR}/p $IGNOREFILE)
            if [ -n "$RES" ]; then
                echo "IGNORING: $DIR"
            else
                PROCESSORS="$PROCESSORS $DIR"
            fi
        done
    else
        echo "Aborting."
        exit 1
    fi
fi

echo building: $PROCESSORS

echo
echo "=== Building processor modules ==="
echo
for PROC in $PROCESSORS;
do
    PROC=${PROC%/}
    build $PROC
done
