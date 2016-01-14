%global scl_name_base devassist
%global scl_name_version 09
%global scl %{scl_name_base}%{scl_name_version}

%scl_package %scl

# the -build subpackage may already be in the buildroot, so we can't use %%python_site{lib,arch}
%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
%global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")
%global devassist09_python_sitelib %{_scl_root}/%{python_sitelib}
%global devassist09_python_sitearch %{_scl_root}/%{python_sitearch}

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: Package that installs %scl
Name: %scl_name
Version: 1.2
Release: 4%{?dist}
License: GPLv2+
Source0: README
Source1: LICENSE
Source2: macros.additional.%{scl}
BuildRequires: help2man
BuildRequires: scl-utils-build
Requires: %{scl_prefix}devassistant
Requires: %{scl_prefix}devassistant-assistants-dts

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE0})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE1} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export PYTHONPATH=%{devassist09_python_sitelib}:%{devassist09_python_sitearch}\${PYTHONPATH:+:\${PYTHONPATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF
%scl_install

# Add the aditional macros to macros.%%{scl}-config
cat %{SOURCE2} >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
sed -i -e 's|@python_sitearch|%{python_sitearch}|' \
       -e 's|@python_sitelib|%{python_sitelib}|' \
       -e 's|@devassist09_python_sitearch|%{devassist09_python_sitearch}|' \
       -e 's|@devassist09_python_sitelib|%{devassist09_python_sitelib}|' \
    %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Create the scldevel subpackage macros
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%files

%files runtime -f filesystem
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Tue Jun 03 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2-4
- Make metapackage depend on the actual assistant set

* Mon May 26 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2-3
- Also add Python's sitearch to SCL's PYTHONPATH

* Thu May 22 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2-2
- Rebuilt for RHEL 7

* Wed May 21 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2-1
- Initial package
