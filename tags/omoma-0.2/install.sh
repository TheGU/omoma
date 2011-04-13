#!/bin/bash

echo "=================="
echo "Omoma installation"
echo "=================="
echo ""
echo "This command automatically installs a local instance of Omoma."
echo ""

scriptname=`readlink -f "$0"`
sourcedir=`dirname "$scriptname"`

# Ask user where (s)he wants to install Omoma
echo "Where do you want to install Omoma?"
echo "(default: $HOME/omoma)"
echo -n "> "
read -e omomapath

# Get the full destination path
if [ -z "$omomapath" ]
then
    omomapath="$HOME/omoma"
elif [ "`echo $omomapath | cut -c1`" != "/" ]
then
    omomapath="`pwd`/$omomapath"
fi

# Test if the destination directory already exists
if [ -e "$omomapath" ]
then
    echo "$omomapath already exists."
    echo "Omoma installation cancelled."
    exit 1
fi

echo ""
echo "          Omoma will be installed in in $omomapath..."
echo ""

mkdir -p "$omomapath"
# Test if the destination directory is created
if [ ! -e "$omomapath" ]
then
    echo "$omomapath cannot be created."
    echo "Omoma installation cancelled."
    exit 1
fi

echo ""
echo "############################################################"

# Get the user's timezone
timezone=`tzselect`

if [ -z "$timezone" ]
then
    echo "No timezone specified."
    echo "Omoma installation cancelled."
    exit 1
fi

echo ""
echo "############################################################"

# Get the user's language code
echo "Select the default language code"
echo "(see http://www.i18nguy.com/unicode/language-identifiers.html)"
echo "Examples: ar-OM, en-US, eo, fr-FR, ja, ru-RU..."
echo "> "
read languagecode

if [ -z "$languagecode" ]
then
    echo "No languagecode specified."
    echo "Omoma installation cancelled."
    exit 1
fi

# Generating a secret key would be better
secretkey="secretkey"

echo ""
echo "############################################################"
echo ""

# Copy the files
cp -r "$sourcedir/omoma/"* "$omomapath/"
cp "$omomapath/local_settings.py.default" "$omomapath/local_settings.py"
sed -i "s*<PATH_TO_OMOMA>*$omomapath*" "$omomapath/local_settings.py"
sed -i "s*<TIMEZONE>*$timezone*" "$omomapath/local_settings.py"
sed -i "s/<LANGUAGECODE>/$languagecode/" "$omomapath/local_settings.py"
sed -i "s/<SECRET_KEY>/$secretkey/" "$omomapath/local_settings.py"

echo "Omoma is installed in \"$omomapath\"!"
echo ""
echo "The following dependencies are needed:"
echo " - Django"
echo " - SQLite (and Python-Sqlite)"
echo " - OFX tools"
echo ""
echo "Run \"python $omomapath/manage.py syncdb\" to initialize Omoma data."
