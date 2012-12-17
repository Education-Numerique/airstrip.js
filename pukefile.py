#!/usr/bin/env puke
# -*- coding: utf8 -*-

global PH
import helpers as PH
import re

@task("Default task")
def default():
  executeTask("build")
  executeTask("deploy")

@task("All")
def all():
  executeTask("build")
  executeTask("mint")
  executeTask("deploy")
  executeTask("stats")


@task("Wash the taupe!")
def clean():
  PH.cleaner()



# Get whatever has been built and exfilter some crappy stuff
@task("Deploying")
def deploy():
  PH.deployer(False)


@task("Stats report deploy")
def stats():
  PH.stater(Yak.build_root)


@task("Minting")
def mint():
  # list = FileList(Yak.build_root, filter = "*bootstrap*.js", exclude = "*-min.js")
  # for burne in list.get():
  #   minify(burne, re.sub(r"(.*).js$", r"\1-min.js", burne), strict = False, ecma3 = True)
  # raise "toto"
  # These dont survive strict
  PH.minter(Yak.build_root, filter = "*ember*.js,*yahoo*.js,*yepnope*.js,*modernizr*.js,*jasmine*.js", excluding=",*latest/jax*", strict = False)
  PH.minter(Yak.build_root, excluding = "*ember*.js,*yahoo*.js,*yepnope*.js,*modernizr*.js,*jasmine*.js,*latest/jax*", strict = True)

@task("Deploying the static ressources, including approved third party dependencies")
def build(buildonly = False):
  # Crossdomain
  sed = Sed()
  sed.add("<\!--.*-->\s*", "")
  combine("src/crossdomain.xml", Yak.build_root + "/crossdomain.xml", replace = sed)

  # Robots
  sed = Sed()
  # XXX partially fucked-up
  sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
  combine("src/robots.txt", Yak.build_root + "/robots.txt", replace = sed)

  # Deepcopy other stuff
  sed = Sed()
  PH.replacer(sed)
  list = FileList("src/", exclude="*robots.txt,*crossdomain.xml,*index.html")
  deepcopy(list, Yak.build_root, replace=sed)


  # Process the remote leaves
  description = {}

  # Yak.collection.items()
  colls = PH.getyanks()
  # print Yak.collection
  # for name in Yak.collection:
  #   print name
  for name in colls:
    packinfo = colls[name]
    # Temporary and build output directories definitions
    tmpdir = FileSystem.join(Yak.tmp_root, "lib", packinfo["Destination"], name)
    builddir = FileSystem.join(Yak.build_root, "lib", packinfo["Destination"], name)

    desclist = []
    marker = 'lib/%s/' % packinfo["Destination"]
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
        desclist += [FileSystem.join(marker, name, localname)]

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
        desclist += [FileSystem.join(marker, name, local)]
        if FileSystem.isfile(f):
          FileSystem.copyfile(f, d)
        elif FileSystem.isdir(f):
          deepcopy(FileList(f), d)

      # ["coin%s" % key for key in ['item1', 'item2']]


      # map((lambda item: "%s%s" % (name, item)), ['item1', 'item2'])
      # # Augment description list with build result
      # bitch = production.keys();

      # for x in bitch:
      #   bitch[x] = FileSystem.join(name, bitch[x]);

      # print bitch
      # raise "toto"

      # desclist = desclist + production.keys()

    description[name] = desclist
    # description[name] = "%s%s" % (name, marker, ('",\n"%s' % marker).join(desclist)))

    # miam += """
    #   %s:
    #     ["%s%s"]
    # """ % (name, marker, ('", "%s' % marker).join(desclist))
  # FileSystem.writefile(FileSystem.join(Yak.build_root, "airstrip.yaml"), yaml.dump(yaml.load('\n'.join(description))))


    # print json.dumps(description)
    # raise "toto"

  shortversion = Yak.package['version'].split('-').pop(0).split('.')
  shortversion = shortversion[0] + "." + shortversion[1]
  PH.describe(shortversion, "airstrip", description)
  # Write description file
  # FileSystem.writefile(FileSystem.join(Yak.build_root, "airstrip.json"), '{%s}' % ',\n'.join(description))

  # Build-up the description file
  file = "src/index.html"
  sed.add("{PUKE-LIST}", json.dumps(description, indent=4))
  deepcopy(file, Yak.build_root, replace=sed)


