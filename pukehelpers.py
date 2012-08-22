from puke import *
import re

# ==================================================================
# General javascript oriented helpers for puke
# ==================================================================

# ------------------------------------------------------------------
# Common yak soup
# ------------------------------------------------------------------

# Puke at large is just untested on windows - and specifically these helpers
if System.OS != System.MACOS and System.OS != System.LINUX:
  console.fail('Your platform sux ass')

# Yank the description file in
r = Require('puke-yak.yaml')
r.yak('yak')
r.yak('user-%s-%s-%s' % (Env.get("PUKE_LOGIN", System.LOGIN), 'box', Env.get("PUKE_OS", System.OS)))

# Aggregate package name and version to the "root" path, if not the default
if Yak.ROOT != './build':
  Yak.ROOT = FileSystem.join(Yak.ROOT, Yak.PACKAGE['NAME'], Yak.PACKAGE['VERSION'])

# Aggregate all inner paths against the declared ROOT, and build-up all the corresponding top level Yak variables
for (key, path) in Yak.ROOT_PATHS.items():
  # Build-up global key only if not overriden
  if not (key + '_ROOT') in Yak:
    Yak.set(key + '_ROOT', FileSystem.join(Yak.ROOT, path))
  FileSystem.makedir(Yak.get(key + '_ROOT'))


# ------------------------------------------------------------------
# Top-level helpers
# ------------------------------------------------------------------

# Cleans every "ROOT" folder cautiously
def cleaner():
  for key in Yak.ROOT_PATHS.keys():
    pathtoremove = Yak[key + '_ROOT']
    resp = prompt('Delete %s? y/[N]' % pathtoremove, 'N')
    if resp == 'y':
      try:
        FileSystem.remove(pathtoremove)
        console.info('Deleted %s' % pathtoremove)
      except:
        console.warn('Failed removing %s' % pathtoremove)

# Adds a {PUKE-*-*} pattern for every package, link, or path entry in the Yak
def replacer(s):
  for (key, path) in Yak.ROOT_PATHS.items():
    s.add('{PUKE-%s}' % (key + '-ROOT').replace('_', '-'), Yak.get(key + '_ROOT'))
  for (key, path) in Yak.PACKAGE.items():
    s.add('{PUKE-%s}' % ('PACKAGE-' + key).replace('_', '-'), Yak.PACKAGE[key])
  if 'LINKS' in Yak:
    for (key, path) in Yak.LINKS.items():
      s.add('{PUKE-%s}' % (key + '-LINK').replace('_', '-'), Yak.LINKS[key])
  return s

# Mint every file in the provided path avoiding xxx files, tests, and already mint files themselves (usually the build root)
excludecrap = '*/tests/*,*xxx*'
def minter(path, strict = True):
  list = FileList(path, filter = "*.js", exclude = "*-min.js,%s" % excludecrap)
  for burne in list.get():
    minify(burne, re.sub(r"(.*).js$", r"\1-min.js", burne), strict = strict)
  list = FileList(path, filter = "*.css", exclude = "*-min.css,%s" % excludecrap)
  for burne in list.get():
    minify(burne, re.sub(r"(.*).css$", r"\1-min.css", burne))

# Lint every file (usually src)
def linter(path, relax=False):
  list = FileList(path, filter = "*.js", exclude = "*-min.js,*xxx*")
  jslint(list, relax=relax)

# Flint every file (usually src)
def flinter(path, relax=False):
  list = FileList(path, filter = "*.js", exclude = "*-min.js,*xxx*")
  jslint(list, relax=relax, fix=True)

# Stat every file (usually build)
def stater(path):
  list = FileList(path, filter = "*.js", exclude = "*-min.js,%s" % excludecrap)
  stats(list, title = "Javascript")
  list = FileList(path, filter = "*-min.js", exclude = excludecrap)
  stats(list, title = "Minified javascript")
  list = FileList(path, filter = "*.css", exclude = "*-min.css,%s" % excludecrap)
  stats(list, title = "Css")
  list = FileList(path, filter = "*-min.css", exclude = excludecrap)
  stats(list, title = "Minified css")
  list = FileList(path, filter = "*.html,*.xml,*.txt%s" % excludecrap)
  stats(list, title = "(ht|x)ml + txt")
  list = FileList(path, exclude = "*.html,*.xml,*.txt,*.js,*.css,%s" % excludecrap)
  stats(list, title = "Other")

def deployer(withversion):
  list = FileList(Yak.BUILD_ROOT)
  if withversion and (Yak.ROOT != './build'):
    deepcopy(list, FileSystem.join(Yak.DEPLOY_ROOT, Yak.PACKAGE['NAME'], Yak.PACKAGE['VERSION']))
  else:
    deepcopy(list, Yak.DEPLOY_ROOT)




# ==================================================================
# Dedicated helpers for static
# ==================================================================

# Bulding / fetching helpers
def donode(path, extra):
  System.check_package('node')
  sh('cd "%s"; node %s' % (path, extra))

def dorake(path, extra = ''):
  System.check_package('rvm')
  System.check_package('npm')
  System.check_package('bundle')
  # System.check_package('ruby')
  # System.check_package('rake')
  sh('cd "%s"; bundle; rake %s' % (path, extra))

def dothor(path, extra = ''):
  System.check_package('ruby')
  System.check_package('rake')
  System.check_package('bundle')
  sh('cd "%s"; thor %s' % (path, extra))

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
    sh(that, std=std, output=True)
    if std.err:
      raise std.err
  except:
    # if puke.FileSystem.exists(dest):
    #   puke.FileSystem.remove(dest)
    console.error('Git operation failed! %s You need to manually fix or remove the directory.' % std.err)


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
  else:
    deepcopy(url, dest)
    if type == 'zip' or type == 'gz' or type == 'bz2' or destype == 'zip':
      try:
        dd = FileSystem.join(dest, remotefilename.replace('.' + type, ''))
        if destype != 'zip':
          if FileSystem.exists(dd):
            FileSystem.remove(dd)
          FileSystem.makedir(dd)
        unpack(packpath, dd, verbose = False)
        # puke.FileSystem.remove(packpath)
      except Exception as e:
        sh('cd "%s"; 7z x "%s"' % (dd, packpath));
      FileSystem.remove(packpath)
    else:
      sh('cd "%s"; mv "%s" "%s"' % (dest, remotefilename, rename))
      packpath = FileSystem.join(dest, rename)



def make(path, type, extra = ''):
  if type == 'rake':
    dorake(path, extra)
  elif type == 'thor':
    dothor(path, extra)
  elif type == 'make':
    domake(path, extra)

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

