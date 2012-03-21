#!/usr/bin/env puke
# -*- coding: utf8 -*-

global PH
import pukehelpers as PH

# Need to find-out where one should output the builded stuff from roxish pukefile
# if FileSystem.exists('../roxish/pukefile.py'):
#     p = sh('cd ../roxish; puke link static')
#     if p != Yak.DEPLOY_ROOT:
#         console.warn('Your deploy path doesn\'t match ROXISH expectations - please adjust to %s unless you know what you are doing.' % p)
# elif FileSystem.exists(FileSystem.join(Yak.ROXISH_PATH, 'pukefile.py')):
#     p = sh('cd ' + Yak.ROXISH_PATH + '; puke link static -q').strip()
#     if p != Yak.DEPLOY_ROOT:
#         console.warn('Your deploy path doesn\'t match ROXISH expectations - please adjust to %s unless you know what you are doing.' % p)
# else:
#     console.warn('Couldn\'t find your Roxish clone! Your DEPLOY_ROOT might or might not be valid')


@task("Default task")
def default():
    executeTask("build")
    executeTask("deploy")
    executeTask("stats")

@task("Calling all interesting tasks")
def all():
    executeTask("build")
#    executeTask("flint")
    executeTask("mint")
    executeTask("deploy")
    executeTask("stats")

@task("Washing-up the taupe :) - cautious mode")
def clean():
    PH.globalclean()


# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage

# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org

global FILTERING
FILTERING="*-stable.js"

# Get whatever has been built and exfilter some crappy stuff
@task("Deploy")
def deploy():
    list = FileList(Yak.TMP_ROOT, exclude = "*.zip,*.tar.gz,*.DS_Store")
    deepcopy(list, Yak.DEPLOY_ROOT)


@task("Stats report deploy")
def stats():
    list = FileList(Yak.TMP_ROOT, filter = FILTERING)
    stats(list, title = "Static statistics - javascript")
    list = FileList(Yak.TMP_ROOT, filter = FILTERING.replace(".js", "-min.js"))
    stats(list, title = "Static statistics - minified javascript")
    list = FileList(Yak.TMP_ROOT, filter = "*-stable.css")
    stats(list, title = "Static statistics - css")
    list = FileList(Yak.DEPLOY_ROOT, filter = "*.html,*.xml,*.txt")
    stats(list, title = "Static statistics - (ht|x)ml + txt")
    list = FileList(Yak.TMP_ROOT, exclude = "*.html,*.xml,*.txt,*.js,*.css")
    stats(list, title = "Static statistics - other")

@task("Linting")
def lint():
    list = FileList(Yak.TMP_ROOT, filter = FILTERING)
    jslint(list, relax=True)

@task("Flint")
def flint():
    list = FileList(Yak.TMP_ROOT, filter = FILTERING)
    jslint(list, relax=True, fix=True)

@task("Minting")
def mint():
    list = FileList(Yak.TMP_ROOT, filter = FILTERING)
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
    combine(list, Yak.TMP_ROOT + "/crossdomain.xml", replace = sed)

    # Robots
    list = "src/robots.txt"
    sed = Sed()
    # XXX partially fucked-up
    sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
    combine(list, Yak.TMP_ROOT + "/robots.txt", replace = sed)



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
        deepcopy(burne["Source"], os.path.join(Yak.TMP_ROOT, "lib", burne["Destination"]))

    # h5 = os.path.join(TMP_ROOT, "lib", fulllist["h5bp-latest"]["Destination"])
    # sh("cd " + h5 + "; rm builder.zip; mv builder* builder.zip")
    # unpack(os.path.join(h5, "builder.zip"), h5)


    # goog = os.path.join(TMP_ROOT, "lib", fulllist["closure-stable"]["Destination"])
    # unpack(os.path.join(goog, "closure-library-20111110-r1376.zip"), goog)

    # Unpack these who need it
    jasm = os.path.join(Yak.TMP_ROOT, "lib", Yak.COLLECTION["jasmine-stable.js"]["Destination"])
    unpack(os.path.join(jasm, "jasmine-standalone-1.1.0.zip"), jasm)
    # XXX can't use jasmine with patching       if (result.trace.stack) to if (result.trace && result.trace.stack) {

    labjs = os.path.join(Yak.TMP_ROOT, "lib", Yak.COLLECTION["labjs-stable.js"]["Destination"])
    unpack(os.path.join(labjs, "LABjs-2.0.3.zip"), os.path.join(labjs, "2.0.3"))

    for (k, burne) in Yak.COLLECTION.items():
#        sh("cd " + Yak.TMP_ROOT + "/lib/" + burne["Destination"] + "; rm " + k + "; ln -s " + burne["Latest"] + " " +  k )
        sh("cd " + Yak.TMP_ROOT + "/lib/" + burne["Destination"] + "; cp -R " + burne["Latest"] + " " +  k )

    # Build-up the description file
    file = "src/doc.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)
    deepcopy(file, Yak.TMP_ROOT, replace=s)

    # Deepcopy other stuff
    list = FileList("src/", exclude="*robots.txt,*crossdomain.xml,*doc.html,*.DS_Store")
    deepcopy(list, Yak.TMP_ROOT)
