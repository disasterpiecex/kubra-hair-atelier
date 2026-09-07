from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

old="function fullyExit(){setShowExit(false);if(Platform.OS==='android'){const native=NativeModules.KubraExit;if(native?.exitApp){native.exitApp();return}BackHandler.exitApp()}}"
new="async function fullyExit(){setShowExit(false);try{await Promise.all([AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri,previewUri})),AsyncStorage.setItem(SAVED,JSON.stringify(savedLooks))])}catch{}if(Platform.OS==='android'){const native=NativeModules.KubraExit;if(native?.exitApp){native.exitApp();return}BackHandler.exitApp()}}"
if old not in s:
    raise SystemExit('v1.8 exit persistence target not found')
s=s.replace(old,new,1)
p.write_text(s)
print('Applied v1.8 exit-state flush before app termination to',p)
