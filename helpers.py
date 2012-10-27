from puke import *
import re
import json

# ==================================================================
# Global helpers for puke
# ==================================================================

# ------------------------------------------------------------------
# Common yak soup
# ------------------------------------------------------------------

def __enforceunix():
  # Puke at large is just untested on windows - and specifically these helpers
  if System.OS != System.MACOS and System.OS != System.LINUX:
    console.fail('Your platform is not supported')

def __yankconfiguration():
  # Yank the base config file
  r = Require('config.yaml')
  # Try to get separate user specific file, either as json or yaml
  usercpath = 'config-%s-%s' % (Env.get("PUKE_LOGIN", System.LOGIN), Env.get("PUKE_OS", System.OS).lower())
  try:
    r.merge(usercpath + ".json")
  except:
    try:
      r.merge(usercpath + ".yaml")
    except:
      pass

  # Yank in the base and default config
  r.yak('baseYank')
  r.yak('defaultYank')
  # Try to yank in a user defined node
  try:
    r.yak(usercpath)
    console.info('Reading inline user configuration from main file')
  except:
    pass
  try:
    r.yak('userYank')
    console.info('Reading separate user configuration')
  except:
    pass

def __yankgitdata():
  # Git helpers
  # Commit hash start: git log -n1 --pretty=format:%h
  # Full commit hash: git log | head -n 1 | cut -f2 -d" "
  # Commit number: git log --pretty=format:%h | wc -l
  # Current branch: git branch | grep '*'

  try:
    branch = sh("cd .; git branch | grep '*'", output=False).strip('*').strip()
    if branch == '(no branch)':
      branch = sh("cd .; git describe --tags", output=False).strip()
    commitnb = sh("cd .; git log --pretty=format:%s | wc -l" % '%h', output=False).strip()
    commithash = sh("cd .; git log | head -n 1 | cut -f2 -d' '", output=False).strip()
    Yak.git['root'] = Yak.git['root'].replace('/master/', '/' + branch + '/')
    Yak.git['revision'] = '#' + commitnb + '-' + commithash
  except:
    Yak.git['revision'] = '#no-git-information'
    console.error("FAILED fetching git information - locations won't be accurate")

def __preparepaths():
  # Aggregate package name and version to the "root" path, if not the default
  if Yak.root != './':
    Yak.root = FileSystem.join(Yak.root, Yak.package['name'], Yak.package['version'])

  # Aggregate all inner paths against the declared ROOT, and build-up all the corresponding top level Yak variables
  for (key, path) in Yak.paths.items():
    # Build-up global key only if not overriden
    if not (key + '_root') in Yak:
      Yak.set(key + '_root', FileSystem.join(Yak.root, path))
    FileSystem.makedir(Yak.get(key + '_root'))


def __prepareconfig():
  Yak.istrunk = Yak.settings['variant'] == 'bleed'


__enforceunix()
__yankconfiguration()
__yankgitdata()
__preparepaths()
__prepareconfig()

# ------------------------------------------------------------------
# Top-level helpers
# ------------------------------------------------------------------

# Cleans every "ROOT" folder cautiously
def cleaner():
  for key in Yak.paths.keys():
    pathtoremove = Yak.get(key + '_root')
    resp = prompt('Delete %s? y/[N]' % pathtoremove, 'N')
    if resp == 'y':
      try:
        FileSystem.remove(pathtoremove)
        console.info('Deleted %s' % pathtoremove)
      except:
        console.error('Failed removing %s' % pathtoremove)


# Adds a {PUKE-*-*} pattern for every package, link, or path entry in the Yak
def replacer(s):
  for (key, path) in Yak.package.items():
    s.add('{PUKE-PACKAGE-%s}' % key.replace('_', '-').upper(), Yak.package[key])
  for (key, path) in Yak.rights.items():
    s.add('{PUKE-RIGHTS-%s}' % key.replace('_', '-').upper(), Yak.rights[key])
  for (key, path) in Yak.git.items():
    s.add('{PUKE-GIT-%s}' % key.replace('_', '-').upper(), Yak.git[key])
  for (key, path) in Yak.paths.items():
    s.add('{PUKE-%s-ROOT}' % key.replace('_', '-').upper(), Yak.get(key + '_root'))
  if 'links' in Yak:
    for (key, path) in Yak.links.items():
      s.add('{PUKE-%s-LINK}' % key.replace('_', '-').upper(), Yak.links[key]['url'])
  return s


# Mint every file in the provided path avoiding xxx files, tests, and already mint files themselves (usually the build root)
excludecrap = '*xxx*'

def minter(path, filter = '', excluding = '', strict = True):
  if excluding:
    excluding = ',%s' % excluding

  if not filter:
    filtre = '*.js'
    list = FileList(path, filter = filtre, exclude = "*-min.js,%s%s" % (excludecrap, excluding))
    for burne in list.get():
      print burne
      print re.sub(r"(.*).js$", r"\1-min.js", burne)
      minify(burne, re.sub(r"(.*).js$", r"\1-min.js", burne), strict = strict)
    filtre = '*.css'
    list = FileList(path, filter = filtre, exclude = "*-min.css,%s%s" % (excludecrap, excluding))
    for burne in list.get():
      minify(burne, re.sub(r"(.*).css$", r"\1-min.css", burne))
  else:
    filtre = filter
    list = FileList(path, filter = filtre, exclude = "*-min.js,%s%s" % (excludecrap, excluding))
    for burne in list.get():
      minify(burne, re.sub(r"(.*).js$", r"\1-min.js", burne), strict = strict)

# Lint every file (usually src)
def linter(path, excluding = '', relax=False):
  if excluding:
    excluding = ',%s' % excluding
  list = FileList(path, filter = "*.js", exclude = "*-min.js,%s%s" % (excludecrap, excluding))
  jslint(list, relax=relax)

# Flint every file (usually src)
def flinter(path, excluding = '', relax=False):
  if excluding:
    excluding = ',%s' % excluding
  list = FileList(path, filter = "*.js", exclude = "*-min.js,%s%s" % (excludecrap, excluding))
  jslint(list, relax=relax, fix=True)

# Stat every file (usually build)
def stater(path, excluding = ''):
  if excluding:
    excluding = ',%s' % excluding
  list = FileList(path, filter = "*.js", exclude = "*-min.js,%s%s" % (excludecrap, excluding))
  stats(list, title = "Javascript")
  list = FileList(path, filter = "*-min.js", exclude = "%s%s" % (excludecrap, excluding))
  stats(list, title = "Minified javascript")
  list = FileList(path, filter = "*.css", exclude = "*-min.css,%s%s" % (excludecrap, excluding))
  stats(list, title = "Css")
  list = FileList(path, filter = "*-min.css", exclude = "%s%s" % (excludecrap, excluding))
  stats(list, title = "Minified css")
  list = FileList(path, filter = "*.html,*.xml,*.txt", exclude = "%s%s" % (excludecrap, excluding))
  stats(list, title = "(ht|x)ml + txt")
  list = FileList(path, exclude = "*.html,*.xml,*.txt,*.js,*.css,%s%s" % (excludecrap, excluding))
  stats(list, title = "Other")

def deployer(withversion):
  list = FileList(Yak.build_root, exclude="*.DS_Store")
  if withversion and (Yak.root != './' or Yak.deploy_root != './lib'):
    v = Yak.package['version'].split('-').pop(0).split('.')
    v = v[0] + "." + v[1]
    deepcopy(list, FileSystem.join(Yak.deploy_root, Yak.package['name'], v))
  else:
    deepcopy(list, Yak.deploy_root)


def describe(shortversion, name, description):
  yamu = FileSystem.join(Yak.deploy_root, "%s.json" % name)
  if FileSystem.exists(yamu):
    mama = json.loads(FileSystem.readfile(yamu))
    mama[shortversion] = description
  else:
    mama = {shortversion: description}

  # Straight to service root instead - kind of hackish...
  FileSystem.writefile(yamu, json.dumps(mama, indent=4))

# ------------------------------------------------------------------
# Dedicated airstrip helpers
# ------------------------------------------------------------------

def getyanks():
  # Airstrip yank in additional description files
  l = FileList('yanks', filter = '*.yaml');
  yanks = {}
  for i in l.get():
    a = Load(i)
    yanks = Utils.deepmerge(yanks, a.content['yanks'])

  Yak.collection = yanks
  return yanks


# Bulding / fetching helpers
def donode(path, extra):
  System.check_package('node')
  sh('cd "%s"; node %s' % (path, extra))

def dorake(path, extra = ''):
  System.check_package('rvm')
  System.check_package('npm')
  System.check_package('bundle')
  System.check_package('rake')
  # XXX handlebars requires node as well :/
  System.check_package('node')
  sh('cd "%s"; bundle; rake %s' % (path, extra))

def dothor(path, extra = ''):
  System.check_package('rvm')
  System.check_package('bundle')
  # System.check_package('tilt')
  # System.check_package('compass')
  sh('cd "%s"; bundle; thor %s' % (path, extra))

def domake(path, extra = ''):
  sh('cd "%s"; make %s' % (path, extra))


def fetchgit(url, dest):
  # Require git on the system to have it
  System.check_package('git')
  # If directory exist, then update the tree
  if FileSystem.exists(dest):
    console.info('Updating')
    that = 'cd "%s"; git stash; git stash drop' % dest
    sh(that, output=True)
    that = 'cd "%s"; git pull --rebase; ' % dest
  else:
    if not FileSystem.exists(FileSystem.dirname(dest)):
      FileSystem.makedir(FileSystem.dirname(dest))
    console.info('Cloning')
    that = 'cd "%s"; git clone %s' % (FileSystem.dirname(dest), url)

  # Do the deed
  try:
    std = Std()
    sh(that, std=std, output=False)
    if std.err and (std.err.find('No stash found.') == -1):
      raise std.err
  except:
    # if puke.FileSystem.exists(dest):
    #   puke.FileSystem.remove(dest)
    console.error('Git operation failed! %s You need to manually fix or remove the directory.' % std.err)

def fetchsvn(url, dest):
  System.check_package('svn')
  # If directory exist, then update the tree
  if FileSystem.exists(dest):
    console.info('Updating')
    that = 'cd "%s"; svn up' % dest
  else:
    if not FileSystem.exists(FileSystem.dirname(dest)):
      FileSystem.makedir(FileSystem.dirname(dest))
    console.info('Cloning')
    that = 'cd "%s"; svn co %s %s' % (FileSystem.dirname(dest), url, FileSystem.basename(dest))

  # Do the deed
  try:
    std = Std()
    sh(that, std=std, output=False)
    if std.err:
     # and (std.err.find('No stash found.') == -1):
      raise std.err
  except:
    # if puke.FileSystem.exists(dest):
    #   puke.FileSystem.remove(dest)
    console.error('Svn operation failed! %s You need to manually fix or remove the directory.' % std.err)


def fetchone(url, dest, rename):
  remotefilename = url.split('/').pop()
  type = url.split('.').pop().lower()
  # Dirty trick to detect zip where the remote has no extension
  destype = rename.split('.').pop().lower()
  packpath = FileSystem.join(dest, remotefilename)
  if type == 'git':
    packpath = packpath.split('.')
    packpath.pop()
    packpath = '.'.join(packpath)
    console.info('Git repository')
    fetchgit(url, packpath)
  elif type == 'svn' or destype == 'svn':
    console.info('Svn repository %s %s' % (url, packpath))
    fetchsvn(url, packpath)
  else:
    deepcopy(url, dest + '/')
    if type == 'zip' or type == 'gz' or type == 'bz2' or destype == 'zip':
      try:
        dd = FileSystem.join(dest, remotefilename.replace('.' + type, ''))
        if FileSystem.exists(dd):
          FileSystem.remove(dd)
        FileSystem.makedir(dd)
        unpack(packpath, dd, verbose = False)
        # puke.FileSystem.remove(packpath)
      except Exception as e:
        sh('cd "%s"; 7z x "%s"' % (dd,  FileSystem.abspath(packpath)));
      FileSystem.remove(packpath)
    else:
      if remotefilename != rename:
        if not FileSystem.exists(FileSystem.dirname(FileSystem.join(dest, rename))):
          FileSystem.makedir(FileSystem.dirname(FileSystem.join(dest, rename)))
        sh('cd "%s"; mv "%s" "%s"' % (dest, remotefilename, rename))
      packpath = FileSystem.join(dest, rename)



def make(path, type, extra = ''):
  if type == 'rake':
    dorake(path, extra)
  elif type == 'thor':
    dothor(path, extra)
  elif type == 'make':
    domake(path, extra)
  elif type == 'sh':
    sh('cd "%s"; %s' % (path, extra))

  # for (k, ipath) in production.items():
  #   FileSystem.copyfile(FileSystem.join(path, ipath), FileSystem.join(destination, k))

  # else:
  #   sh('cd "%s"; cp -R %s %s' % (path, latest, destination), output = True)
    #   sh("cd " + Yak.TMP_ROOT + "/lib/" + burne["Destination"] + "; cp -R " + burne["Latest"] + " " +  k + "; rm " + burne["Latest"])


      # localtmp = puke.FileSystem.join(tmp, url.split('/').pop())
      # if puke.FileSystem.checksum(localtmp) != self.__checksum:
      #   console.fail("PANIC! Archive doesn't pan out. You may puke -c if in doubt, and anyhow double check integrity. %s vs. %s" % (puke.FileSystem.checksum(localtmp), self.__checksum))

      # if type == 'dmg':
      #   console.info('Processing dmg')
      #   self.__dodmg(localtmp, self.local, pwd)
      # elif type == 'pkg':
      #   console.info('Processing pkg')
      #   self.__dopkg(localtmp)
      # else:
      #   console.info('Processing archive file')
      #   self.__dounpack(localtmp, puke.FileSystem.dirname(pwd))


