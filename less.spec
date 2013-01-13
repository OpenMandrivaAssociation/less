%define less_p_vers 1.72

Summary:	A text file browser similar to more, but better
Name:		less
Version:	457
Release:	3
License:	GPLv3+ or BSD-like
Url:		http://www.greenwoodsoftware.com/less
Group:		File tools
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
cd lesspipe-%{less_p_vers}
%patch2 -p1 -b .posix~
%patch5 -p1 -b .o3read~
cd ..
%patch3 -p1 -b .fixline
%patch4 -p1 -b .Foption
%patch6 -p1 -b .odt2xt~
chmod a+r lesspipe-%{less_p_vers}/*
cp lesspipe-%{less_p_vers}/README README.lesspipe

# Some source files have very odd permissions
# that happen to be passed on to the debug package
find . -name "*.[ch]" |xargs chmod 0644

%build
CFLAGS=$(echo "%{optflags} -DHAVE_LOCALE" | sed -e s/-fomit-frame-pointer//)
%configure2_5x
%make
cd lesspipe-%{less_p_vers}
./configure --yes
cd ..

%install
%makeinstall
# faq
install -m 644 %{SOURCE1} .
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
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
%{_sysconfdir}/profile.d/*

%changelog
* Sun Jan 13 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 457-3
- fix mixed-use-of-spaces-and-tabs
- filter out perl dependencies from code2color, less will check for perl itself
  first before trying to use it

* Sun Jan 13 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 457-2
- drop bundled sxw2txt and use odt2txt in stead (P6)

* Mon Jul 23 2012 Alexander Khrukin <akhrukin@mandriva.org> 451-1
+ Revision: 810768
- version update 451

* Mon Jul 16 2012 Alexander Khrukin <akhrukin@mandriva.org> 450-1
+ Revision: 809813
- version update 450

* Thu Feb 23 2012 Bernhard Rosenkraenzer <bero@bero.eu> 444-1
+ Revision: 779418
- Update to 444
- Update lesspipe to 1.72
- Set LESS="-R" in profile.d, fixes (among others)
  colorized git output
- Change the no-o3read patch to check for o3read
  instead of just assuming it's not there and falling
  back
- Remove some obsolete rpm constructs

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 436-5
+ Revision: 666071
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 436-4mdv2011.0
+ Revision: 606400
- rebuild

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 436-3mdv2010.1
+ Revision: 519015
- rebuild

* Sun Sep 27 2009 Olivier Blin <blino@mandriva.org> 436-2mdv2010.0
+ Revision: 449844
- use freshly built less for lesspipe tests (from Arnaud Patard)
  When using a binary coming from debian bootstrap chroot, some
  symbols (ospeed) may differe in size than the one in the bootstrap
  mdv chroot. Using the system less will make tests failing even if
  the freshly built is fine.

* Mon Jul 27 2009 Frederik Himpe <fhimpe@mandriva.org> 436-1mdv2010.0
+ Revision: 400636
- update to new version 436

* Sat May 02 2009 Funda Wang <fwang@mandriva.org> 429-1mdv2010.0
+ Revision: 370565
- New version 429

* Mon Apr 06 2009 Funda Wang <fwang@mandriva.org> 418-6mdv2009.1
+ Revision: 364389
- suggests html2text for displaying html content

* Tue Dec 02 2008 Götz Waschk <waschk@mandriva.org> 418-5mdv2009.1
+ Revision: 309057
- new lesspipe 1.6.0
- update patches 2,5
- update documentation

* Thu Aug 14 2008 Götz Waschk <waschk@mandriva.org> 418-4mdv2009.0
+ Revision: 271984
- lesspipe 1.55
- update patch 5
- drop patch 6

* Mon Jul 28 2008 Götz Waschk <waschk@mandriva.org> 418-3mdv2009.0
+ Revision: 251026
- lesspipe 1.54
- drop patch 1 (lesspipe now prefers links for html)

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 418-2mdv2009.0
+ Revision: 222385
- rebuild

* Wed Jan 23 2008 Gustavo De Nardin <gustavodn@mandriva.com> 418-1mdv2008.1
+ Revision: 157090
- new version 418 (probably fixes bug #35182)
- license change: "GPLv2+" -> "GPLv3+ or BSD-like" (Less license, like
  "FreeBSD BSD Variant (2 clause BSD)", without requirement to reproduce
  list of conditions and the disclaimer)

* Sat Dec 22 2007 Guillaume Rousse <guillomovitch@mandriva.org> 416-3mdv2008.1
+ Revision: 136997
- rename README.mdk into README.urpmi
- no executable bit on profile scriptlets
  order prefix on profile scriptlets

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Nov 27 2007 Funda Wang <fwang@mandriva.org> 416-1mdv2008.1
+ Revision: 113446
- New version 416
- drop UTF-8 patch (merged upstream)
- Build against ncursesw

* Thu Nov 22 2007 Thierry Vignaud <tv@mandriva.org> 415-2mdv2008.1
+ Revision: 111277
- patch 7: fix crash on UTF-8 files (#35710)

* Fri Nov 16 2007 Funda Wang <fwang@mandriva.org> 415-1mdv2008.1
+ Revision: 109082
- update to new version 415

* Sun Oct 14 2007 Gustavo De Nardin <gustavodn@mandriva.com> 409-1mdv2008.1
+ Revision: 98231
- new version 409, fixes an UTF-8 related crash when searching

* Fri Oct 12 2007 Thierry Vignaud <tv@mandriva.org> 408-1mdv2008.1
+ Revision: 97436
- new release
- update URL

* Mon Jul 09 2007 Funda Wang <fwang@mandriva.org> 406-1mdv2008.0
+ Revision: 50443
- New version

* Thu Jun 07 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 403-2mdv2008.0
+ Revision: 36721
- bump
- fix lzma patch

* Thu May 31 2007 Götz Waschk <waschk@mandriva.org> 403-1mdv2008.0
+ Revision: 33458
- new version
- unpack patches

* Fri May 04 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 394-5mdv2008.0
+ Revision: 22159
- add support for lzma (P6)
- Import less

