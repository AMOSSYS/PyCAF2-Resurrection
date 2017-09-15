@echo off
rem -----------------------------
rem Extraction tool for Microsoft Windows OS.
rem 
rem This script relies on several external software which are located
rem in the bin/ directory. All of these tools are free (as in free 
rem beer) software. See bin/TOOLS.txt for more information on how to
rem download them.
rem -----------------------------
@echo on

@rem -----------------------------
@echo [i] Verification des droits
@echo OFF
NET SESSION >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [+] Privileges Administrateur: OK !
) else (
   echo [-] ERREUR: Ce script a besoin de privileges Administrateur pour fonctionner correctement!
   echo Pour lancer le script, clique-droit puis: "Lancez en tant qu'Administrateur".
   goto :error
)
@echo ON
@rem -----------------------------


@rem -----------------------------
@rem -- outdir is path of current directory + output --
@rem -- Si le dossier existe deja, on quitte pour eviter une betise --
@cd %~dp0
@set outdir=output-%COMPUTERNAME%
@echo [i] Verification du repertoire de destination...

@echo OFF
if exist "%outdir%\" (
	echo [-] Le repertoire de destination "%outdir%\" existe deja, merci de choisir un autre dossier.
	goto :error
)
@echo ON

@mkdir %outdir%
@echo [+] Creation du dossier de destination "output"
@rem -----------------------------


@rem -----------------------------
@echo [+] Lancement du script
@date /T > %outdir%/log
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la version de Windows
@ver > %outdir%/win_version.txt
@systeminfo > %outdir%/system_info.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des utilisateurs
@bin\dumpsec /rpt=users /saveas=csv /outfile=%outdir%\u_users.txt /showosid
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des groupes
@bin\dumpsec /rpt=groups /saveas=csv /outfile=%outdir%\u_groups.txt /showosid
@net group > %outdir%\u_netgroup.txt
@net localgroup > %outdir%\u_localgroup.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export des politiques de domaine
@bin\dumpsec /rpt=policy /saveas=csv /outfile=%outdir%\domain_policies.txt
@net accounts > %outdir%\u_policy.txt
@auditpol /backup /file:%outdir%/audit_pol.csv
@ver | find " 5." > nul
@if %ERRORLEVEL%==0 goto W2K3_GPR 
@gpresult /h %outdir%/GP-Report.html /f
@goto END_GPR
:W2K3_GPR
@gpresult /V > %outdir%/GP-Report.txt
:END_GPR
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des services
@bin\dumpsec /rpt=services /saveas=csv /outfile=%outdir%\services.txt
@sc query type= service > %outdir%/services_activ.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des partages
@bin\dumpsec /rpt=shares /saveas=csv /outfile=%outdir%\shares.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de secedit
@secedit /export /cfg %outdir%\local-policy-export.txt
@net accounts > %outdir%\u_policy.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des processus
@bin\pslist /accepteula -t > %outdir%/ps-tree.txt
@bin\pslist /accepteula -m > %outdir%/ps-memory.txt
@tasklist /FO table /V > %outdir%/ps2.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la configuration reseau
@ipconfig /all > %outdir%/ipconfig.txt
@arp -a > %outdir%/arp.txt
@route print > %outdir%/route.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la configuration IPsec
@netsh ipsec static show policy all > %outdir%/ipsec_pol.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la liste des logiciels installes
@bin\psinfo.exe /accepteula
@bin\psinfo.exe -s > %outdir%/software.txt
@bin\psinfo.exe -s -c > %outdir%/software.csv
@bin\psinfo.exe -h > %outdir%/hotfixes.txt
@bin\psinfo.exe -h -c > %outdir%/hotfixes.csv
@wmic qfe list full > %outdir%/installed_patches.txt
@wmic qfe list full /format:htable >%outdir%/installed_patches.htm
@rem -----------------------------

@rem -----------------------------
@echo [+] Export des taches programmees
@schtasks.exe /Query > %outdir%/scheduled_tasks.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la configuration netbios
@netstat -abnO > %outdir%/netstat.txt
@netstat -abnO | find /i "listening" > %outdir%/netstat_listening.txt
@nbtstat -a %COMPUTERNAME% > %outdir%/netbios.txt
@nbtstat -c > %outdir%/netbios-c.txt
@rem -----------------------------

@rem -----------------------------
@echo [+] Copie de fichiers systemes
@xcopy /Y /Q %SystemRoot%\system32\drivers\etc\lmhosts.sam %outdir%
@xcopy /Y /Q %SystemRoot%\system32\drivers\etc\hosts %outdir%
@rem -----------------------------

@rem -----------------------------
@echo [+] Export de la configuration systeme
@msinfo32 /nfo %outdir%\msinfo.nfo
@rem -----------------------------

@rem -----------------------------
@echo [+] Compression de l'archive et suppression des fichiers temporaires
@bin\7za.exe a -tzip -r export-%COMPUTERNAME%.zip %outdir%
@del /s /q %outdir%
@rmdir %outdir%
@rem -----------------------------

@rem -----------------------------
@echo [+] Fin du script
@rem @date /T >> %outdir%/log
@rem -----------------------------

@goto done

:error
@echo [-] Le script a rencontre une erreur... 
@goto :done

:done
@echo Veuillez appuyer sur une touche pour quitter.
@pause
@exit /B 1
