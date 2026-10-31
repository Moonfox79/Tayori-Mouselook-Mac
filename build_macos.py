"""Build the pinned personal viewer on a disposable macOS GitHub runner."""
from pathlib import Path
import hashlib, json, os, plistlib, shutil, subprocess, sys, zipfile

BASE='be6bce603845b9dc376a381722ebd9525aba0e64'
VARIABLES='c17312d38377c003977cf5b6dcc83c6042eba194'
PACKAGE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('RUNNER_TEMP','/tmp'))/'tayori-mac-build'
OUT=PACKAGE/'dist'
EXTRA=['fsfloatertargetlock.cpp','fsfloatertargetlock.h','tayoriaim.h',
       'skins/default/xui/en/floater_fs_target_lock.xml']

def run(args,cwd=None,env=None):
    print('>',subprocess.list2cmdline([str(a) for a in args]),flush=True)
    subprocess.run([str(a) for a in args],cwd=cwd,env=env,check=True)

def checkout(path,url,commit):
    path.mkdir()
    run(['git','init',path])
    run(['git','remote','add','origin',url],cwd=path)
    run(['git','-c','core.autocrlf=false','fetch','--depth','1','origin',commit],cwd=path)
    run(['git','-c','core.autocrlf=false','checkout','--detach','FETCH_HEAD'],cwd=path)
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()
    if actual!=commit:raise RuntimeError('Unexpected upstream revision')

def validate_patch_content(source):
    s=(source/'indra/newview/fsfloatertargetlock.cpp').read_text()
    if s.count('setText(std::string(') != 3:
        raise RuntimeError('Missing explicit status text conversions')
    for expected in ['changeCameraToMouselook(false)', 'LLVector3 aim = av->getPositionAgent();',
                     'aim.mV[VZ] += 0.35f;', '[](LLUICtrl*, const LLSD&) { stop(); }']:
        if expected not in s:raise RuntimeError('Missing tested correction: '+expected)

def source_archive(source,dest):
    names=set(subprocess.check_output(['git','ls-files','-z'],cwd=source).decode().split('\0'))-{''}
    names.update('indra/newview/'+n for n in EXTRA)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(names):
            p=source/name
            if not p.is_file():raise RuntimeError('Missing source: '+name)
            z.write(p,name)

def main():
    if sys.platform!='darwin':raise RuntimeError('Requires macOS with Xcode')
    if ROOT.exists():raise RuntimeError('Build directory already exists; use a fresh runner')
    ROOT.mkdir(parents=True);OUT.mkdir(exist_ok=True)
    source=ROOT/'source';variables=ROOT/'variables'
    checkout(source,'https://github.com/FirestormViewer/phoenix-firestorm.git',BASE)
    checkout(variables,'https://github.com/FirestormViewer/fs-build-variables.git',VARIABLES)
    run(['git','apply','--check',PACKAGE/'Tayori_TargetLock.patch'],cwd=source)
    run(['git','apply',PACKAGE/'Tayori_TargetLock.patch'],cwd=source)
    validate_patch_content(source)
    run([sys.executable,'-m','pip','install','-r',source/'requirements.txt'])
    env=os.environ.copy()
    env['PYTHON']=sys.executable
    env['AUTOBUILD_VARIABLES_FILE']=str(variables/'variables')
    env['AUTOBUILD_CPU_COUNT']='2'
    env['CMAKE_BUILD_PARALLEL_LEVEL']='2'
    # Upstream uses its ad-hoc signing path when no build-secrets checkout exists.
    env.pop('build_secrets_checkout',None)
    autobuild=shutil.which('autobuild')
    if not autobuild:raise RuntimeError('autobuild missing from PATH')
    free=shutil.disk_usage(ROOT).free/1024**3
    print(f'Free disk before configure: {free:.1f} GiB',flush=True)
    if free<12:raise RuntimeError('Less than 12 GiB free; no build attempted')
    run([autobuild,'configure','-A','64','-c','ReleaseFS_open','--','--package',
         '--chan','TayoriTargetLock','-DLL_TESTS:BOOL=FALSE',
         '-DPYTHON_EXECUTABLE:FILEPATH='+sys.executable,
         '-DAUTOBUILD_EXECUTABLE:FILEPATH='+autobuild],cwd=source,env=env)
    run([autobuild,'build','-A','64','-c','ReleaseFS_open','--no-configure'],cwd=source,env=env)
    build=source/'build-darwin-universal'
    images=list((build/'newview').glob('*.dmg'))+list((build/'newview/Release').glob('*.dmg'))
    if len(images)!=1:raise RuntimeError('Expected one DMG; found '+str(images))
    image=images[0]
    run(['hdiutil','verify',image])
    result=subprocess.check_output(['hdiutil','attach','-readonly','-nobrowse','-plist',str(image)])
    mounted=plistlib.loads(result)
    mounts=[Path(e['mount-point']) for e in mounted['system-entities'] if 'mount-point' in e]
    if len(mounts)!=1:raise RuntimeError('Unexpected DMG mount points')
    mount=mounts[0]
    try:
        apps=list(mount.glob('*.app'))
        if len(apps)!=1:raise RuntimeError('Expected one application on DMG')
        app=apps[0]
        info=plistlib.loads((app/'Contents/Info.plist').read_bytes())
        executable=app/'Contents/MacOS'/info['CFBundleExecutable']
        archs=subprocess.check_output(['lipo','-archs',str(executable)],text=True).split()
        if not {'arm64','x86_64'}.issubset(archs):raise RuntimeError('Not universal: '+str(archs))
        run(['codesign','--verify','--deep','--strict','--verbose=2',app])
    finally:
        run(['hdiutil','detach',mount])
    shutil.copy2(image,OUT/image.name)
    source_archive(source,OUT/'Firestorm_Quellen_Mac.zip')
    shutil.copy2(PACKAGE/'LICENSE_Firestorm.txt',OUT/'LICENSE_Firestorm.txt')
    shutil.copy2(PACKAGE/'README.md',OUT/'BITTE_LESEN.md')
    with zipfile.ZipFile(OUT/'Tayori_Mac_Buildquellen.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ['build_macos.py','Tayori_TargetLock.patch','Firestorm_Mac_Build_Original.md',
                     'LICENSE_Firestorm.txt','README.md','.github/workflows/build-macos.yml']:
            z.write(PACKAGE/name,name)
    with zipfile.ZipFile(OUT/'Firestorm_Buildvariablen.zip','w',zipfile.ZIP_DEFLATED) as z:
        names=subprocess.check_output(['git','ls-files','-z'],cwd=variables).decode().split('\0')
        for n in names:
            if n:z.write(variables/n,n)
    hashes={}
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!='SHA256.json':
            with p.open('rb') as f:hashes[p.name]=hashlib.file_digest(f,'sha256').hexdigest()
    (OUT/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    (OUT/'BUILD_RESULT.json').write_text(json.dumps({'upstream':BASE,'variables':VARIABLES,
        'architectures':archs,'signature':'ad-hoc, no Apple notarization',
        'dmg_integrity':'PASS','signature_verification':'PASS','in_world_test':'NOT_PERFORMED'},indent=2)+'\n')
    print('Mac package assembled in',OUT,flush=True)

if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,subprocess.CalledProcessError) as exc:
        print('BUILD FAILED:',exc,file=sys.stderr);sys.exit(1)
