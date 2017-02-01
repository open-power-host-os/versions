Contributing
************

This is an open source project and thus you're welcome to contribute!

How to contribute a new package to Host OS
------------------------------------------

Create a new directory at https://github.com/open-power-host-os/versions repository named <package_name>.

Under this new directory:

1. Create a metadata file named <package_name>.yaml. It will contain most of the information required to build the package. The package metadata (yaml) file format is described at https://github.com/open-power-host-os/versions/package_metadata_yaml_template.yaml. You can use this template to start your own metadata file.
2. Create a nested directory named <distro_name>/<distro_version>, e.g. CentOS/7.
3. Create an rpm package specification file in <package_name>/<distro_name>/<distro_version>/<package_name>.spec.
4. Copy any extra files required to build the package to <package_name>/<distro_name>/<distro_version>/SOURCES/. These extra files are the ones which are not available in one of the sources of the package for some reason.

If the rpm specification file has a %check macro for running tests during rpm package build, add the following code to allow skipping these tests:

1. Add at the beginning of the file:

::

   # The tests are disabled by default.
   # Set --with tests or bcond_without to run tests.
   %bcond_with tests


2. Add at the point of %check macro:

::

   %if %{with tests}
   %check
   # any code used to verify, e.g.:
   make V=1 check
   %endif

