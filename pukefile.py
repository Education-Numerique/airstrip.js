#!/usr/bin/env puke
# -*- coding: utf8 -*-

# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage

# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org

global ALLOWED_DOMAIN
global BUILD_ROOT
global DEPLOY_ROOT

ALLOWED_DOMAIN = Env.get("ALLOWED_DOMAIN", "app.roxee.net");
BUILD_ROOT = Env.get("BUILD_ROOT", "dist");
DEPLOY_ROOT = Env.get("DEPLOY_ROOT", "/Users/dmp/buildd")


global mafunction

def mafunction(param):
    print "toto"

@task("Default")
def default():
    print "defulta"
    mafunction("stuff")
#    executeTask("build")

@task("Clean all output dirs")
def clean():
    rm(BUILD_ROOT)
#    sh("rm -R " + DEPLOY_ROOT)

@task("Deploy")
def deploy():
    executeTask("build")
    # XXX gotcha
    list = FileList(BUILD_ROOT)
    deepcopy(list, DEPLOY_ROOT)


@task("Deploying the static ressources, including approved third party dependencies")
def build():

    # Crossdomain
    list = "src/crossdomain.xml"
    sed = Sed()
    sed.add("<\!--.*-->\s*", "")
    sed.add("{PUKE-DOM}", ALLOWED_DOMAIN)
    combine(list, BUILD_ROOT + "/crossdomain.xml", replace = sed)

    # Robots
    list = "src/robots.txt"
    sed = Sed()
    # XXX partially fucked-up
    sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
    combine(list, BUILD_ROOT + "/robots.txt", replace = sed)

    # Add external dependencies

    fulllist = {
    # We use only the core part of jasmine (h.ackitup.net our own reporters)
        "jasmine-stable.js":
            {
               "License": "MIT",
                "Source": ["http://pivotal.github.com/jasmine/downloads/jasmine-standalone-1.1.0.zip"],
                "Destination": "com/pivotallabs",
                "Latest": "jasmine-standalone-1.1.0/lib/jasmine-1.1.0/jasmine.js"
            },
    # Use that
        "jquery-stable.js":
            {
                "License": "MIT/GPL",
                "Source": ["http://code.jquery.com/jquery-1.7.js"],
                "Destination": "com/jquery",
                "Latest": "jquery-1.7.js"
            },
    # Use that
        "sproutcore-stable.js":
            {
                "License": "MIT",
                "Source": ["http://cloud.github.com/downloads/sproutcore/sproutcore20/sproutcore-2.0.beta.3.js"],
                "Destination": "com/sproutcore",
                "Latest": "sproutcore-2.0.beta.3.js"
            },
    # Doesn't have a notino of "stable" releases - whatever is master on github is the "stable" release
        "normalize-stable.css":
            {
                "License": "Public domain",
                "Source": ["https://raw.github.com/necolas/normalize.css/master/normalize.css"],
                "Destination": "org/normalize",
                "Latest": "normalize.css"
            },

    # A very simple shim to emulate console when there is none (no "release" per-se either)
        "console-stable.js":
            {
                "License": "MIT",
                "Source": ["https://raw.github.com/kayahr/console-shim/master/console-shim.js"],
                "Destination": "org/kayahr",
                "Latest": "console-shim.js"
            },

    # A state crap we use to handle history in the documentation
        "jquery-bbq-stable.js":
            {
                "License": "MIT/GPL",
                "Source": ["https://raw.github.com/cowboy/jquery-bbq/v1.2.1/jquery.ba-bbq.js"],
                "Destination": "org/cowboy",
                "Latest": "jquery.ba-bbq.js"
            },

    # A simple (hopefully) loader
        "labjs-stable":
            {
                "License": "MIT",
                "Source": ["http://labjs.com/releases/LABjs-2.0.3.zip"],
                "Destination": "com/labjs",
                "Latest": "2.0.3/LAB.src.js"
            },


# https://github.com/getify/LABjs/blob/master/LAB.src.js





    # # We don't use closure (yet)
    #     "closure-latest":
    #         {
    #             "License": "Apache",
    #             "Source":  ["http://closure-library.googlecode.com/files/closure-library-20111110-r1376.zip"],
    #             "Destination": "com/google", 
    #             "Latest": "closure/goog"
    #         },

    # # Going to reduce that
    #     "modernizr-latest":
    #         {
    #             "License": "MIT/BSD",
    #             "Source": [
    #                 "http://www.modernizr.com/i/js/modernizr.2.0.6-prebuild.js",
    #                 "http://www.modernizr.com/i/js/modernizr.load.1.0.2.js",
    #                 "http://www.modernizr.com/i/js/respond.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/cookies.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-backgroundrepeat.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-backgroundsizecover.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-boxsizing.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-cubicbezierrange.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-displaytable.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-overflow-scrolling.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-pointerevents.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/css-userselect.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/custom-protocol-handler.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/dom-createElement-attrs.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/elem-details.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/elem-progress-meter.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/emoji.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/event-deviceorientation-motion.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/file-api.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/forms-placeholder.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/hyphens.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/img-webp.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/url-data-uri.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/webgl-extensions.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/window-framed.js",
    #                 "http://www.modernizr.com/i/js/feature-detects/workers-sharedworkers.js"
    #             ],
    #             "Destination": "org/modernizr",
    #             "Latest": ""
    #         },


    #     "backbone-latest.js":
    #         {
    #             "License": "MIT",
    #             "Source": ["http://documentcloud.github.com/backbone/backbone.js"],
    #             "Destination": "org/backbone",
    #             "Latest": "backbone.js"
    #         },

    #     "h5bp-latest":
    #         {
    #             "License": "UNSPECIFIED",
    #             "Source": ["http://www.initializr.com/builder?mode=custom&h5bp-analytics&h5bp-chromeframe&h5bp-css&h5bp-csshelpers&h5bp-favicon&h5bp-iecond&h5bp-mediaqueries&h5bp-mediaqueryprint&h5bp-readmemd&h5bp-scripts&html5shiv"],
    #             "Destination": "org/h5bp",
    #             "Latest": ""
    #         },
    #     "html5shim-latest.js":
    #         {
    #             "License": "MIT/GPL",
    #             "Source": ["https://html5shim.googlecode.com/svn/trunk/html5.js"],
    #             "Destination": "org/",
    #             "Latest": "html5.js"
    #         },


    }

    description = "<h2>Third parties</h2>"
    for (k, burne) in fulllist.items():
        description += "<section>\n"
        description += "\t<h3><a href=\"lib/" + burne["Destination"] + "/" + k + "\">" + k + "</a></h3>\n\t<dl>\n"
        for (key, v) in burne.items():
            if(isinstance(v, str)):
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + v + "</dd>\n"
            else:
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + "</dd><dd>".join(v) + "</dd>\n"
        description += "\t</dl>\n</section>\n"
        deepcopy(burne["Source"], os.path.join(BUILD_ROOT, "lib", burne["Destination"]))
        sh("cd " + BUILD_ROOT + "/lib/" + burne["Destination"] + "; rm " + k + "; ln -s " + burne["Latest"] + " " +  k )


    # h5 = os.path.join(BUILD_ROOT, "lib", fulllist["h5bp-latest"]["Destination"])
    # sh("cd " + h5 + "; rm builder.zip; mv builder* builder.zip")
    # unpack(os.path.join(h5, "builder.zip"), h5)


    # goog = os.path.join(BUILD_ROOT, "lib", fulllist["closure-stable"]["Destination"])
    # unpack(os.path.join(goog, "closure-library-20111110-r1376.zip"), goog)

    # Unpack these who need it
    jasm = os.path.join(BUILD_ROOT, "lib", fulllist["jasmine-stable.js"]["Destination"])
    unpack(os.path.join(jasm, "jasmine-standalone-1.1.0.zip"), jasm)

    labjs = os.path.join(BUILD_ROOT, "lib", fulllist["labjs-stable"]["Destination"])
    unpack(os.path.join(labjs, "LABjs-2.0.3.zip"), os.path.join(labjs, "2.0.3"))

    # Build-up the description file
    file = "src/doc.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)
    deepcopy(file, BUILD_ROOT, replace=s)

    # Deepcopy other stuff
    list = FileList("src", exclude="*robots.txt,*crossdomain.xml,*doc.html")
    deepcopy(list, BUILD_ROOT)

