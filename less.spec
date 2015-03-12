%define less_p_vers 1.82

Summary:	A text file browser similar to more, but better
Name:		less
Version:	475
Release:	1
License:	GPLv3+ or BSD-like
Group:		File tools
Url:		http://www.greenwoodsoftware.com/less
Source0:	http://www.greenwoodsoftware.com/less/%{name}-%{version}.tar.gz
Source1:	faq_less.html
Source2:	http://www-zeuthen.desy.de/~friebel/unix/less/lesspipe-%{less_p_vers}.tar.gz
Patch0:		less-374-manpages.patch
Patch2:		lesspipe-1.72-posix.patch
Patch3:		less-382-fixline.patch
Patch4:		less-392-Foption.patch
# If o3read isn't installed, use the filter that comes with lesspipe
Patch5:		lesspipe-1.72-optional-o3read.patch
Patch6:		less-457-use-odt2txt-in-stead-of-sxw2txt.patch
BuildRequires:	pkgconfig(ncursesw)
# lesspipe.sh requires file
Requires:	file
Suggests:	html2text
Suggests:	odt2txt

%define	__noautoreqfiles %{_bindir}/code2color

%description
The less utility is a text file browser that resembles more, but has
more capabilities.  Less allows you to move backwards in the file as
well as forwards.  Since less doesn't have to read the entire input file
before it starts, less starts up more quickly than text editors (for
example, vi). 

You should install less because it is a basic utility for viewing text
files, and you'll use it frequently.

%prep
%setup -q -a 2
%patch0 -p1 -b .manpages~
pushd lesspipe-%{less_p_vers}
%patch2 -p1 -b .posix~
%patch5 -p1 -b .o3read~
popd

%patch3 -p1 -b .linefix
%patch4 -p1 -b .Foption
%patch6 -p1 -b .odt2xt~
chmod a+r lesspipe-%{less_p_vers}/*
cp lesspipe-%{less_p_vers}/README README.lesspipe
# faq
cp %{SOURCE1} .

# Some source files have very odd permissions
# that happen to be passed on to the debug package
find . -name "*.[ch]" |xargs chmod 0644
chmod +x configure

%build
CFLAGS=$(echo "%{optflags} -DHAVE_LOCALE" | sed -e s/-fomit-frame-pointer//)
%configure
%make
cd lesspipe-%{less_p_vers}
./configure --yes
cd ..

%install
%makeinstall
cd lesspipe-%{less_p_vers}
%makeinstall PREFIX=%{buildroot}%{_prefix}
cd ..
mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
cat << EOF > %{buildroot}%{_sysconfdir}/profile.d/20less.sh
CHARSET=\$(locale charmap 2> /dev/null)
case "\$CHARSET" in 
	UTF-8) 
		export LESSCHARSET="\${LESSCHARSET:-utf-8}" 
	;; 
	*) 
		export LESSCHARSET="\${LESSCHARSET:-koi8-r}" 
	;; 
esac
# Make a filter for less
export LESSOPEN="|/usr/bin/lesspipe.sh %s"
export LESS="-R"
EOF

cat << EOF > %{buildroot}%{_sysconfdir}/profile.d/20less.csh
if ! ( \$?LESSCHARSET ) then
	set CHARSET=\`locale charmap\`
	if ( "\$CHARSET" == "UTF-8" ) then
		setenv LESSCHARSET utf-8
	else
		setenv LESSCHARSET koi8-r
	endif
endif
# Make a filter for less
setenv LESSOPEN "|/usr/bin/lesspipe.sh %s"
setenv LESS "-R"
EOF

cat << EOF > README.urpmi
This version of less includes lesspipe.sh from Wolfgang Friebel
( http://www-zeuthen.desy.de/~friebel/unix/less/ ).

This enables you to view gz, bz2, lzma, zip, rpm and html files
among others with less. It works by setting the LESSOPEN 
environment variable, see the man pages for details.

If you want to disable this behavior, either use 'unset LESSOPEN' or
use an alias ( alias less='less -l' ).

less will open html files with lynx, then html2text, then cat if
none of the previous were found.
EOF

install -m644 lessecho.1 %{buildroot}%{_mandir}/man1

%check
cd lesspipe-%{less_p_vers}
# make sure we're testing stuff with new less and not currently installed one
export PATH=$PWD/../:$PATH
# FIXME The test suite in lesspipe 1.72 doesn't seem to be compatible
# with perl 5.14 -- re-enable once lesspipe tests have been fixed.
#make test

%files
%doc README NEWS README.lesspipe
%doc faq_less.html lesspipe-%{less_p_vers}/{ChangeLog,german.txt,TODO}
%doc README.urpmi
%{_bindir}/*
%{_mandir}/man1/*
%{_sysconfdir}/profile.d/*

