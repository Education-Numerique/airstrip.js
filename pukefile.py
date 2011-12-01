#!/usr/bin/env puke
# -*- coding: utf8 -*-

# Yank the file in
r = Require('puke-yak.yaml')
# Yak the yak node
r.yak('yak')
# Yak-in another node, either the login name or the value of the PLATFORM env variable
r.yak('user-' + Env.get("PLATFORM", System.LOGIN))

# Mangle the deploy root
# XXX fix so that ~/ is expanded? Might help.
Yak.DEPLOY_ROOT = FileSystem.join(Yak.DEPLOY_ROOT, Yak.NAME, Yak.VERSION)

# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage

# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org

global FILTERING
FILTERING="*-stable.js"

# Just make-deploy by default
@task("Default task called")
def default():
    executeTask("build")
    executeTask("deploy")
    executeTask("stats")

# Clean build and dist
@task("Washing-up the taupe :)")
def clean():
    try:
        FileSystem.remove(Yak.BUILD_ROOT)
        FileSystem.remove(Yak.DEPLOY_ROOT)
    except:
        pass

# Get whatever has been built and exfilter some crappy stuff
@task("Deploy")
def deploy():
    list = FileList(Yak.BUILD_ROOT, exclude = "*.zip,*.tar.gz,*.DS_Store")
    deepcopy(list, Yak.DEPLOY_ROOT)

# Build, minify, deploy, stats
@task("All tasks called")
def all():
    executeTask("build")
#    executeTask("flint")
    executeTask("mint")
    executeTask("deploy")
    executeTask("stats")

@task("Stats report deploy")
def stats():
    list = FileList(Yak.BUILD_ROOT, filter = FILTERING)
    stats(list, title = "Static statistics - javascript")
    list = FileList(Yak.BUILD_ROOT, filter = FILTERING.replace(".js", "-min.js"))
    stats(list, title = "Static statistics - minified javascript")
    list = FileList(Yak.BUILD_ROOT, filter = "*-stable.css")
    stats(list, title = "Static statistics - css")
    list = FileList(Yak.DEPLOY_ROOT, filter = "*.html,*.xml,*.txt")
    stats(list, title = "Static statistics - (ht|x)ml + txt")
    list = FileList(Yak.BUILD_ROOT, exclude = "*.html,*.xml,*.txt,*.js,*.css")
    stats(list, title = "Static statistics - other")

@task("Linting")
def lint():
    list = FileList(Yak.BUILD_ROOT, filter = FILTERING)
    jslint(list, relax=True)

@task("Flint")
def flint():
    list = FileList(Yak.BUILD_ROOT, filter = FILTERING)
    jslint(list, relax=True, fix=True)

@task("Minting")
def mint():
    list = FileList(Yak.BUILD_ROOT, filter = FILTERING)
    for burne in list.get():
        m = burne.replace(".js", "-min.js")
        minify(burne, m)

@task("Deploying the static ressources, including approved third party dependencies")
def build():
    sed = Sed()
    sed.add("<\!--.*-->\s*", "")
    sed.add("{PUKE-DOM}", Yak.ALLOWED_DOMAIN)

    # Crossdomain
    list = "src/crossdomain.xml"
    combine(list, Yak.BUILD_ROOT + "/crossdomain.xml", replace = sed)

    # Robots
    list = "src/robots.txt"
    sed = Sed()
    # XXX partially fucked-up
    sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
    combine(list, Yak.BUILD_ROOT + "/robots.txt", replace = sed)



    description = "<h2>Third parties</h2>"
    for (k, burne) in Yak.COLLECTION.items():
        description += "<section>\n"
        description += "\t<h3><a href=\"lib/" + burne["Destination"] + "/" + k + "\">" + k + "</a></h3>\n\t<dl>\n"
        for (key, v) in burne.items():
            if(isinstance(v, str)):
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + v + "</dd>\n"
            else:
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + "</dd><dd>".join(v) + "</dd>\n"
        description += "\t</dl>\n</section>\n"
        deepcopy(burne["Source"], os.path.join(Yak.BUILD_ROOT, "lib", burne["Destination"]))

    # h5 = os.path.join(BUILD_ROOT, "lib", fulllist["h5bp-latest"]["Destination"])
    # sh("cd " + h5 + "; rm builder.zip; mv builder* builder.zip")
    # unpack(os.path.join(h5, "builder.zip"), h5)


    # goog = os.path.join(BUILD_ROOT, "lib", fulllist["closure-stable"]["Destination"])
    # unpack(os.path.join(goog, "closure-library-20111110-r1376.zip"), goog)

    # Unpack these who need it
    jasm = os.path.join(Yak.BUILD_ROOT, "lib", Yak.COLLECTION["jasmine-stable.js"]["Destination"])
    unpack(os.path.join(jasm, "jasmine-standalone-1.1.0.zip"), jasm)

    labjs = os.path.join(Yak.BUILD_ROOT, "lib", Yak.COLLECTION["labjs-stable.js"]["Destination"])
    unpack(os.path.join(labjs, "LABjs-2.0.3.zip"), os.path.join(labjs, "2.0.3"))

    for (k, burne) in Yak.COLLECTION.items():
#        sh("cd " + Yak.BUILD_ROOT + "/lib/" + burne["Destination"] + "; rm " + k + "; ln -s " + burne["Latest"] + " " +  k )
        sh("cd " + Yak.BUILD_ROOT + "/lib/" + burne["Destination"] + "; cp -R " + burne["Latest"] + " " +  k )


    # Build-up the description file
    file = "src/doc.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)
    deepcopy(file, Yak.BUILD_ROOT, replace=s)

    # Deepcopy other stuff
    list = FileList("src", exclude="*robots.txt,*crossdomain.xml,*doc.html,*.DS_Store")
    deepcopy(list, Yak.BUILD_ROOT)

