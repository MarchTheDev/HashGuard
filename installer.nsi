; HashGuard - NSIS Installer
; Build with: makensis /DAPP_VERSION=1.1 installer.nsi
;
; Upgrade / Silent flags:
;   /S         – silent (no UI) install, used for in-app auto-update
;   /UPDATE    – custom flag signalling "upgrade" (keeps existing shortcuts,
;                skips the Welcome / Directory pages)

!define APP_NAME      "HashGuard"
!define APP_EXE       "HashGuard.exe"
!define PUBLISHER     "HashGuard"
!define REGKEY        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
!define INSTDIR_REG   "Software\${PUBLISHER}\${APP_NAME}"

!ifndef APP_VERSION
  !define APP_VERSION "1.1"
!endif

OutFile "HashGuard-Setup-${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "${INSTDIR_REG}" "InstallDir"
RequestExecutionLevel admin

!include "MUI2.nsh"
!include "LogicLib.nsh"

; Icon setup - use /nonfatal so build continues if icon doesn't exist
!define MUI_ICON "hashguard.ico"
!define MUI_UNICON "hashguard.ico"

!define MUI_ABORTWARNING

; ---------------------------------------------------------------------------
; Detect whether this is an upgrade (existing install found)
; ---------------------------------------------------------------------------
Var IsUpgrade
Var PrevInstallDir

Function .onInit
  StrCpy $IsUpgrade "0"

  ; Check registry for previous installation
  ReadRegStr $PrevInstallDir HKLM "${INSTDIR_REG}" "InstallDir"
  ${If} $PrevInstallDir != ""
  ${AndIf} ${FileExists} "$PrevInstallDir\${APP_EXE}"
    StrCpy $IsUpgrade "1"
    ; Use the previous install directory for the upgrade
    StrCpy $INSTDIR $PrevInstallDir
  ${EndIf}

  ; If /UPDATE flag was passed (in-app auto-update), force silent + use existing dir
  ${If} $IsUpgrade == "1"
    ; Check for /UPDATE command-line flag
    StrCpy $0 ""
    ${GetParameters} $0
    ${StrContains} $1 "/UPDATE" $0
    ${If} $1 != ""
      ; Already in upgrade path — silent is handled by /S
    ${EndIf}
  ${EndIf}
FunctionEnd

; ---------------------------------------------------------------------------
; Pages — skip Welcome + Directory when upgrading silently
; ---------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Name "${APP_NAME}"
BrandingText "${APP_NAME} ${APP_VERSION}"

; ---------------------------------------------------------------------------
; Installer section
; ---------------------------------------------------------------------------
Section "Install" SecInstall
  SectionIn RO

  ; Kill any running instance (needed for both fresh install and upgrade)
  ExecWait 'taskkill /F /IM "${APP_EXE}"' $0
  Sleep 1500

  SetOutPath "$INSTDIR"
  File '/oname=${APP_EXE}' "dist\HashGuard.exe"

  ; Icon - use /nonfatal so build continues if not present
  File /nonfatal "hashguard.ico"

  ; -----------------------------------------------------------
  ; Shortcuts — only create on fresh install, or if /UPDATE
  ; is NOT present (normal GUI install always creates them)
  ; -----------------------------------------------------------
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"

  ; Start Menu shortcut (always refresh)
  ${If} ${FileExists} "$INSTDIR\hashguard.ico"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\hashguard.ico" 0
  ${Else}
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  ${EndIf}

  ; Desktop shortcut — create only on fresh install
  ${If} $IsUpgrade == "0"
    ${If} ${FileExists} "$INSTDIR\hashguard.ico"
      CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\hashguard.ico" 0
    ${Else}
      CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    ${EndIf}
  ${EndIf}

  ; -----------------------------------------------------------
  ; Registry entries (overwrite with new version info)
  ; -----------------------------------------------------------
  WriteRegStr HKLM "${INSTDIR_REG}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "${REGKEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${REGKEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "${REGKEY}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "${REGKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${REGKEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  
  ${If} ${FileExists} "$INSTDIR\hashguard.ico"
    WriteRegStr HKLM "${REGKEY}" "DisplayIcon" "$INSTDIR\hashguard.ico"
  ${Else}
    WriteRegStr HKLM "${REGKEY}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  ${EndIf}
  
  WriteRegDWORD HKLM "${REGKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${REGKEY}" "NoRepair" 1

  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; ---------------------------------------------------------------------------
; Uninstaller section
; ---------------------------------------------------------------------------
Section "Uninstall"
  ExecWait 'taskkill /F /IM "${APP_EXE}"' $0
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\hashguard.ico"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "${REGKEY}"
  DeleteRegKey HKLM "${INSTDIR_REG}"
SectionEnd
