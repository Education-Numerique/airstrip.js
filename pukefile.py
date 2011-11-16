#!/usr/bin/env puke
# -*- coding: utf8 -*-

# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage

# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org

# Yak it up
r = Require('puke-base.yaml')

# Get current username to decide what the platform is
DEV = sh("(id -un)", output=False).strip()
# Let it be overriden if need be
PLATFORM = Env.get("PLATFORM", DEV)

# Optionnaly merge with a local file
r.merge('puke-' + PLATFORM + ".yaml")
r.yak('invariant')
r.yak('platform')

@task("Default task called")
def default():
    executeTask("deploy")
#    executeTask("flintdeploy")
    executeTask("mintdeploy")
    executeTask("stats")

@task("Washing-up the taupe :)")
def clean():
    rm(Yak.BUILD_ROOT)
    rm(Yak.DEPLOY_ROOT)

@task("Deploy")
def deploy():
    executeTask("build")
    list = FileList(Yak.BUILD_ROOT, exclude = "*.zip,*.tar.gz,*.DS_Store")
    deepcopy(list, Yak.DEPLOY_ROOT)

@task("Stats report deploy")
def stats():
    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.js")
    (files, lines, size) = stats(list, title = "Static statistics - javascript")
#    console.log(files, lines, size)

#    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.js.gz")
#    stats(list, title = "Static statistics - javascript (+gzed)")

    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable-min.js")
    stats(list, title = "Static statistics - minified javascript")

#    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable-min.js.gz")
#    stats(list, title = "Static statistics - minified javascript (+gzed)")

    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.css")
    stats(list, title = "Static statistics - css")
    list = FileList(Yak.DEPLOY_ROOT, filter = "*.html,*.xml,*.txt")
    stats(list, title = "Static statistics - (ht|x)ml + txt")
    list = FileList(Yak.DEPLOY_ROOT, exclude = "*.html,*.xml,*.txt,*.js,*.css")
    stats(list, title = "Static statistics - other")

@task("Linting")
def lintdeploy():
    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.js")
    jslint(list, strict=False, nojsdoc=True, relax=True)

@task("Flint")
def flintdeploy():
    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.js")
    jslint(list, strict=False, nojsdoc=True, relax=True, fix=True)

@task("Minting")
def mintdeploy():
    list = FileList(Yak.DEPLOY_ROOT, filter = "*-stable.js")
    for burne in list.get():
        m = burne.replace("-stable.js", "-stable-min.js")
        minify(burne, m)
#        pack(burne, burne + ".gz")
#        pack(m, m + ".gz")

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
        sh("cd " + Yak.BUILD_ROOT + "/lib/" + burne["Destination"] + "; rm " + k + "; ln -s " + burne["Latest"] + " " +  k )

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

    # Build-up the description file
    file = "src/doc.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)
    deepcopy(file, Yak.BUILD_ROOT, replace=s)

    # Deepcopy other stuff
    list = FileList("src", exclude="*robots.txt,*crossdomain.xml,*doc.html")
    deepcopy(list, Yak.BUILD_ROOT)

