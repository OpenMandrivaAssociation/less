%define	name	less
%define	version	415
%define less_p_vers 1.53

Summary:	A text file browser similar to more, but better
Name:		%{name}
Version:	%{version}
Release:	%mkrel 2
License:	GPL
Url:		http://www.greenwoodsoftware.com/less
Group:		File tools
BuildRequires:	ncurses-devel
Source0:	http://www.greenwoodsoftware.com/less/%{name}-%{version}.tar.bz2
Source1:	faq_less.html
Source2:	http://www-zeuthen.desy.de/~friebel/unix/less/lesspipe-%{less_p_vers}.tar.bz2
Patch0:		less-374-manpages.patch
Patch1:		lesspipe.lynx_for_html.patch
Patch2:		lesspipe-1.53-posix.patch
Patch3:		less-382-fixline.patch
Patch4:		less-392-Foption.patch
#gw we don't have o3read, use the filter that comes with lesspipe
Patch5:		lesspipe-1.53-no-o3read.patch
Patch6:		lesspipe-1.53-lzma-support.patch
Patch7:		less-fix-utf-crash.diff
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
# lesspipe.sh requires file
Requires:	file

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
%patch0 -p1
cd lesspipe-%less_p_vers
%patch1 -p1
%patch2 -p1
%patch5 -p1
%patch6 -p0 -b .lzma
cd ..
%patch3 -p1 -b .fixline
%patch4 -p1 -b .Foption
%patch7 -p0 -b .crash
chmod a+r lesspipe-%less_p_vers/*

%build
CFLAGS=$(echo "%{optflags} -DHAVE_LOCALE" | sed -e s/-fomit-frame-pointer//)
%configure2_5x
%make 
cd lesspipe-%less_p_vers
./configure --yes
cd ..

%install
rm -rf %{buildroot}
%makeinstall
# faq
install -m 644 %{SOURCE1} .
cd lesspipe-%less_p_vers
%makeinstall PREFIX=%{buildroot}%{_prefix}
cd ..
mkdir -p %buildroot%_sysconfdir/profile.d/
cat << EOF > %buildroot%_sysconfdir/profile.d/less.sh
#!/bin/sh
CHARSET=\$(locale charmap 2> /dev/null) 
case "\$CHARSET" in 
       UTF-8) 
               export LESSCHARSET="\${LESSCHARSET:-utf-8}" 
       ;; 
       * ) 
               export LESSCHARSET="\${LESSCHARSET:-koi8-r}" 
       ;; 
esac
# Make a filter for less
export LESSOPEN="|/usr/bin/lesspipe.sh %s"
EOF

cat << EOF > %buildroot%_sysconfdir/profile.d/less.csh
#!/bin/csh
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
EOF

cat << EOF > README.mdk
This version of less includes lesspipe.sh from Wolfgang Friebel
( http://www-zeuthen.desy.de/~friebel//unix/less/ ).

This enables you to view gz, bz2, lzma, zip, rpm and html files
among others with less. It works by setting the LESSOPEN 
environment variable, see the man pages for details.

If you want to disable this behavior, either use 'unset LESSOPEN' or
use an alias ( alias less='less -l' ).

less will open html files with lynx, then html2text, then cat if
none of the previous were found.
EOF

install -m644 lessecho.1 %{buildroot}%{_mandir}/man1

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc faq_less.html lesspipe-%less_p_vers/{BUGS,COPYING,ChangeLog,README,english.txt,german.txt}
%doc README.mdk

%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
%attr(755,root,root) %{_sysconfdir}/profile.d/*
