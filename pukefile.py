#!/usr/bin/env puke
# -*- coding: utf8 -*-

global PH
import pukehelpers as PH
import yaml

@task("Default task")
def default():
  pass
  # executeTask("build", "redactor")
  # executeTask("deploy")

@task("Calling all interesting tasks")
def all():
  Cache.clean()
  executeTask("build")
  # Because sometime you are in a hurry :)
  executeTask("deploy")
  executeTask("mint")
  executeTask("deploy")
  executeTask("stats")
#    executeTask("flint")
#    executeTask("lint")


# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage
# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org


@task("Washing-up the taupe :) - cautious mode")
def clean():
  PH.cleaner()



# Get whatever has been built and exfilter some crappy stuff
@task("Deploying")
def deploy():
  PH.deployer(False)


@task("Stats report")
def stats():
  PH.stater(Yak.BUILD_ROOT)

@task("Linting")
def lint():
  PH.linter(Yak.BUILD_ROOT)

@task("Flinting")
def flint():
  PH.flinter(Yak.BUILD_ROOT)

@task("Minting")
def mint():
  # Ember doesn't survive strict
  PH.minter(Yak.BUILD_ROOT, strict = False)

@task("Deploying the static ressources, including approved third party dependencies")
def build(buildonly = False):
  # Crossdomain
  sed = Sed()
  sed.add("<\!--.*-->\s*", "")
  sed.add("{PUKE-DOM}", Yak.ALLOWED_DOMAIN)
  combine("src/crossdomain.xml", Yak.BUILD_ROOT + "/crossdomain.xml", replace = sed)

  # Robots
  sed = Sed()
  # XXX partially fucked-up
  sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
  combine("src/robots.txt", Yak.BUILD_ROOT + "/robots.txt", replace = sed)

  # Deepcopy other stuff
  sed = Sed()
  PH.replacer(sed)
  list = FileList("src/", exclude="*robots.txt,*crossdomain.xml,*index.html")
  deepcopy(list, Yak.BUILD_ROOT, replace=sed)


  # Process the remote leaves
  description = []

  for (name, packinfo) in Yak.COLLECTION.items():
    # Temporary and build output directories definitions
    tmpdir = FileSystem.join(Yak.TMP_ROOT, "lib", packinfo["Destination"])
    builddir = FileSystem.join(Yak.BUILD_ROOT, "lib", packinfo["Destination"])

    desclist = []
    for(localname, url) in packinfo["Source"].items():
      # Do the fetch of 
      PH.fetchone(url, tmpdir, localname)
      # Copy files that "exists" to build directory
      f = FileSystem.join(tmpdir, localname)
      if FileSystem.exists(f):
        d = FileSystem.join(builddir, localname)
        # if not FileSystem.exists(FileSystem.dirname(d)):
        #   FileSystem.makedir(FileSystem.dirname(d));
        FileSystem.copyfile(f, d)
        # Augment desclist with provided localname
        desclist += [localname]

    if "Build" in packinfo:
      buildinfo = packinfo["Build"]
      production = buildinfo["production"]
      tmpdir = FileSystem.join(tmpdir, buildinfo["dir"])
      extra = ''
      if 'args' in buildinfo:
        extra = buildinfo["args"]
      if not buildonly or buildonly == name:
        PH.make(tmpdir, buildinfo["type"], extra)

      # Copy production to build dir
      for(local, builded) in production.items():
        f = FileSystem.join(tmpdir, builded)
        d = FileSystem.join(builddir, local)
        if FileSystem.isfile(f):
          FileSystem.copyfile(f, d)
        elif FileSystem.isdir(f):
          deepcopy(FileList(f), d)

      # Augment description list with build result
      desclist = desclist + production.keys()

    marker = 'lib/%s/' % packinfo["Destination"]
    description.append('"%s": [\n"%s%s"\n]' % (name, marker, ('",\n"%s' % marker).join(desclist)))
    # miam += """
    #   %s:
    #     ["%s%s"]
    # """ % (name, marker, ('", "%s' % marker).join(desclist))
  FileSystem.writefile(FileSystem.join(Yak.BUILD_ROOT, "airstrip.yaml"), yaml.dump(yaml.load('\n'.join(description))))

  # Write description file
  # FileSystem.writefile(FileSystem.join(Yak.BUILD_ROOT, "static.json"), '{%s}' % ',\n'.join(description))

  # Build-up the description file
  file = "src/index.html"
  sed.add("{PUKE-LIST}", '{%s}' % ',\n'.join(description))
  deepcopy(file, Yak.BUILD_ROOT, replace=sed)


