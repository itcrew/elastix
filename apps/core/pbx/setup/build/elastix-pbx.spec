%define modname pbx 

Summary: Elastix Module PBX 
Name:    elastix-%{modname}
Version: 2.4.0
Release: 12
License: GPL
Group:   Applications/System
Source0: %{modname}_%{version}-%{release}.tgz
#Source0: %{modname}_%{version}-20.tgz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Prereq: elastix-framework >= 2.3.0-9
Prereq: elastix-my_extension >= 2.0.4-5
Prereq: freePBX >= 2.11.0-1
Prereq: elastix-system >= 2.3.0-10
Prereq: tftp-server, vsftpd
Prereq: asterisk >= 1.8
Requires: festival >= 1.95

%description
Elastix Module PBX

%prep
%setup -n %{modname}

%install
rm -rf $RPM_BUILD_ROOT

# Asterisk files
mkdir -p $RPM_BUILD_ROOT/var/lib/asterisk/agi-bin
mkdir -p $RPM_BUILD_ROOT/var/lib/asterisk/mohmp3

mkdir -p $RPM_BUILD_ROOT/etc/cron.daily

# ** /bin path ** #
mkdir -p $RPM_BUILD_ROOT/bin

# Files provided by all Elastix modules
mkdir -p    $RPM_BUILD_ROOT/var/www/html/
mv modules/ $RPM_BUILD_ROOT/var/www/html/

# ** files ftp ** #
#mkdir -p $RPM_BUILD_ROOT/var/ftp/config

# ** /tftpboot path ** #
mkdir -p $RPM_BUILD_ROOT/tftpboot

# ** /asterisk path ** #
mkdir -p $RPM_BUILD_ROOT/etc/asterisk/

# ** service festival ** #
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
mkdir -p $RPM_BUILD_ROOT/var/log/festival/

# The following folder should contain all the data that is required by the installer,
# that cannot be handled by RPM.
mkdir -p      $RPM_BUILD_ROOT/usr/share/elastix/module_installer/%{name}-%{version}-%{release}/
mkdir -p      $RPM_BUILD_ROOT/usr/share/elastix/privileged/

# crons config
mv setup/etc/cron.daily/asterisk_cleanup      $RPM_BUILD_ROOT/etc/cron.daily/
chmod 755 $RPM_BUILD_ROOT/etc/cron.daily/*
rmdir setup/etc/cron.daily/

# ** asterisk.reload file ** #
mv setup/bin/asterisk.reload                  $RPM_BUILD_ROOT/bin/
chmod 755 $RPM_BUILD_ROOT/bin/asterisk.reload
rmdir setup/bin

# ** files asterisk for agi-bin and mohmp3 ** #
mv setup/asterisk/agi-bin/*                   $RPM_BUILD_ROOT/var/lib/asterisk/agi-bin/
chmod 755 $RPM_BUILD_ROOT/var/lib/asterisk/agi-bin/*
mv setup/asterisk/mohmp3/*                    $RPM_BUILD_ROOT/var/lib/asterisk/mohmp3/
rmdir setup/asterisk/*
rmdir setup/asterisk

# Moviendo archivos festival y sip_notify_custom_elastix.conf
chmod +x setup/etc/asterisk/sip_notify_custom_elastix.conf
chmod +x setup/etc/init.d/festival
mv setup/etc/asterisk/sip_notify_custom_elastix.conf      $RPM_BUILD_ROOT/etc/asterisk/
mv setup/etc/init.d/festival                              $RPM_BUILD_ROOT/etc/init.d/
mv setup/usr/share/elastix/privileged/*                   $RPM_BUILD_ROOT/usr/share/elastix/privileged/
rmdir setup/etc/init.d
rmdir setup/etc/asterisk
rmdir setup/usr/share/elastix/privileged

# Archivos tftp and ftp
mv setup/etc/xinetd.d/tftp                     $RPM_BUILD_ROOT/usr/share/elastix/
rmdir setup/etc/xinetd.d

# ** files tftpboot for endpoints configurator ** #
unzip setup/tftpboot/P0S3-08-8-00.zip  -d     $RPM_BUILD_ROOT/tftpboot/
mv setup/tftpboot/*                           $RPM_BUILD_ROOT/tftpboot/

# Install new endpoint configurator
mkdir -p $RPM_BUILD_ROOT/usr/bin/
mv setup/usr/bin/elastix-endpoint-configure $RPM_BUILD_ROOT/usr/bin/
chmod 755 $RPM_BUILD_ROOT/usr/bin/elastix-endpoint-configure
mv setup/usr/bin/fix-model-duplicates-bug1618 $RPM_BUILD_ROOT/usr/bin/
chmod 755 $RPM_BUILD_ROOT/usr/bin/fix-model-duplicates-bug1618
mv setup/usr/share/elastix/endpoint-vendors $RPM_BUILD_ROOT/usr/share/elastix/

rmdir setup/usr/share/elastix setup/usr/share setup/usr/bin setup/usr

mv setup/     $RPM_BUILD_ROOT/usr/share/elastix/module_installer/%{name}-%{version}-%{release}/
mv menu.xml   $RPM_BUILD_ROOT/usr/share/elastix/module_installer/%{name}-%{version}-%{release}/


%pre
#Para migrar monitor
touch /tmp/migration_version_monitor.info
rpm -q --queryformat='%{VERSION}\n%{RELEASE}' elastix > /tmp/migration_version_monitor.info

# TODO: TAREA DE POST-INSTALACIÓN
#useradd -d /var/ftp -M -s /sbin/nologin ftpuser

# Try to fix mess left behind by previous packages.
if [ -e /etc/vsftpd.user_list ] ; then
    echo "   NOTICE: broken vsftpd detected, will try to fix..."
    cp /etc/vsftpd.user_list /tmp/
fi

mkdir -p /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/
touch /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
if [ $1 -eq 2 ]; then
    rpm -q --queryformat='%{VERSION}-%{RELEASE}' %{name} > /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
fi

%post
# Tareas de TFTP
chmod 777 /tftpboot/

# TODO: TAREA DE POST-INSTALACIÓN
# Tareas de VSFTPD
#chkconfig --level 2345 vsftpd on
#chmod 777 /var/ftp/config

# TODO: TAREA DE POST-INSTALACIÓN
# Reemplazo archivos de otros paquetes: tftp, vsftp
cat /usr/share/elastix/tftp   > /etc/xinetd.d/tftp

######### Para ejecucion del migrationFilesMonitor.php ##############

#/usr/share/elastix/migration_version_monitor.info
#obtener la primera linea que contiene la version

vers=`sed -n '1p' "/tmp/migration_version_monitor.info"`
if [ "$vers" = "1.6.2" ]; then
  rels=`sed -n '2p' "/tmp/migration_version_monitor.info"`
  if [ $rels -le 13 ]; then # si el release es menor o igual a 13 entonces ejecuto el script

    echo "Executing process migration audio files Monitor"
    chmod +x /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/setup/migrationFilesMonitor.php
    php /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/setup/migrationFilesMonitor.php
  fi
fi
rm -rf /tmp/migration_version_monitor.info
###################################################################

varwriter=0

if [ -f "/etc/asterisk/extensions_override_freepbx.conf" ]; then
    echo "File extensions_override_freepbx.conf in asterisk exits, verifying macro record-enable and hangupcall exists..."
    grep "#include extensions_override_elastix.conf" /etc/asterisk/extensions_override_freepbx.conf &>/dev/null
    res=$?
    if [ $res -eq 1 ]; then #macro record-enable not exists
	echo "#include extensions_override_elastix.conf" > /tmp/ext_over_freepbx.conf
        cat /etc/asterisk/extensions_override_freepbx.conf >> /tmp/ext_over_freepbx.conf
        cat /tmp/ext_over_freepbx.conf > /etc/asterisk/extensions_override_freepbx.conf
	rm -rf /tmp/ext_over_freepbx.conf
        echo "macros elastix was written."
    fi
else
    echo "File extensions_override_freepbx.conf in asterisk not exits, copying include macros elastix..."
    touch /etc/asterisk/extensions_override_freepbx.conf
    echo "#include extensions_override_elastix.conf" > /etc/asterisk/extensions_override_freepbx.conf
fi

# verifico si se incluye a sip_notify_custom_elastix.conf
if [ -f "/etc/asterisk/sip_notify_custom.conf" ]; then
    echo "/etc/asterisk/sip_notify_custom.conf exists, verifying the inclusion of sip_notify_custom_elastix.conf"
    grep "#include sip_notify_custom_elastix.conf" /etc/asterisk/sip_notify_custom.conf &> /dev/null
    if [ $? -eq 1 ]; then
	echo "including sip_notify_custom_elastix.conf..."
	echo "#include sip_notify_custom_elastix.conf" > /tmp/custom_elastix.conf
	cat /etc/asterisk/sip_notify_custom.conf >> /tmp/custom_elastix.conf
	cat /tmp/custom_elastix.conf > /etc/asterisk/sip_notify_custom.conf
	rm -rf /tmp/custom_elastix.conf
    else
	echo "sip_notify_custom_elastix.conf is already included"
    fi
else
    echo "creating file /etc/asterisk/sip_notify_custom.conf"
    touch /etc/asterisk/sip_notify_custom.conf
    echo "#include sip_notify_custom_elastix.conf" > /etc/asterisk/sip_notify_custom.conf
fi

varwriter=1
mv /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/setup/extensions_override_elastix.conf /etc/asterisk/
chown -R asterisk.asterisk /etc/asterisk

if [ $varwriter -eq 1  ]; then
    service asterisk status &>/dev/null
    res2=$?
    if [ $res2 -eq 0  ]; then #service is up
         service asterisk reload
    fi
fi

pathModule="/usr/share/elastix/module_installer/%{name}-%{version}-%{release}"
# Run installer script to fix up ACLs and add module to Elastix menus.
elastix-menumerge /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/menu.xml

pathSQLiteDB="/var/www/db"
mkdir -p $pathSQLiteDB
preversion=`cat $pathModule/preversion_%{modname}.info`
rm -f $pathModule/preversion_%{modname}.info

if [ $1 -eq 1 ]; then #install
  # The installer database
  elastix-dbprocess "install" "/usr/share/elastix/module_installer/%{name}-%{version}-%{release}/setup/db"
elif [ $1 -eq 2 ]; then #update
  # The installer database
   elastix-dbprocess "update"  "$pathModule/setup/db" "$preversion"

  # Elastix bug #1618 - need to scan and fix model duplicates
  /usr/bin/fix-model-duplicates-bug1618
fi

#verificando si existe el menu en pbx
path="/var/www/db/acl.db"
path2="/var/www/db/menu.db"
id_menu="control_panel"

#obtenemos el id del recurso (EOP)
res=`sqlite3 $path "select id from acl_resource  where name='control_panel'"`

#obtenemos el id del grupo operador
opid=`sqlite3 $path "select id from acl_group  where name='Operator'"`

if [ $res ]; then #debe de existir el recurso EOP
   if [ $opid ]; then #debe de existir el grupo operador
      val=`sqlite3 $path "select * from acl_group_permission where id_group=$opid and id_resource=$res"`
      if [ -z $val ]; then #se pregunta si existe el permiso de EOP para el grupo Operador
         echo "updating group Operator with permissions in Control Panel Module"
	 `sqlite3 $path "insert into acl_group_permission(id_action, id_group, id_resource) values(1,$opid,$res)"`
      fi
   fi
fi

# The installer script expects to be in /tmp/new_module
mkdir -p /tmp/new_module/%{modname}
cp -r /usr/share/elastix/module_installer/%{name}-%{version}-%{release}/* /tmp/new_module/%{modname}/
chown -R asterisk.asterisk /tmp/new_module/%{modname}

php /tmp/new_module/%{modname}/setup/installer.php
rm -rf /tmp/new_module

# Detect need to fix up vsftpd configuration
if [ -e /tmp/vsftpd.user_list ] ; then
    echo "   NOTICE: fixing up vsftpd configuration..."
    # userlist_deny=NO
    sed --in-place "s,userlist_deny=NO,#userlist_deny=NO,g" /etc/vsftpd/vsftpd.conf
    rm -f /tmp/vsftpd.user_list
fi


%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ $1 -eq 0 ] ; then # Validation for desinstall this rpm; delete
pathModule="/usr/share/elastix/module_installer/%{name}-%{version}-%{release}"
  echo "Delete System menus"
  elastix-menuremove "pbxconfig"

  echo "Dump and delete %{name} databases"
  elastix-dbprocess "delete" "$pathModule/setup/db"
fi

%files
%defattr(-, asterisk, asterisk)
/etc/asterisk/sip_notify_custom_elastix.conf
/var/lib/asterisk/*
/var/lib/asterisk/agi-bin
/var/log/festival
/usr/share/elastix/module_installer/%{name}-%{version}-%{release}/setup/extensions_override_elastix.conf
%defattr(-, root, root)
%{_localstatedir}/www/html/*
/usr/share/elastix/module_installer/*
/tftpboot/*
/usr/share/elastix/tftp
/usr/share/elastix/endpoint-vendors
%defattr(755, root, root)
/usr/bin/elastix-endpoint-configure
/usr/bin/fix-model-duplicates-bug1618
/etc/init.d/festival
/bin/asterisk.reload
/usr/share/elastix/privileged/*
/var/lib/asterisk/agi-bin/*
/etc/cron.daily/asterisk_cleanup

%changelog
* Thu Sep 19 2013 Jose Briones <jbriones@elastix.com>
- UPDATED: Module endpoints_batch, the help section was updated
  SVN Rev[5907]

* Thu Sep 19 2013 Jose Briones <jbriones@elastix.com>
- UPDATED: Module control_panel, the help section was updated
  SVN Rev[5905]

* Wed Sep 18 2013 Jose Briones <jbriones@elastix.com>
- UPDATED: Module control_panel. The help section was updated
  SVN Rev[5897]

* Tue Sep 10 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-12
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.

* Tue Sep 10 2013 Luis Abarca <labarca@palosanto.com> 
- FIXED: Problem about upload a recorded file with a registered extension its
  now solved.
  SVN Rev[5846]

* Wed Sep 04 2013 Luis Abarca <labarca@palosanto.com> 
- CHANGED: pbx - pbxadmin/contentFreePBX.php,main.tpl,es.lang: Changed the name
  of the link 'Zap Channel DIDs' to 'DAHDI Channel DIDs', and fixed the url to
  this module.
  SVN Rev[5836]

* Wed Sep 04 2013 Luis Abarca <labarca@palosanto.com> 
- ADDED: pbx - pbxadmin/mainstyle.css,current.js,main.tpl: Now the left menu
  shows a current link indicator of navigation.
  SVN Rev[5831]

* Wed Sep 04 2013 Luis Abarca <labarca@palosanto.com> 
- CHANGED: pbx - pbxadmin/contentFreePBX.php,main.tpl,es.lang: Changed the name
  of the link 'Day/Night Control' to 'Call Flow Control'.
  SVN Rev[5830]

* Wed Aug 28 2013 Luis Abarca <labarca@palosanto.com> 
- ADDED: pbx -Build/elastix-pbx.spec: From this release onwards, the package
  now have as a prerequisite the new version of FreePBX => 2.11.0 to be
  installed.
  SVN Rev[5810]

* Thu Aug 22 2013 Luis Abarca <labarca@palosanto.com> 
- CHANGED: pbx - menu.xml: Another correction to the FOP link for proper
  operation of module.
  SVN Rev[5798]

* Thu Aug 22 2013 Luis Abarca <labarca@palosanto.com> 
- FIXED: pbx - menu.xml: Now the link to FOP its corrected for proper operation
  of module.
  SVN Rev[5797]

* Wed Aug 21 2013 Luis Abarca <labarca@palosanto.com> 
- CHANGED: pbx - modules/pbxadmin/themes/default: A total change in this folder
  for better support to new FreePBX.
  SVN Rev[5796]

* Wed Aug 21 2013 Luis Abarca <labarca@palosanto.com> 
- REMOVED: pbx - modules/pbxadmin: Its no longer necesary the use of a folder
  with the js's files.
  SVN Rev[5795]

* Wed Aug 21 2013 Luis Abarca <labarca@palosanto.com> 
- CHANGED: pbx - pbxadmin/contentFreePBX.php: This library now its updated for
  better support to new FreePBX.
  SVN Rev[5794]

* Wed Aug 21 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-11
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
- ADDED: pbx -Build/elastix-pbx.spec: From this release onwards, the package 
  has as a prerequisite the new version of FreePBX => 2.11.0 to be installed. 
  SVN Rev[5792]

* Tue Aug 20 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Endpoint Configurator: add support for Elastix LXP100.
  SVN Rev[5778]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5633]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5632]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5631]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5630]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5629]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5628]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5627]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5626]

* Thu Aug 08 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file fr.lang.
  SVN Rev[5625]

* Tue Aug 06 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file es.lang.
  SVN Rev[5572]

* Tue Aug 06 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file es.lang.
  SVN Rev[5571]

* Mon Aug 05 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-10
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5560]

* Mon Aug 05 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file es.lang.
  SVN Rev[5513]

* Mon Aug 05 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Correction of some mistakes in the translation file es.lang.
  SVN Rev[5512]

* Fri Aug 02 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module file_editor. Correction of some mistakes in the translation
  files.
  SVN Rev[5503]

* Fri Aug 02 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module conference. Support Added for the translation of some words.
  SVN Rev[5502]

* Fri Aug 02 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module monitoring. Correction of some mistakes in the translation
  files.
  SVN Rev[5501]

* Fri Aug 02 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Support added to allow the translation of most of the words in
  control_panel module.
  SVN Rev[5500]


* Thu Aug 01 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Conference: relax regexp to extract from lines in 'meetme list'. Fixes
  Elastix bug #1652.
- FIXED: Conference: in Asterisk 11, Invite Caller fails because both 
  Application and Context/Priority are specified for Originate. Fixed.
- FIXED: Conference: list all extensions, not just SIP.
  SVN Rev[5491]
- FIXED: Conference: remove bogus reference to PST/PDT timezone in conference
  start time. Fixes Elastix bug #1650.
  SVN Rev[5479]

* Wed Jul 31 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module voicemail. Correction of some mistakes in the translation
  files.
  SVN Rev[5477]

* Wed Jul 31 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module text_to_wav. Correction of some mistakes in the translation
  files.
  SVN Rev[5472]

* Mon Jul 29 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module recordings. Correction of some mistakes in the translation
  files.
  SVN Rev[5451]

* Mon Jul 29 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module pbxadmin. Correction of some mistakes in the translation
  files.
  SVN Rev[5441]

* Mon Jul 29 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module monitoring. Correction of some mistakes in the translation
  files.
  SVN Rev[5436]

* Wed Jul 24 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module file_editor. Correction of some mistakes in the translation
  files.
  SVN Rev[5411]

* Wed Jul 24 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module festival. Correction of some mistakes in the translation
  files.
  SVN Rev[5410]

* Wed Jul 24 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module  extensions_batch. Correction of some mistakes in the
  translation files.
  SVN Rev[5401]

* Wed Jul 24 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module  endpoints_batch. Correction of some mistakes in the
  translation files.
  SVN Rev[5400]

* Wed Jul 24 2013 Jose Briones <jbriones@palosanto.com> 
- UPDATED: Module  endpoint_configurator. Correction of some mistakes in the
  translation files.
  SVN Rev[5399]

* Tue Jul 23 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-9
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5393]

* Mon Jul 22 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Extensions Batch: fix invalid SQL query that gets executed when an 
  extension requires a direct DID.
  SVN Rev[5387]

* Thu Jul 18 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-8
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5352]

* Wed Jul 17 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- DELETED: Asterisk CLI: remove unused folder i18n
  SVN Rev[5319]  

* Thu Jul 04 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- ADDED: Endpoint Configurator: add a script that will scan for model duplicates
  and move all endpoints references to the first item before removing the 
  duplicates. Final fix for Elastix bug #1618.
  SVN Rev[5215]
- FIXED: Endpoint Configurator: rename SQL file for update which was incorrectly
  named. This will prevent the update from being applied twice when updating 
  from 2.4.0-1 to versions later than 2.4.0-7. Partially fixes Elastix bug #1618.
  SVN Rev[5213]

* Tue Jun 25 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-7
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5128]

* Mon Jun 24 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Control Panel, Recordings: specify Context for AMI Originate instead of
  a blank field. Fixes Elastix bug #1605.
  SVN Rev[5121]

* Tue Jun 18 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Voicemail, Monitoring: stop using popup.tpl. The blackmin theme lacks
  this template, and these two are the only two modules to use it. Additionally
  the template triggers javascript errors due to missing jquery. It is easier to
  just embed the html header and footer.
  SVN Rev[5108]
- CHANGED: Endpoint Configurator: prevent potential use of unset array element
  in session at construction of PaloSantoFileEndPoint.
  SVN Rev[5107]

* Mon Jun 17 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-6
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5102]

* Thu Jun 13 2013 Alberto Santos <asantos@palosanto.com>
- FIXED: script hangup.agi. Fixed a missplaced code at line 89. Also changed
  the method to call the scripts.
  SVN Rev[5096]

* Wed Jun 12 2013 José Briones <jbriones@palosanto.com>
- UPDATED: Module conference. The help section was updated.
  SVN Rev[5091]

* Wed Jun 12 2013 José Briones <jbriones@palosanto.com>
- ADDED: Added new file of sql commands for the new phone Grandstream GXP2200
  in endpoint database.
  SVN Rev[5089]

* Wed Jun 12 2013 José Briones <jbriones@palosanto.com>
- UPDATE: Module endpoint_configurator, Support for GXP2200 was added, and
  support for GXV3140 was improved.
  SVN Rev[5087]

* Tue Jun 11 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-5
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5081]

* Thu Jun 06 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: File Editor, Monitoring, Voicemail: remove duplicate definition of
  getParameter() that gets confused by Fortify as the one used by the framework.
  SVN Rev[5057]

* Tue Jun 04 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Configurator: search of extension given IP can falsely match
  another IP of which the target IP is a prefix. Fixed. Fixes part of Elastix 
  bug #1570.
  SVN Rev[5052]

* Mon May 27 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-4
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Bump Release in specfile.
  SVN Rev[5015]

* Wed May 22 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Configurator: add missing check for IPv4 address format.
  Pointed out by Fortify report.
  SVN Rev[4999]
- FIXED: Batch of Endpoints: remove unnecessary and risky copy of uploaded file.
  Pointed out by Fortify report.
  SVN Rev[4998] 

* Tue May 21 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Asterisk CLI: rewrite to use escapeshellarg properly instead of
  reimplementing special character filtering. Remove bogus unused library.
  SVN Rev[4991]

* Mon May 20 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Recordings: fix a number of command injection vulnerabilities. Replace
  calls to exec with corresponding internal functions for mkdir(). Clean up
  code indentation. Pointed out by Fortify report.
  SVN Rev[4977]

* Thu May 16 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Extensions Batch: rewrite the entire module to get rid of multiple
  opportunities for SQL injection and code execution. Tighten up and centralize
  validations on CSV fields. Improve readability and make the code smaller.
  SVN Rev[4954]

* Mon May 13 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-3
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile. 
  SVN Rev[4920]

* Mon May 13 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Control Panel: validate several parameters before building AMI requests
  with them. More of the same.
  SVN Rev[4917]
- FIXED: Conference: validate several conference parameters before building AMI
  requests with them. Fixes Elastix bug #1551.
  SVN Rev[4915]

* Wed May 07 2013 José Briones <jbriones@palosanto.com>
- ADDED: Added new file of sql commands for new phones models in endpoint
  database.
  SVN Rev[4906]
- ADDED: support for new vendor Voptech VI2006, VI2007, VI2008.
  SVN Rev[4903]
- CHANGED: endpoints_batch : support for new vendor Voptech.
  SVN Rev[4900]
- CHANGED: support for new vendor Voptech.
  SVN Rev[4899]
- CHANGED: support for new vendor Voptech, models VI2006, VI2007, VI2008.
  SVN Rev[4898]
- ADDED: Added support for new vendor Voptech.
  SVN Rev[4897]

* Mon May 06 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Voicemail: check that voicemail password is numeric before writing 
  configuration. Fixes Elastix bug #1547.
  SVN Rev[4886]
- FIXED: Voicemail: check that specified extension belongs to user before 
  deleting voicemail. Fixes Elastix bug #1546.
  SVN Rev[4885]

* Mon Apr 15 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-2
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4839]

* Thu Apr 04 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: conference module, help section was updated.
  SVN Rev[4793]

* Thu Apr 04 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: conference module, help section was updated.
  SVN Rev[4792]

* Thu Mar 14 2013 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Batch of Extensions: the keywords that encode the recording options 
  must be written to the database with capital first letter. Fixes rest of
  Elastix bug #1435. 
  SVN Rev[4755]
- FIXED: Batch of Extensions: relax extension secret validation to match the 
  validations performed by the FreePBX javascript checks. Fixes part of Elastix
  bug #1435.
  SVN Rev[4754]

* Wed Feb 27 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: recordings module, help section was updated.
  SVN Rev[4743]

* Wed Feb 27 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: festival module, help section was updated.
  SVN Rev[4742]

* Wed Feb 27 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: text_to_wav module, help section was updated.
  SVN Rev[4740]

* Wed Feb 27 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: conference module, help section was updated.
  SVN Rev[4739]

* Wed Feb 27 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: file_editor module, help section was updated.
  SVN Rev[4738]

* Tue Feb 26 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: asterisk_cli module, help section was updated.
  SVN Rev[4734]

* Tue Feb 26 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: conference module, help section was updated.
  SVN Rev[4733]

* Mon Feb 25 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: extensions_batch module, help section was updated.
  SVN Rev[4730]

* Sat Feb 23 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: endpoints_batch module, help section was updated.
  SVN Rev[4729]

* Sat Feb 23 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: endpoint_configurator module, help section was updated.
  SVN Rev[4728]

* Fri Feb 22 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: monitoring module, help section was updated.
  SVN Rev[4727]

* Wed Feb 20 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: voicemail module, help section was updated.
  SVN Rev[4726]

* Wed Feb 20 2013 Jose Briones <jbriones@palosanto.com>
- UPDATED: pbxadmin module, help section was updated.
  SVN Rev[4724]

* Mon Feb 18 2013 German Macas <gmacas@palosanto.com>
- ADD: modules: endpoint_configurator: Add suppor to set new model Snom m9
  SVN Rev[4692]

* Fri Feb 08 2013 German Macas <gmacas@palosanto.com>
- ADD: modules: endpoint_configurator: Add support to set new model Snom 821
  SVN Rev[4664]

* Wed Feb 06 2013 German Macas <gmacas@palosanto.com>
- ADD: modules: endpoint_configurator: Add support to set new Fanvil models
  C56/C56P C58/C58P and C60
  SVN Rev[4661]

* Thu Jan 31 2013 German Macas <gmacas@palosanto.com>
- ADD: modules: endpoint_configurator: Add support to set new Yealink model
  SIP-T38G and automatic provision in VP530 model
  SVN Rev[4659]

* Thu Jan 31 2013 Luis Abarca <labarca@palosanto.com>
- REMOVED: pbx - modules/index.php: It were removed innecesary information when
  Festival is activated.
  SVN Rev[4652]

* Tue Jan 29 2013 Luis Abarca <labarca@palosanto.com> 2.4.0-1
- CHANGED: pbx - Build/elastix-pbx.spec: Changed Version and Release in 
  specfile according to the current branch.
  SVN Rev[4642]

* Mon Jan 28 2013 Luis Abarca <labarca@palosanto.com> 2.3.0-20
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4627]

* Thu Jan 24 2013 Rocio Mera <rmera@palosanto.com>
- CHANGED: Apps - PBX: In module Control_Planel was made changes in function
  showChannels in order to fix bugs in wich the call made through a sip trunk
  have not been displayed in control panel
  SVN Rev[4615]

* Wed Jan 16 2013 German Macas <gmacas@palosanto.com>
- CHANGE: modules - packages - festival -antispam: Change grid view and add
  option to Update packages in Package module - Fixed bug in StickyNote
  checkbox in festival and antispam modules
  SVN Rev[4588]

* Tue Jan 15 2013 Luis Abarca <labarca@palosanto.com> 2.3.0-19
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4586]

* Sat Jan 12 2013 Luis Abarca <labarca@palosanto.com>
- FIXED: The behavior of the checkbox in the sticky-notes its now normal,
  showing the checkbox instead of the ON-OFF slider button. Fixes Elastix BUG
  #1424 - item 3
  SVN Rev[4582]

* Sat Jan 12 2013 German Macas <gmacas@palosanto.com>
- CHANGE: modules - endpoint_configurator: Add support to set new Vendor
  Atlinks model Alcatel Temporis IP800 and fix Label Select a Model and
  Unselected in Endpoint Configurator grid
  SVN Rev[4581]

* Mon Jan 07 2013 German Macas <gmacas@palosanto.com>
- CHANGE: modules - endpoint_configurator - endpoints_batch: Add support to set
  new Vendors and models  Damall D3310 and Elastix LXP200.
  SVN Rev[4560]

* Thu Dec 27 2012 Sergio Broncano <sbroncano@palosanto.com>
- CHANGED: module extensions_batch, Secret field validation must be minimum 6
  alphanumeric characters, including upper and lowercase.
  SVN Rev[4532]

* Thu Dec 20 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: module endpoint configurator, default DTMF mode was audio, now default
  DTMF is RFC. Grandstream model GXV280. Ported to new endpoint configurator.
  SVN Rev[4528]

* Thu Dec 20 2012 Bruno Macias <bmacias@palosanto.com>
- FIXED: module endpoint configurator, default DTMF mode was audio, now default
  DTMF is RFC. Grandstream model GXV280.
  SVN Rev[4527]

* Fri Dec 14 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Elastix Operator Panel: assign dummy logger to silence logging spam on
  httpd error logfile. Fixes Elastix bug #1426.
  SVN Rev[4512]

* Tue Dec 11 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Batch of Extensions: if individual extensions list a blank context, 
  assume from-internal. Fixes Elastix bug #854.
  SVN Rev[4509]

* Tue Dec 04 2012 German Macas <gmacas@palosanto.com>
- CHANGED: modules - file_editor - sec_weak_keys: Fixed item 4 and 5 from bug
  1416, keep search filter in file_editor and change Reason for Status in
  sec_weak_keys.
  SVN Rev[4503]

* Tue Dec 04 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-18
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4494]

* Mon Dec 03 2012 German Macas <gmacas@palosanto.com>
- CHANGE: modules - endpoint_configurator: Add Support to set new model Escene
  620 and Fixed bug in Fanvil vendor
  SVN Rev[4492]

* Fri Nov 30 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Text to Wav: change operation mode of module. Now the module will
  stream the output of text2wave directly without creating a downloadable file
  in a web directory. This removes one requirement for a web directory that is
  both readable and writable by the httpd user.
  SVN Rev[4486] 

* Thu Nov 29 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Festival: fix iButton setup so that it runs directly from $.ready
  instead of $.change. Fixes part 1 of Elastix bug #1416.
  SVN Rev[4476]

* Thu Nov 29 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Festival: fix iButton setup so that it runs directly from $.ready
  instead of $.change. Fixes part 1 of Elastix bug #1416.
  SVN Rev[4475]

* Fri Nov 23 2012 German Macas <gmacas@palosanto.com>
- FIXED: modules - extensions_batch: Bug 1117, set disable voicemail from csv
  file.
  SVN Rev[4456]

* Wed Nov 21 2012 German Macas <gmacas@palosanto.com>
- ADD: modules - endpoint_configurator: Add support to set new model Fanvil C62
  and fix validation in vendor Atcom.cfg
  SVN Rev[4446]

* Mon Nov 19 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-17
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4443]

* Thu Nov  1 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Batch of Extensions: replace brittle regexp parsing of voicemail.conf
  and repeated invocation of grep with a single load. The rewritten loading of
  voicemail.conf is also more robust in the face of missing/additional/reordered
  key/value pairs in vm_options. Fixes Elastix bug #1117.
  SVN Rev[4401]

* Thu Oct 18 2012 Luis Abarca <labarca@palosanto.com>
- FIXED: pbx - Build/elastix-pbx.spec: For correct behavior of rmdir we have to
  erase all folders that exists inside the dir in order to erase it.
  SVN Rev[4365]

* Wed Oct 17 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-16
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4350]

* Wed Oct 17 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- Framework,Modules: remove temporary file preversion_MODULE.info under 
  /usr/share/elastix/module_installer/MODULE_VERSION/ which otherwise prevents
  proper cleanup of /usr/share/elastix/module_installer/MODULE_VERSION/ on 
  RPM update. Part of the fix for Elastix bug #1398.
- Framework,Modules: switch as many files and directories as possible under
  /var/www/html to root.root instead of asterisk.asterisk. Partial fix for 
  Elastix bug #1399.
- Framework,Modules: clean up specfiles by removing directories under 
  /usr/share/elastix/module_installer/MODULE_VERSION/setup/ that wind up empty
  because all of their files get moved to other places.
- Endpoint Configurator: install new configurator properly instead of leaving
  it at module_installer/MODULE/setup
  SVN Rev[4347]

* Mon Oct 15 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Endpoint Configurator: allow listmacip to be interrupted via a 
  signal in order to implement cancellation of runaway network scans.
  SVN Rev[4341] 

* Fri Sep 21 2012 Sergio Broncano <sbroncano@palosanto.com>
- CHANGED: MODULE - PBX/EXTENSION_BATCH: Password at least 6 characters, and
  query parameters for downloading extensions.
  SVN Rev[4240]

* Fri Sep 13 2012 Sergio Broncano <sbroncano@palosanto.com>
- CHANGED: MODULE - PBX/EXTENSION_BATCH: Query parameters to download the file
  .csv
  SVN Rev[4202]

* Mon Sep 10 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Control Panel: fix failure to update interface after user opens browser
  tab to different Elastix module while keeping Control Panel open.
  SVN Rev[4194]
- CHANGED: Endpoint Configurator: revert emergency commit (again). Now with a
  fat warning to update elastix-system instead.
  SVN Rev[4193]
- CHANGED: Port changes to Grandstream configurator for batch configuration to
  new parallel implementation.
  SVN Rev[4192]

* Fri Sep 07 2012 Sergio Broncano <sbroncano@palosanto.com>
- ADD: Module Endpoint Configurator, Endpoints Batch, Added support for phones
  Grandstream models GXP2100, GXP1405.
  SVN Rev[4191]

* Fri Sep 07 2012 Sergio Broncano <sbroncano@palosanto.com>
- ADD: Module Endpoint Configurator, Endpoints Batch, Added support for phones
  Grandstream models GXP2100, GXP1405, GXP2120.
  SVN Rev[4187]

* Mon Sep 03 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Endpoint Configurator: fill-out implementation of Sangoma Vega
  endpoint. Copy completed implementation to trunk.
  SVN Rev[4181]

* Mon Sep 03 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-15
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4179]

* Mon Sep 03 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Batch of Endpoints: reimplement CSV download to take into account all of 
  the endpoints that were configured via Endpoint Configurator and therefore have no 
  parameters as inserted by Batch of Endpoints. Fixes Elastix bug #1360.
  SVN Rev[4175]

* Mon Sep 03 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Endpoint Configurator: revert emergency commit. The problem that was fixed 
  in this commit should no longer occur with the Prereq: elastix-system >= 2.3.0-10 
  that fixed Elastix bug #1358.
  SVN Rev[4174]

* Sun Sep 02 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- ADDED: Endpoint Configurator: new endpoint class Sangoma, partial implementation.
  SVN Rev[4173]

* Fri Aug 31 2012 Alex Villacis Lasso <a_villacis@palosanto.com> 2.3.0-14
- FIXED: Prereq: elastix-system >= 2.3.0-10. Fixes Elastix bug #1358.
  SVN Rev[4164]

* Fri Aug 31 2012 German Macas <gmacas@palosanto.com>
- FIXED: modules -control_panel : Reset counter in queues when there are not calls.
  SVN Rev[4162]

* Thu Aug 23 2012 Bruno Macias <bmacias@palosanto.com>
- FIXED: modules - endpoint_configurator: network() function was changed, paloSantoNetwork invoke bad format.
  SVN Rev[4160]

* Thu Aug 23 2012 Alberto Santos <asantos@palosanto.com> 2.3.0-13
- CHANGED: module voipprovider, added spanish translation to an
  informative message
  SVN Rev[4117]
- CHANGED: module voipprovider, this module was removed from core.
  An informative message is added to indicate to the user that this
  is now an Addon.
  SVN Rev[4116]
- ADDED: added new agi script called hangup.agi that is executed in
  file extensions_override_elastix.conf. This agi intends to be an
  intermediary between addons scripts that needs information about a
  call as soon as it is hang up. This addons_scripts must be in path
  /usr/local/elastix/addons_scripts 
  SVN Rev[4114]
- CHANGED: Module Batch of Extensions: By downloading the csv file
  batch of Extensions reflects the Record Incoming and Record Outgoing
  ("Adhoc") as "On Demand".
  SVN Rev[4112]
- CHANGED: Menu.xml: The Level 2 module named "Endpoints", now called
  "Batch Configurations".
  CHANGED: Module Endpoint Configurator: The warning message that shows
  before discovering the endpoints on the network.
  ADD: Module Endpoints Batch: Download the current endpoints in CSV format
  CHANGED: Module Batch of Extensions: Upload the CSV with multiple subnets
  separated by "&" in the "Denny" and "Permit".
  CHANGED: Module Batch of Extensions: The parameters "IMAP Username" and
  "IMAP Password" is not shown in the "VM Options".
  CHANGED: Module Batch of Extensions: By downloading the csv file batch
  of Extensions reflects the Record Incoming and Record Outgoing ("Adhoc")
  as "On Demand".
  CHANGED: Module Batch of Extensions: Field "Secret" must have minimum 8
  alphanumeric characters, case sensitive.
  SVN Rev[4111]
- FIXED: modules - antispam - festival - sec_advanced_setting - remote_smtp:
  Fixed graphic bug in ON/OFF Button
  SVN Rev[4101]
- CHANGED: module pbx, deleted tables and queries related to voipprovider
  SVN Rev[4090]
- Fixed bug 0001318, bug 0001338: fixed in Asterisk File Editor return last
  query in Back link, fixed Popups, position and design, add in Dashboard
  Applet Admin option to check all
  SVN Rev[4088]
- Add Mac and application form to Set Sangoma Vega Gateway
  SVN Rev[4084]

* Fri Jul 20 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- ADDED: Endpoint Configurator: add new command-line utility.
  This new utility runs from /usr/bin/elastix-endpoint-configure. The program
  aims to introduce a new architecture for endpoint configuration, with better
  encapsulation of vendor-specific operations, and with an emphasis on parallel
  configuration of multiple endpoints for speed. The ultimate goal is to enable 
  the quick configuration of hundreds of phones at once.

* Wed Jul 18 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- ADDED: Endpoint Configurator: add SQL for vendor, MAC and model for Zultys.
  MAC range taken from http://www.base64online.com/mac_address.php?mac=00:0B:EA

* Tue Jul 17 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Configurator: for Cisco phones, syncinfo.xml must contain 
  <SYNCINFO> and </SYNCINFO> tags, else Cisco phone will not reboot.
  SVN Rev[4065]

* Tue Jul 03 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Batch: Properly figure out network mask for local network 
  instead of hardcoding a /24 network mask. SVN Rev[4037]

* Fri Jun 29 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-12
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.

* Fri Jun 29 2012 German Macas <gmacas@palosanto.com>
- ADDED: module - endpoints_batch: image file_csv.jpg for help of module.
  SVN Rev[4029]

* Thu Jun 28 2012 Luis Abarca <labarca@palosanto.com> 2.3.0-11
- CHANGED: pbx - Build/elastix-pbx.spec: update specfile with latest
  SVN history. Changed release in specfile.
  SVN Rev[4025]

* Thu Jun 28 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Configurator: Remove stray print_r.
  SVN Rev[4018]
  
* Wed Jun 27 2012 German Macas <gmacas@palosanto.com>
- CHANGED : modules - endpoint_configurator: Add function and sql statement to 
  set the new model Yealink VP530 from Endpoint Configurator.
  SVN Rev[4014]

* Tue Jun 26 2012 Sergio Broncano <sbroncano@palosanto.com>
- ADDED: Module endpoints_batch, copy from trunk revision
  SVN Rev[4013]

* Mon Jun 25 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Conference: Remove XSS vulnerability.
  SVN Rev[4012]

* Tue Jun 19 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- CHANGED: Endpoint Configurator: Reimplement Grandstream configuration encoder
  as a pure PHP method. This allows the package to drop the Java-based encoder,
  which in turn allows the package to drop the openfire dependency.
- CHANGED: Endpoint Configurator: modify listmacip so that it can stream output
  from nmap as it is generated.
  SVN Rev[4009]

* Tue Jun 12 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Endpoint Configurator: Properly figure out network mask for local 
  network instead of hardcoding a /24 network mask. SVN Rev[3993]
- FIXED: Endpoint Configurator: Relax pattern matching in listmacip script to
  account for differences in output format in nmap from CentOS to Fedora 17.
  SVN Rev[3992]
- FIXED: Endpoint Configurator: Use ip addr show instead of ifconfig to get
  size of network mask for endpoint scan. Required for compatibility with 
  Fedora 17.
  SVN Rev[3989]

* Mon Jun 11 2012 Sergio Broncano <sbroncano@palosanto.com>
- ADD: MODULE endpoints_batch, Parent menu is created second level called "Endpoints". 
  with their respective classification Batch of Extensions, Endpoint Configurator become 
  the third-level menu, menu is also added a third level called Batch Enpoints enabling 
  mass configuration enpoints so fast, taking as input: subnet where the endpoints are 
  connected and a file (. csv) file that contains configuration parameters such as 
  (Vendor, Model, MAC, Ext, IP, Mask, GW, DNS1, DNS2, Bridge, Time Zone).
  SVN Rev[3985]

* Thu Jun 7 2012 Alberto Santos <asantos@palosanto.com>
- NEW: new rest resource in pbxadmin to make calls.
  SVN Rev[3971]

* Tue Jun 05 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: installer.php: stop leaving temporary file /tmp/trunk_dump.sql around 
  after install or update.
- FIXED: installer.php: stop leaving temporary file /var/www/db/trunk-pbx.db
  around on most install/update scenarios.
  SVN Rev[3959] 

* Mon Jun 04 2012 Alex Villacis Lasso <a_villacis@palosanto.com> 2.3.0-10
- FIXED: Changed specfile so that several files are explicitly set as 
  executable. Fixes Elastix bugs #1291, #1292.

* Fri Jun 01 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: On-demand recording must not use MIXMON_FORMAT. The format for
  recording is TOUCH_MONITOR_FORMAT, if defined, or wav if not defined.
- CHANGED: Use ASTSPOOLDIR instead of hardcoded /var/spool/asterisk.

* Mon May 28 2012 Sergio Broncano <sbroncano@palosanto.com> 2.3.0-9
- CHANGED: MODULES - PBX/EXTENSION_BATCH: The following fields were added 
  callgroup, pickupgroup, disallow, allow, deny, permit, Record Incoming, 
  Outgoing Record in extensiones.csv file to upload and download. 
  SVN Rev[3940]

* Mon May 07 2012 Rocio Mera <rmera@palosanto.com> 2.3.0-8
- UPDATED: UPDATED in specfile to release 8

* Thu May 03 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Conference: Check the context variable MEETME_ACTUAL_RECORDINGFILE 
  alongside MEETME_RECORDINGFILE in order to decide whether a MeetMe recording
  exists. Before this check, CBMySQL conferences end up marking a recording as
  available in Monitoring report when no recording actually exists.
  FIXED: Conference: Check that MEETME_ACTUAL_RECORDINGFILE with MIXMON_FORMAT
  extension exists. If not, fallback to assuming .wav as file extension. Before
  this check, CBMySQL conference recordings are not downloadable if
  MIXMON_FORMAT is something other than .wav .
  SVN Rev[3926].

* Wed May 02 2012 Rocio Mera <rmera@palosanto> 2.3.0-7
- CHANGED: In spec file, changed prereq elastix-framework >= 2.3.0-9

* Wed May 02 2012 Alex Villacis Lasso <a_villacis@palosanto.com>
- FIXED: Conference: Rework several conference manipulation functions so that
  they use SQL parameters. Fixes Elastix bug #1256.
  FIXED: Conference: Reorder evaluation of actions so that kicking and muting
  participants actually works. Fixes Elastix bug #1245.
  SVN Rev[3916].
- FIXED: Conference: Validation of type "integer" for HH:MM is unimplemented.
  Use "numeric" instead.
  SVN Rev[3914].

* Fri Apr 27 2012 Rocio Mera <rmera@palosanto.com> 2.3.0-6
- CHANGED: Addons - Build/elastix-addons.spec: update specfile with latest
  SVN history. Changed release in specfile
- FIXED: Monitoring: queue recording file names are written with full absolute
  path in DB, so a LIKE operator is required to select on the file name.
  Rewrite recording file download to add more checks. Part of fix for Elastix
  bug #1225.
  SVN Rev[3873]
- FIXED: Batch of Extensions: voicemail password (if any) should be
  numeric-only. Part of the fix for Elastix bug #1238.
  SVN Rev[3871]
- FIXED: PBX Admin: add enough of the FreePBX validation javascripts so that
  field validations work. Part of the fix for Elastix bug #1238.
  SVN Rev[3870]
- ADDED: Build - SPEC's: The spec files were added to the corresponding modules
  and the framework.
  SVN Rev[3854]
  SVN Rev[3836]
- FIXED: PBX - Festival: Fixed problem when chance status to festival. Bug 1219
  SVN Rev[3814]

* Mon Apr 02 2012 Rocio Mera <rmera@palosanto.com> 2.3.0-5
- FIXED: PBX - Festival: Fixed problem when chance status to festival. Bug 1219
  SVN Rev[3814]

* Fri Mar 30 2012 Bruno Macias <bmacias@palosanto.com> 2.3.0-4
- CHANGED: In spec file, changed prereq elastix-framework >= 2.3.0-5
- CHANGED: Control Panel: sqlite query reports SELECT X.COLUMN as 'X.COLUMN' in
  CentOS and 'COLUMN' in Fedora. Query needs to explicitly set the column name
  and perform conversion to the expected format.
  SVN Rev[3806]
- FIXED: modules - SQLs DB: se quita SQL redundante de alter table y nuevos 
  registros, esto causaba un error leve en la instalación de el/los modulos.
  SVN Rev[3797]

* Mon Mar 26 2012 Rocio Mera <rmera@palosanto.com> 2.3.0-3
- CHANGED: In spec file, changed prereq elastix-framework >= 2.3.0-3
- CHANGED: In spec file, changed prereq freePBX >= 2.8.1-12
- CHANGED: modules/control_panel: Se define auto como propiedad de altura a las
  areas.
  SVN Rev[3779]
- CHANGED: PBX - Monitoring little change in index.php to fix problem appear
  the 'X' option in whose filters that are always active
  SVN Rev[3757]
- CHANGED: PBX - Voicemail index.php change in index.php to fix problem
  coulnd't be the voicemail in the elastix web interface
  SVN Rev[3756]

* Fri Mar 09 2012 Alberto Santos <asantos@palosanto.com> 2.3.0-2
- CHANGED: In spec file, changed prereq elastix-framework >= 2.3.0-2
- CHANGED: PBX Admin: bail out if unable to connect to Asterisk AMI.
  SVN Rev[3727]

* Wed Mar 07 2012 Rocio Mera <rmera@palosanto.com> 2.3.0-1
- CHANGED: In spec file, changed prereq elastix-framework >= 2.3.0-1
- FIXED: modules - faxlist: Se corrige bug de pagineo en el modulo de faxlist.
  Tambien se definen correctamente ciertas traducciones.
  SVN Rev[3714]
- CHANGED: voipprovider index.php add control to applied filters
  SVN Rev[3706]
- CHANGED: file_editor index.php add control to applied filters
  SVN Rev[3705]
- CHANGED: conference index.php add control to applied filters
  SVN Rev[3704]
- CHANGED: voicemail index.php add control to applied filters
  SVN Rev[3703]
- CHANGED: voicemail index.php add control to applied filters
  SVN Rev[3702]
- CHANGED: endpoint_configurator index.php change to put new function outside
  of filter
  SVN Rev[3685]
- FIXED: Conference: honor new parameter isUserAdministratorGroup in
  listConferences(). Requires elastix-conferenceroom >= 2.0.0.
  SVN Rev[3680]
- FIXED: PBX - Monitoring: sometimes blind transfer results in two or more CDRs
  with the same uniqueid. When recording calls, it is necessary to specify the
  distinct call filename in order to have access to all portions of the
  recording.
  SVN Rev[3678]
- UPDATED: modules - hardware_detector: Se define ancho de la tabla que formar
  parte de un puerto, en chrome se mostraba mal los puertos.
  SVN Rev[3663]
- CHANGED: pbx control_panel Now the max numbers of columns is 4, modifcations
  in index.php. Add the file 3_2.2.0-26_2.2.0-27.sql in db/update to change
  take efect in updating
  SVN Rev[3651]
- CHANGED: little change in file *.tpl to better the appearance the options
  inside the filter
  SVN Rev[3639]
- CHANGED: modules - extension_batch/themes: The incorrect positioning of
  Dowload link is now corrected.
  SVN Rev[3631]
- FIXED: Modules - Monitoring: Bugs about cannot listen on the web in
  google-crone the recording
  * Bug:0001085
  * Introduced by:
  * Since: Development Monitoring Module
  SVN Rev[3630]
- FIXED: Modules - Monitoring: Bugs about cannot listen on the web the
  recording
  * Bug:0001085
  * Introduced by:
  SVN Rev[3629]


* Wed Feb 1 2012 Rocio Mera <rmera@palosanto.com> 2.2.0-26
- CHANGED: In spec file, changed prereq elastix-framework >= 2.2.0-30
- CHANGED: file index.php to fixed the problem with the paged 
  to show callers of conference. SVN Rev[3623].
- CHANGED: file index.php to fixed the problem with the paged
  SVN Rev[3620].
- CHANGED: file index.php to fixed the problem with the paged.
  SVN Rev[3617]. SVN Rev[3616]. SVN Rev[3610]. 

* Mon Jan 30 2012 Alberto Santos <asantos@palosanto.com> 2.2.0-25
- CHANGED: In spec file, changed prereq elastix-framework >= 2.2.0-29
- CHANGED: Changed the word 'Apply Filter' by 'More Option'
  SVN Rev[3601]

* Sat Jan 28 2012 Rocio Mera <rmera@palosanto.com> 2.2.0-24
- CHANGED: In spec file, changed prereq elastix-framework >= 2.2.0-28
- CHANGED: Added support for the new grid design. SVN Rev[3576].
- CHANGED: modules - images: icon image title was changed on some 
  modules. SVN Rev[3572].
- CHANGED: modules - trunk/core/pbx/modules/monitoring/index.php: 
  Se modifico los archivos index.php para corregir problema con 
  botondeleted. SVN Rev[3570]. SVN Rev[3568].
- CHANGED: modules - icons: Se cambio de algunos módulos los iconos
  que los representaba. SVN Rev[3563].
- CHANGED: modules - * : Cambios en ciertos mòdulos que usan grilla 
  para mostrar ciertas opciones fuera del filtro, esto debido al 
  diseño del nuevo filtro. SVN Rev[3549].
- CHANGED: Modules - PBX: Added support for the new grid layout.
  SVN Rev[3548].
- UPDATED: modules - *.tpl: Se elimino en los archivos .tpl de 
  ciertos módulos que tenian una tabla demás en su diseño de filtro
  que formaba parte de la grilla. SVN Rev[3541].


* Thu Jan 12 2012 Alberto Santos <asantos@palosanto.com> 2.2.0-23
- ADDED: In spec file, added prereq asterisk >= 1.8
- CHANGED: In spec file, changed prereq elastix-system >= 2.2.0-18
- CHANGED: In spec file, changed prereq freePBX >= 2.8.1-11
- FIXED: modules control_panel, when the button reload is pressed
  all the boxes are displayed twice. This is fixed by doing an
  element.empty().append() where element is the container.
  FIXED: modules control_panel, the destination call was not
  displayed and when the page is refreshed all the times are reset
  to 3. This bug happens due to the migration to asterisk 1.8 where
  the command "core show channels concise" shows in different
  positions the time and destination of the call.
  SVN Rev[3524]
- CHANGED: modules endpoint_configurator, the VoIP server address
  is now the network that belongs to the endpoint's network address
  SVN Rev[3523]
- CHANGED: modules endpoint_configurator, now the network
  configuration is not changed in atcom telephones
  SVN Rev[3511]
- ADDED: added new update script for enpoint.db database, this
  scripts adds new atcom models "AT610" and "AT640" also changes
  old atcom model names to "AT620", "AT530" and "AT320"
  SVN Rev[3508]
- ADDED: modules endpoint_configurator, added new atcom models
  "AT610" and "AT640" also changed the name of old atcom models
  to "AT320", "AT530" and "AT620"
  SVN Rev[3507]

* Tue Jan 03 2012 Alberto Santos <asantos@palosanto.com> 2.2.0-22
- CHANGED: modules - pbx/setup/db: Schema de instalación de la
  base meetme, fue modificado para que no asigne una contraseña
  al definir el GRANT de permisos a la base meetme que sea
  administrable por el usuario asteriskuser
  SVN Rev[3499]

* Fri Dec 30 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-21
- CHANGED: In spec file, removed the creation of user asterisk,
  that is handled by elastix-framework

* Thu Dec 29 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-20
- CHANGED: In spec file, changed prereq elastix-framework >= 2.2.0-24
- CHANGED: In spec file, now in this spec is handled everything related
  with asterisk and not any more on framework
- CHANGED: changed everything to do with asterisk from the framework
  to elastix-pbx
  SVN Rev[3495]

* Tue Dec 20 2011 Eduardo Cueva <ecueva@palosanto.com> 2.2.0-19
- CHANGED: In spec file, changed prereq to elastix-framework >= 2.2.0-23
- FIXED: When export a csv file extensions, not export well voicemails fields, 
  the problem was because the path was not sent to find if the extension had 
  a voicemail active.. SVN Rev[3458]

* Thu Dec 08 2011 Eduardo Cueva <ecueva@palosanto.com> 2.2.0-18
- CHANGED: In spec file, changed prereq to elastix-framework >= 2.2.0-21
- FIXED: Festival: Use 'pidof' instead of 'service festival status' 
  to work around https://bugzilla.redhat.com/show_bug.cgi?id=684881
  SVN Rev[3431]

* Fri Nov 25 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-17
- CHANGED: In spec file, changed prereq to elastix-framework >= 2.2.0-18
- CHANGED: Recordings: use load_language_module instead of handcoding
  i18n loading
  FIXED: Recordings: fixed forgotten i18n string change in
  Spanish translation
  SVN Rev[3399]
- FIXED: module festival, informative message was only displayed
  for theme elastixneo. Now it is displayed for all the themes
  SVN Rev[3393]
- CHANGED: Festival: use privileged script 'festival' to reimplement
  festival server activation
  SVN Rev[3392]
- CHANGED: Festival: no need to remove festival service from chkconfig.
  SVN Rev[3391]
- CHANGED: Festival: check for non-existent festival.scm file
  SVN Rev[3390]
- ADDED: Festival: introduce new privileged script 'festival' to
  enable/disable Festival and to add required configuration.
  SVN Rev[3389]
- CHANGED: Festival: sudo is not required for querying festival
  server status
  SVN Rev[3388]
- FIXED: PBX Admin: freePBX modules always need type=setup defined,
  so define if display is not defined
  SVN Rev[3387]
- FIXED: PBX Admin: all freePBX module links need a type=setup
  GET parameter. Partially fixes PHP Notice:  Undefined index:
  1 in /var/www/html/admin/modules/fax/functions.inc.php on line 389
  SVN Rev[3386]
- FIXED: PBX Admin: assign instead of concatenate to $htmlFPBX.
  Fixes PHP Notice:  Undefined variable: htmlFPBX in
  /var/www/html/modules/pbxadmin/libs/contentFreePBX.php on line 492
  SVN Rev[3385]
- FIXED: PBX Admin: $amp_conf_defaults must be declared as global
  BEFORE admin/functions.inc.php, fixes PHP Warning:  Invalid
  argument supplied for foreach() in /var/www/html/admin/functions.inc.php
  on line 782
  SVN Rev[3384]
- CHANGED: Endpoint Configurator: use privileged script 'listmacip'
  to reimplement endpoint mapping
  SVN Rev[3382]
- CHANGED: Endpoint Configurator: privileged script 'listmacip'
  needs to report netcard vendor description too.
  SVN Rev[3381]
- ADDED: Endpoint Configurator: introduce new privileged script
 'listmacip' to map out available IPs and MACs in a network.
  This removes the need to allow full access to nmap via sudo.
  SVN Rev[3380]
- CHANGED: Endpoint Configurator: remove no-longer-necessary
  sudo chmod around invocation of encoder for GrandStream configurator.
  SVN Rev[3379]

* Wed Nov 23 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-16
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-17
- FIXED: module voicemail, wrong concatenation of variable 
  $contenidoModulo, consecuence of this the filter is showed twice
  SVN Rev[3353]

* Tue Nov 22 2011 Eduardo Cueva <ecueva@palosanto.com> 2.2.0-15
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-15
- FIXED: Voicemail: remove nested <form> tag. SVN Rev[3270]
- CHANGED: module endpoint_configurator, extensions showed 
  in field "Current Extension" are unregistered when the 
  button set is pressed. SVN Rev[3267]
- CHANGED: module endpoint_configurator, changed width and 
  align in input for discovering endpoints. SVN Rev[3263]

* Tue Nov 01 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-14
- CHANGED: In spec file, changed prereq freePBX >= 2.8.1-7
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-14
- CHANGED: module pbxadmin, was increased the width of warning
  message in option "Unembedded FreePBX"
  SVN Rev[3249]

* Sat Oct 29 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-13
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-13

* Sat Oct 29 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-12
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-12
- CHANGED: module pbxadmin, added a margin-top negative to the
  informative message in Unembedded FreePBX
  SVN Rev[3229]
- CHANGED: module control_panel, added a border-radius to the style
  SVN Rev[3228]
- CHANGED: module voipprovider, changed the color of fieldset border and title
  SVN Rev[3199]
- FIXED: module festival, messages was not displaying for theme elastixneo
  SVN Rev[3185]
- CHANGED: module voipprovider, the module title is now handled by the framework
  SVN Rev[3162]
- CHANGED: module recordings, the module title is now handled by the framework
  SVN Rev[3160]
- CHANGED: module text_to_wav, the module title is now handled by the framework
  SVN Rev[3158]
- CHANGED: module file_editor, the module title is now handled by the framework
  SVN Rev[3157]
- CHANGED: module asterisk_cli, the module title is now handled by the framework
  SVN Rev[3155]
- CHANGED: module extensions_batch, the module title is now handled by the framework
  SVN Rev[3153]
- CHANGED: module conference, the module title is now handled by the framework
  SVN Rev[3151]
- CHANGED: module voicemail, the module title is now handled by the framework
  SVN Rev[3150]
- CHANGED: module pbxadmin, changed the module title to "PBX Configuration"
  SVN Rev[3149]
- CHANGED: module pbxadmin, added a title to the module pbxadmin
  SVN Rev[3147]

* Mon Oct 17 2011 Eduardo Cueva <ecueva@palosanto.com> 2.2.0-11
- CHANGED: module endpoint_configurator, when a patton does not 
  have 2 ethernet ports, the WAN options are not displayed.
  SVN Rev[3087]
- CHANGED: module recordings, added information. SVN Rev[3082]

* Thu Oct 13 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-10
- CHANGED: module endpoint_configurator, added asterisks in some
  required fields
  SVN Rev[3081]
- CHANGED: module endpoint_configurator, in case an error occurs
  and a file can not be created, a message is showed
  SVN Rev[3078]

* Fri Oct 07 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-9
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-8
- FIXED: module conference, added an id of "filter_value" to the
  filter text box
  SVN Rev[3035]

* Wed Sep 28 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-8
- FIXED: module extensions_batch, wrong name of button, changed
  "CVS" to "CSV"
  SVN Rev[3006]
- FIXED: module extensions_batch, only if the field "Direct DID"
  is entered, an inbound route is created
  SVN Rev[3005]

* Tue Sep 27 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-7
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-5
- CHANGED: changed the password "elastix456" of AMI to the
  password set in /etc/elastix.conf
  SVN Rev[2995]

* Thu Sep 22 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-6
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-4
- ADDED: module endpoint_configurator, added the option for
  patton configuration
  SVN Rev[2985]
- ADDED: added script sql for database endpoint, it creates 
  a new table called settings_by_country and added the vendor Patton
  SVN Rev[2984]
- CHANGED: Conference: add new method required for verification 
  of date range. Part of fix for Elastix bug #937.
  SVN Rev[2983]
- FIXED: Embedded FreePBX: include jquery.toggleval if available,
  to fix some javascript errors.
  SVN Rev[2981]
- FIXED: Elastix Operator Panel: IE6 through IE8 deal incorrectly
  with nested draggables, as detailed in http://bugs.jqueryui.com/ticket/4333.
  Applied workaround suggested in bug report.
  SVN Rev[2980]
- FIXED: Elastix Operator Panel: fix incorrect regular expression 
  that missed extension names with dashes.
  SVN Rev[2979]
- CHANGED: Elastix Operator Panel: remove comment and trailing comma
  that trigger syntax error in IE6. Part of fix for Elastix bug #938.
  SVN Rev[2978]
- CHANGED: Elastix Operator Panel: use jQuery methods instead of
  innerHTML to insert table information. Part of fix for Elastix bug #938.
  SVN Rev[2977]
- CHANGED: Elastix Operator Panel: use DOM instead of innerHTML
  to insert loading animation. Part of fix for Elastix bug #938.
  SVN Rev[2976]
- FIXED: Control Panel: check for support of DOMParser and fall back
  to IE-specific code if not supported. Partial fix for Elastix bug #938.
  SVN Rev[2971]
- CHANGED: module text_to_wav, deleted unnecessary asterisks
  SVN Rev[2962]
- CHANGED: module extensions_batch, deleted unnecessary asterisks
  SVN Rev[2961]
- CHANGED: module monitoring, deleted unnecessary asterisks
  SVN Rev[2960]
- CHANGED: module voicemail, deleted unnecessary asterisks
  SVN Rev[2959]
- FIXED: module recordings, variable $pDB and $filename were not defined
  SVN Rev[2957]
- CHANGED: module recordings, database address_book.db is not 
  used. Deleted any relation with that database
  SVN Rev[2954]

* Fri Sep 09 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-5
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-3
- CHANGED: module recordings, changed the location of module
  recordings, now it is in PBX->tools
  SVN Rev[2953]
- CHANGED: module conference, in view mode the asterisks and
  word required were removed
  SVN Rev[2951]
- FIXED: module endpoint_configurator, the version must have 4 decimals
  SVN Rev[2939]
- FIXED: module control_panel, word class is reserved in javascript
  for firefox >= 5. Changed the variable name to other one
  SVN Rev[2934]
- CHANGED: installer.php, deleted the register string of trunks
  created in voipprovider
  SVN Rev[2930]
- ADDED: added script sql for database control_panel_design.db,
  updated the description for the trunk area
  SVN Rev[2928]

* Tue Aug 30 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-4
- CHANGED: In spec file, verify the inclusion of
  sip_notify_custom_elastix.conf on /etc/asterisk/sip_notify_custom.conf
- CHANGED: installer.php, trunks created by provider_account were
  written in file /etc/asterisk/sip_custom.conf. Now when this
  script is executed these trunks are deleted from the mentioned
  file because now the voipprovider trunks are created in freePBX database
  SVN Rev[2925]

* Fri Aug 26 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-3
- CHANGED: In spec file, changed prereq elastix >= 2.2.0-2
- ADDED: In spec file, added prereq elastix-system >= 2.2.0-5
- CHANGED: PBX: Return a diagnostic message instead of exiting 
  when some FreePBX issue disables all modules.
  SVN Rev[2910]
- CHANGED: installer.php, the trunks created in voipprovider
  are also created in the database asterisk of freePBX
  SVN Rev[2890]
- FIXED: module monitoring, fixed many security holes in this module
  SVN Rev[2885]
- CHANGED: module voicemail, if user is not administrator and does
  not have an extension assigned only a message is showed
  SVN Rev[2883]

* Fri Aug 03 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-2
- FIXED: module control_panel, the queues was not showing the
  extension or agent which attends it. Now it shows all the
  extensions or agents that attent it
  SVN Rev[2873]

* Tue Aug 02 2011 Alberto Santos <asantos@palosanto.com> 2.2.0-1
- ADDED: In Spec file added requires festival >= 1.95
- FIXED: module festival, informative message was not displayed. 
  The error was fixed and now it is displayed
  SVN Rev[2863]

# el script de patton query debe moverse a /usr/share/elastix/priviliges en el spec
* Fri Jul 29 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-28
- CHANGED: in spec file changed prereq elastix >= 2.0.4-30
- ADDED: pbx setup/db, sql script to add iax support. SVN Rev[2842]
- ADDED: pbx setub, added the script that searchs for patton 
  devices. SVN Rev[2841]
- ADDED: module endpoint_configurator, added support iax 
  (on phones that support it), also added support to smartnodes.
  SVN Rev[2840]
- FIXED: extensions_override_elastix.conf, when the audio file 
  is not created the field userfield is set empty in the database
  SVN Rev[2821]
- FIXED: module monitoring, when user is not admin the filter 
  options dissapear. Now those options remains with any user.
  SVN Rev[2820]
- CHANGED: module festival, the button save was eliminated, now 
  when user press on or off automatically make the action. SVN Rev[2798]
- CHANGED: module voicemail, changed message when user does not 
  have an extension associated. SVN Rev[2794]
- CHANGED: module monitoring, changed message when a user does 
  not have an extension associated. SVN Rev[2793]
- CHANGED: module voicemail, when the user does not have an 
  extension associated, a link appear to assign one extension.
  SVN Rev[2790]
- CHANGED: module monitoring, The link here 
  (when a user does not have an extension) now open a new window to 
  edit the extension of the user logged in. SVN Rev[2788]
- ADDED: module extensions_batch, added iax2 support. SVN Rev[2774]

* Wed Jun 29 2011 Alberto Santos <asantos@palosanto.com> 2.0.4-27
- FIXED: module festival, added a sleep of 2 seconds when the service
  is started that is the maximum time delay. SVN Rev[2764]

* Mon Jun 13 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-26
- CHANGED: In spec file change prereq freepbx >= 2.8.1-1 and 
  elastix >= 2.0.4-24
- CHANGED: Modules - Trunk: The ereg function was replaced by the 
  preg_match function due to that the ereg function was deprecated 
  since PHP 5.3.0. SVN Rev[2688]
- FIXED: module festival, wrong informative message the file 
  modified is /usr/share/festival/festival.scm and not 
  /usr/share/elastix/elastix.scm. SVN Rev[2669]
- CHANGED: The split function of these modules was replaced by the 
  explode function due to that the split function was deprecated 
  since PHP 5.3.0. SVN Rev[2650]

* Wed May 18 2011 Alberto Santos <asantos@palosanto.com> 2.0.4-25
- CHANGED: change prereq of freePBX to 2.8.0-3

* Wed May 18 2011 Alberto Santos <asantos@palosanto.com> 2.0.4-24
- CHANGED: module pbxadmin, library contentFreePBX.php updated with 
  the last code in pbxadmin
  SVN Rev[2646]
- CHANGED: module pbxadmin, created a library that gets the content
  of freePBX modules
  SVN Rev[2645]
- FIXED: module voipprovider, when a trunk is created by voipprovider
  and then this one is deleted in freePBX, it is not deleted in the
  database of voipprovider. Now its deleted from the database of voipprovider
  SVN Rev[2640]
- ADDED: Conference: new Chinese translations for Conference interface.
  Part of fix for Elastix bug #876
  SVN Rev[2639]

* Thu May 12 2011 Alberto Santos <asantos@palosanto.com> 2.0.4-23
- CHANGED: renamed sql scripts 4 and 5 for updates in database endpoint
  SVN Rev[2638]
- FIXED: Endpoint Configurator: check that selected phone model is
  a supported model before using include_once on it.
  FIXED: Endpoint Configurator: check that MAC address for endpoint
  is valid.
  SVN Rev[2637]
- ADDED: module endpoint_configurator, disabled other accounts in
  YEALINK phones.
  SVN Rev[2635]
- FIXED: File Editor: undo use of <button> inside of <a> as this
  combination does not work as intended in Firefox 4.0.1. Related
  to Elastix bug #864
  SVN Rev[2632]
- FIXED: module pbxadmin, added a width of 330px to the informative
  message in "Unembedded freePBX"
  SVN Rev[2627]
- FIXED: module pbxadmin, the option "Unembedded freePBX" was placed
  at the end of the list, also a warning message was placed on it.
  SVN Rev[2626]

* Thu May 05 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-22
- FIXED:    module pbxadmin, IVR did not displayed extensions, 
  conferences, trunks, etc. Now that information is displayed 
  according to the option selected in the combo box. SVN Rev[2620]
- CHANGED:  PBX - monitoring: Changed  value of 
  $arrConfModule['module_name'] = 'monitoring2' to 
  $arrConfModule['module_name'] = 'monitoring' in default.conf.php
  SVN Rev[2591]

* Tue Apr 26 2011 Alberto Santos <asantos@palosanto.com> 2.0.4-21
- CHANGED: installer.php, changed installer.php in order to works for
  updates to elastix 2.0.4
  SVN Rev[2586]
- FIXED: module control_panel, added a validation in case there is no data
  SVN Rev[2585]
- ADDED: module festival, added folders lang, configs and help
  SVN Rev[2583]
- CHANGED: module voicemail, changed class name to core_Voicemail
  SVN Rev[2580]
- ADDED: added new provider called "Vozelia"
  SVN Rev[2574]
- CHANGED: provider vozelia was removed from the installation script
  SVN Rev[2573]
- CHANGED: module voicemail, changed name from puntosF_Voicemail.class.php
  to core.class.php
  SVN Rev[2571]
- UPDATED: module file editor, some changes with the styles of buttons
  SVN Rev[2561]
- NEW: new scenarios for SOAP in voicemail
  SVN Rev[2559]
- NEW: new module festival
  SVN Rev[2553]
- ADDED: added new module in tools called Festival
  SVN Rev[2552]
- NEW: service festival in /etc/init.d and asterisk file sip_notify_custom_elastix.conf
  SVN Rev[2551]
- CHANGED: In Spec file, moved the files festival and sip_notify_custom_elastix.conf

* Wed Apr 13 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-20
- FIXED: pbx - extension_batch: Removed download_csv.php, this file 
  was removed in commit 1550 but this file was put in this package 
  by error in the rpm version 2.0.4-19.
- ADDED: module endpoint_configurator, added the vendor LG-ERICSSON 
  and the model IP8802A. SVN Rev[2536][2537]
- CHANGED: module endpoint_configurator, changed model names for 
  phones Yealink. SVN Rev[2527][2529][2530]
- ADDED: module endpoint_configurator, added support for 
  phones Yealink models T20, T22, T26 and T28. SVN Rev[2518][2519]

* Tue Apr 04 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-19
- FIXED: module voipprovider, undefined data was set to the 
  combo box. Added a validation for default values in case of 
  an undefined data. SVN Rev[2507]

* Mon Apr 04 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-18
- FIXED: module control_panel, when the area is empty, a box 
  can not be dropped. Now it can. SVN Rev[2498]

* Thu Mar 31 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-17
- FIXED: Error to install databases of sqlite in "process of 
  installation" because in spec file when mysql is down this 
  event is sending to "first-boot" but only mysql scripts and 
  not sqlite.

* Thu Mar 31 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-16
- FIXED: Module Conference, database meetme, bad defintion sql 
  script was fixed. SVN Rev[2477]

* Tue Mar 29 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-15
- ADDED: module voicemail, added a new validation in case the 
  path file does not exist when writing the file voicemail.conf.
  SVN Rev[2469]

* Thu Mar 03 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-14
- CHANGED: module voipprovider, now the provider net2phone is 
  the first in the list of providers. SVN Rev[2391]
- ADDED:  file .sql to create a new column called orden in the 
  table provider of the database trunk.db also the orden field 
  was set for each provider. SVN Rev[2390]

* Tue Mar 01 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-13
- CHANGED: in Spec file change prereq elastix>=2.0.4-10
- ADDED: module control_panel, added a loading image until all 
  the boxes are loaded, also the info window was reduced. 
  SVN Rev[2385]
- CHANGED: module voipprovider, voipprovider now insert the 
  data in the database of freepbx and automatically reload 
  asterisk files. SVN Rev[2384]
- ADDED: database trunk, added a column called id_trunk in 
  table provider_account. SVN Rev[2382]
- FIXED: module voipprovider, the edit mode did not show the 
  data of the account. Now the data is showed. SVN REV[2380]
- FIXED: module voipprovider, fixed the problem of moving down 
  the peer settings options when the width of the browser is 
  smaller. SVN Rev[2378]
- ADDED: module file_editor, added a new button called 
  "Reload Asterisk" that applies the command module reload to 
  asterisk. SVN Rev[2376]
- CHANGED: module endpoint_configurator, added a message when 
  the files are configurated. SVN Rev[2373]
- CHANGED: module enpoint_configurator, changed the field status 
  to current extension which shows the extension to which is 
  registered the phone. SVN Rev[2371]
- FIXED:   Error to try to renove database meetme, change action 
  "drop table meetme" to "drop database meetme". SVN Rev[2365]
- CHANGED: module voipprovider, added a checkbox called advanced 
  that when is checked displays the PEER Setting options. 
  SVN Rev[2358]
- ADDED: module endpoint_configurator, added the configuration 
  for the vendor AudioCodes with models 310HD and 320HD. 
  SVN Rev[2356]
- FIXED: module control_panel, the extensions on the area 1,2 
  and 3 didnt show the status also when you call to a conference 
  or a number that is not an extension the call destiny didn't 
  display. All those problems were fixed. SVN Rev[2355]
- FIXED:  PBX - control Panel: Error in script.sql to update 
  control panel to the next version, The error was the script 
  try to update a table rate but it did not exit and the correct 
  table was area. SVN Rev[2344]

* Mon Feb 07 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-12
- CHANGED:  In Spec file add prerequiste elastix 2.0.4-9

* Mon Feb 07 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-11
- CHANGED:   In Spec add lines to support install or update
  proccess by script.sql.
- DELETED:   Databases sqlite were removed to use the new format 
  to sql script for administer process install, update and delete. 
  In Installer.php remove all instances of .db but the logic to 
  update the old versions of trunk.db is there. SVN Rev[2333]
- ADD:  PBX - setup: New schema organization to get better 
  performance to databases sqlite and mysql. SVN Rev[2328]
- CHANGED: Module conference, meetme database was merged, now
  sql script is 1_schema.sql. SVN Rev[2317]

* Thu Feb 03 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-10
- CHANGED:  menu.xml to support new tag "permissions" where has 
  all permissions of group per module and new attribute "desc" 
  into tag  "group" for add a description of group. 
  SVN Rev[2294][2299]
- CHANGED: module endpoint_configurator, eliminated a print_r.
  SVN Rev[2290]
- ADDED:    database endpoint, added model GXV3175 in the table 
  model. SVN Rev[2287]
- ADDED:    module endpoint_configurator, added model GXV3175. 
  SVN REV[2286]
- ADDED:    database control_panel_design.db, added a new area, 
  parking lots, and added a new column for the color of each 
  area. SVN Rev[2257]
- CHANGED:  module control_panel, new area for parking lots the 
  boxes are generated in the client side and the time counting 
  for the calls are made also in the client side. SVN Rev[2256]
- ADD:      database control_panel_design, added new data in 
  the tabla area for the conferences and the SIP/IAX Trunks. 
  SVN Rev[2237]

* Thu Jan 13 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-9
- CHANGED: In spect file was added script to add permissions
  to "Operador" Group on "Control Panel" Module

* Wed Jan 05 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-8
- UPDATED: Module VoIP Provider, Update codecs of Vozelia
  provider. SVN Rev[2220]
- ADDED: database endpoint, added the model AT 620R in the 
  table model. SVN Rev[2219]
- ADDED: module endpoint_configuration, added a new model of 
  phone for the vendor ATCOM. SVN Rev[2218]

* Wed Jan 05 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-7
- NEW: Module VoIP Provider, New provider Vozelia. SVN Rev[2215]
- FIXED: PBX: Hangup macro now tests if MixMon filename actually
  exists, and clears CDR(userfield) if file is missing (as is 
  the case for NOANSWER call status). Fixes Elastix bug #422. 
  SVN Rev[2209]
- CHANGED: PBX: add comments to extension macros for readability
  SVN Rev[2209]
- FIXED: Monitoring: Do NOT delete CDR from database when 
  deleting audio file. Instead, update CDR to have audio:deleted 
  as its audio file. Also update index.php to cope with this 
  change. SVN Rev[2206]
- CHANGED: Monitoring: do not complain if recording does not 
  exist when deleting it. SVN Rev[2205]
- FIXED: Monitoring: do not reset filter with bogus values at 
  recording removal time. This allows user to realize that 
  recording has indeed been removed when displaying date ranges 
  other than current day. SVN Rev[2204]

* Mon Jan 03 2011 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-6
- UPDATED: Module VoIP Provider, Provider Net2phone codecs 
  updated attributes. SVN Rev[2201]

* Thu Dec 30 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-5
- FIXED: Module Monitoring, Fix bug with record of audio files
  in a conference. SVN Rev[2200]
- CHANGED: module endpoint_configuration, new parameter for the
  phone GXV3140. SVN Rev[2197]

* Thu Dec 30 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-4
- CHANGED: module endpoint_configurator, new parameters for the 
  configuration of the phones grandstream and renamed the names 
  of the files with the configuration. SVN Rev[2187]
- CHANGED: database endpoint, four new models were inserted. 
  SVN Rev[2186]
- CHANGED: Module VoIP Provider, change ip 208.74.169.86, for 
  gateway.circuitid.com of provider CircuitID. SVN Rev[2180]

* Tue Dec 28 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-3
-  NEW: New file macros elastix, old files macro hangup and
   macro record was remove as sources of RPM and put in tar file
   of PBX. SVN Rev[2167]

* Mon Dec 27 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-2
- CHANGED: In Spec file add new prereq elastix-my_extension to 
  remove the old instance of myextension of elastix-pbx
- FIXED: In Database Voip Provider appear a warning after to 
  install, this warning appear in the moment to read the old 
  database to replace during a update. SVN Rev[2159]

* Mon Dec 20 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.4-1
- CHANGED: Add tftpboot, openfire, ftp and vsftp in spec file as 
  part of process install and post. This configurations were in
  elastix.spec
- NEW:     Module VoIP Provider, new provider CircuitID was added.
  SVN Rev[2120]
- DELETED:  Module myextension of PBX wax remove and moved to 
  new main menu called My Extension. SVN Rev[2113]
- NEW:     New files of vsftpd, xinetd.d folders and 
  vsftpd.user_list file in setup/etc in modules/trunk/pbx/, now 
  the spec of elastix.pbx use and required these services
  SVN Rev[2109]
- NEW:     Tftpboot in setup of pbx was added from trunk, it is 
  for get a better organization. SVN Rev[2106]
- CHANGED: Module endpoint configurator, DTMF in phones atcom, 
  are configurated to send on rfc2833. SVN Rev[2093]

* Mon Dec 06 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-42
- CHANGED: Add new Prereq freePBX in spec file
- FIXED:  Quit menu=module_name as parameters to send for ajax to 
  identify the menu to get data. This change was done in javascript
  in voipProvider module. SVN Rev[2042]
- CHANGED:    Module monitoring, to export data from reports the
  output contain text html if the report to export has any styles
  or html elements as part of grid. The solution was changing the
  data to export only if the request is export so, the data(array) 
  can be returned without html elements only the data from 
  database, it is in paloSantoGrid.class.php in commit 2024.
  SVN Rev[2034]
- CHANGED:    Module VOIP Provider was changed and new functionality 
  were done, for example the creation of new account and custom 
  accounts. SVN Rev[2025]
- FIXED: Module monitoring, variable $file no found in commit 2011.
  SVN Rev[2016]
- CHANGED: massive search and replace of HTML encodings with the
  actual characters. SVN Rev[2002]
- FIXED:   Conference: detect Asterisk version on the fly to 
  decide whether to use a pipe or a comma to separate arguments 
  for an Asterisk application. Fixes Elastix bug #578. SVN Rev[1998]
- FIXED:   Conference: properly escape HTML characteres to prevent 
  XSS in grid display of conferences. SVN Rev[1992]
- CHANGED: stop assigning template variable "url" directly, and 
  remove nested <form> tag. The modules with those changes are:
  Conference SVN Rev[1992], Voicemail SVN Rev[1990], 
  Endpoint Configurator SVN Rev[1984]
- FIXED: Voicemail: emit proper 404 HTTP header when denying 
  access to a recording. SVN Rev[1990]
- CHANGED: Voicemail: synchronize index.php between Elastix 1.6
  and Elastix 2. SVN Rev[1987]
- FIXED: File Editor: complete rewrite. This rewrite achieves 
  the following:
         Add proper license header to module file
         Improve readability of code by splitting file listing 
           and file editing into separate procedures
         Remove opportunities for XSS in file list navigation 
           (ongoing fix for Elastix bug #572)
         Remove opportunities for XSS in file content viewing.
         Remove possible opportunity for arbitrary command 
           execution due to nonvalidated exec()
         Fix unintended introduction of DOS line separators when 
           saving files.
         Remove nested <form> tags as grid library already 
           introduces them.
  SVN Rev[1983]

* Fri Nov 26 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-41
- FIXED:  Monitoring module, the problem was that the recordings 
  of the queues "the audio file" if it was created but not saved 
  the information in the database. For the solution 
  extensions_override_freepbx.conf file was modified to add the 
  information stored in database at the time of the hangup, and 
  the respective changes in Monitoring Module. SVN Rev[2011]

* Mon Nov 15 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-40
- FIXED:  Fixed bug where use $oForm->fetchForm in the function
  load_extension in extension batch and never was used. SVN Rev[1953]

* Fri Nov 12 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-39
- FIXED:change style in the tittle of the module my extension.
  SVN Rev[1946]
- FIXED: make module aware of url-as-array in paloSantoGrid.
     Split up URL construction into an array.
     Assign the URL array as a member of the $arrGrid structure.
     Remove <form> tags from the filter HTML template fetch. They are 
      not required, since the template already includes a proper <form> 
      tag enclosing the grid.
     Part of fix for Elastix bug #572. Requires commits 1901 and 1902 
      in order to work properly.
  SVN Rev[1915]
- FIXED: Problem with changing the page, when searching and want to move 
  from page to page the search pattern is lost, also did not show the 
  correct amount of the results, related bug [# 564] of bugs.elastix.org. 
  Also had the problem that in the link of the page showing all the names 
  of the files as parameters of GET request. The solution was to change 
  the way to build the url. Also the way to change the filter to obtain 
  data for both GET and POST. SVN Rev[1904]

* Fri Nov 05 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-38
- ADDED: Create folder version_sql in update process. SVN Rev[1896]
- FIXED: day night modes cannot be edited in Elastix embedded
  freePBX, [#576] www.bugs.elastix.org. SVN Rev[1893]
- CHANGED: Routine maintenance, changed the name of the file and
  remove lines that do nothing to create folders that were not used.
  SVN Rev[1891]

* Sat Oct 30 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-37
- FIXED:  Add macros in /etc/asterisk/extensions_override_freepbx.conf
  but asterisk never is reloaded. Changes in SPEC

* Fri Oct 29 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-36
- FIXED:  File migartionFileMontor.php was not work fine. 
  Some monitoring audio files were not written SVN Rev[1877]
- FIXED:  Fixed bug where users cannot listen the audios in 
  monitoring. [#563].SVN Rev[1875]

* Thu Oct 28 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-35
- FIXED:  Change move migrationFilesMonitor.php into folder installer
  /usr/share/elastix/"moduleInstall"/setup/

* Thu Oct 28 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-34
- CHANGED: Add headers of information in migrationFilesMonitor.php.
  SVN Rev[1868]

* Wed Oct 27 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-33
- CHANGED: Spec file was change. New file migrationFilesMonitor.php, it 
  was removed from elastix.spec and now it part of the source of 
  elastix-pbx. SVN Rev[1866]

* Wed Oct 27 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-32
- CHANGED: Updated the Bulgarian language elastix. SVN Rev[1857]
- FIXED:  Batch Of Extensions Problems with Outbound CID and Inbound DID, 
  they don't appear this fields in csv files to download. 
  More details in http://bugs.elastix.org/view.php?id=447. SVN Rev[1853]

* Tue Oct 26 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-31
- CHANGED: The Spec file valid if version and release are lower to 
  1.6.2-13 for doing migration of monitoring audio files. It is only for
  migration Elastix 1.6 to 2.0

* Tue Oct 26 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-30
- CHANGED: Move line elastix-menumerge at beginning the "%post" in spec file. 
  It is for the process to update.

* Mon Oct 18 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-29
- FIXED:   Fixed security bug with audio.php and popup.php where an user can be download 
  files system without authentication. See in http://bugs.elastix.org/view.php?id=552
  SVN Rev[1833]
- CHNAGED: Language fr.lang was updated. SVN Rev[1825]
- ADDED:   New lang file fa.lang. SVN Rev[1823]
- FIXED:   It validates that the index of the callerid exist, if it don't 
  exits the callerid is left. This fixes a problem that did not display the number of
  participants at the conference when it is an outside call. 
  Bug [#491]. Bug [#491] SVN Rev[1814]

* Mon Sep 27 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-28
- FIXED:    include character '/' in function isDialpatternChar where character / (match cid) not valid for dial pattern in outbound routes. SVN Rev[1754], Bug[#485] 

* Tue Sep 14 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-27
- CHANGED: rework translation support so that it will work with untranslated English strings for new menu items. Rev[1734]
- FIXED:   add several new menu items for FreePBX menus, to make them appear on the embedded interface. Should fix Elastix bug #458. Rev[1734]
- FIXED:   Valid fields with only spaces blank. Rev[1740]
- FIXED:   actually implement paging correctly on discovered endpoint list. Should fix Elastix bug #411. Rev[1732]
- FIXED:   preserve list of discovered endpoints across page refreshes until next reload. Rev[1732]
- CHANGED: enforce sorting by IP on list of discovered endpoints. Rev[1732]

* Mon Aug 23 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-26
- REMOVE: Remove extensions_override_freepbx.conf in Sources for many macros as macro-record-enable and macro-hangupcall. 

* Mon Aug 23 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-25
- FIXED: Fixed bug[#409] and change the Source extensions_override_freepbx.conf.

* Fri Aug 20 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-24
- FIXED: Fix incorrect wording for text string. Part of fix for bug #421. Rev[1724]
- FIXED: Merge translations strings from local language with English. This allows module to display English text if localized text is unavailable, instead of showing blanks. Rev[1721]
- FIXED: do not use uninitialized array indexes when logged-on user has no extension. Rev[1718]

* Thu Aug 12 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-23
- NEW:     New module My Extension in PBX, It configure the user's extension from elastix web interface. Rev[1694]

* Sat Aug 07 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-22
- CHANGED: Change help files in  Operator Panel, Endpoint Configurator, VoIP Provider.
           Change the module name to Operator Panel
- CHANGED: Task [#243] extension batch. Now if no extension availables the file downloaded show all columns about the information that it must have...

* Wed Jul 28 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-21
- FIXED: Script is not authenticated session, and anyone from the internet can be invoked with arbitrary parameters.
-        Expose connection data of known IP providers

* Fri Jul 23 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-20
- NEW: Implementation to support install database in fresh install.

* Fri Jul 23 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-19
- CHANGED: database module conference (meetme db) was removed in process index.php instalation in web interface. Now the install db is with to help elastix-dbprocess.

* Fri Jul 23 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-18
- DELETED: Source module realtime, this module is devel yet.
- CHANGED: String connection database to asteriskuser in module monitoring.

* Fri Jul 23 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-17
- CHANGED: Name module to Operator Panel.
- CHANGED: String connection database to asteriskuser. 

* Thu Jul 01 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-16
- FIXED:    Add line 'global $recordings_save_path' in pbxadmin module to obtain the path where upload audio files in recording [#346] bugs.elastix.org

* Thu Jun 17 2010 Eduardo Cueva <ecueva@palosanto.com> 2.0.0-15
- Change module extensions batch. Now the option download cvs is processing by index.php 

* Thu Apr 15 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-14
- Change port 5061 to 5060 in file config vendor Cisco.cfg.php module endpoint configurator.
- Fixed bug module extension batch, wasn't validating the file csv. Error code in compration boolean expresion.
- Fixed bug in module monitoring not had been changed  the new code.
- Be improve the look in module voip provider.


* Thu Mar 25 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-13
- Re-write macro-record-enable for freePBX, this action is for module monitorin support new programming in based database asteriskcdrdb.
- Module Monitoring was rewrited, improved behavoir in search audio files. 

* Fri Mar 19 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-12
- Defined Lang missed. 

* Tue Mar 16 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-11
- Defined number order menu.

* Mon Mar 01 2010 Bruno Macias <bmacias@palosanto.com> 2.0.0-10
- Fixed minor bug in EOP.

* Wed Dec 30 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-6
- Fixed bug module Voip Provider, change name voip-provider-cust to voip-provider.

* Tue Dec 29 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-7
- Improved module control panel support multi columns.
- Fixed bug, boxes of extension into other them.
- Improved module VOIP Provider performance.

* Fri Dec 04 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-6
- Improved the modulo voip provider, validation and look.

* Mon Oct 19 2009 Alex Villacis <bmacias@palosanto.com> 2.0.0-5
- Inplemetation for support web conferences in module cenferences elastix.

* Fri Sep 18 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-4
- New module VOIP PROVIDER
- Fixed minor bugs in definition words languages and messages.
- Add accion uninstall rpm.

* Fri Sep 18 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-3
- Add words in module coference.

* Mon Sep 07 2009 Bruno Macias <bmacias@palosanto.com> 2.0.0-2
- New structure menu.xml, add attributes link and order.

* Wed Aug 26 2009 Bruno Macias <bmacias@palosanto.com> 1.0.0-1
- Initial version.
