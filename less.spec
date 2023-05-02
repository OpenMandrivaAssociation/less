%undefine beta

%global optflags %{optflags} -Oz

Summary:	A text file browser similar to more, but better
Name:		less
Version:	632
Release:	1
License:	GPLv3+ or BSD-like
Group:		File tools
Url:		http://www.greenwoodsoftware.com/less
Source0:	http://www.greenwoodsoftware.com/less/%{name}-%{version}%{?beta:-%{beta}}.tar.gz
Patch0:		less-374-manpages.patch
Patch3:		less-382-fixline.patch
BuildRequires:	pkgconfig(ncursesw)

%description
The less utility is a text file browser that resembles more, but has
more capabilities.  Less allows you to move backwards in the file as
well as forwards.  Since less doesn't have to read the entire input file
before it starts, less starts up more quickly than text editors (for
example, vi).

You should install less because it is a basic utility for viewing text
files, and you'll use it frequently.

%prep
%autosetup -p1

# Some source files have very odd permissions
# that happen to be passed on to the debug package
find . -name "*.[ch]" |xargs chmod 0644
chmod +x configure

%build
CFLAGS=$(echo "%{optflags} -DHAVE_LOCALE" | sed -e s/-fomit-frame-pointer//)
%configure
%make_build

%install
%make_install
mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
cat << EOF > %{buildroot}%{_sysconfdir}/profile.d/20less.sh
export LESS="-R"
EOF

cat << EOF > %{buildroot}%{_sysconfdir}/profile.d/20less.csh
setenv LESS "-R"
EOF

install -m644 lessecho.1 %{buildroot}%{_mandir}/man1

%files
%doc README NEWS
%{_bindir}/*
%doc %{_mandir}/man1/*
%{_sysconfdir}/profile.d/*
