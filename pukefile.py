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
BUILD_ROOT = "dist"
DEPLOY_ROOT = Env.get("DEPLOY_ROOT", "/Users/dmp/buildd")

@task("Default")
def default():
    executeTask("build")

@task("Clean all output dirs")
def clean():
    console.log(BUILD_ROOT)
    raise "toto"
#    sh("rm -R " + BUILD_ROOT)
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
        "jasmine":
            {
               "License": "MIT",
                "Source": ["http://pivotal.github.com/jasmine/downloads/jasmine-standalone-1.1.0.zip"],
                "Destination": "org/pivotal",
                "Latest": "jasmine-standalone-1.1.0/lib/jasmine-1.1.0"
            },
        "closure":
            {
                "License": "Apache",
                "Source":  ["http://closure-library.googlecode.com/files/closure-library-20111110-r1376.zip"],
                "Destination": "org/google", 
                "Latest": "closure/goog"
            },
        "modernizr":
            {
                "License": "MIT/BSD",
                "Source": [
                    "http://www.modernizr.com/i/js/modernizr.2.0.6-prebuild.js",
                    "http://www.modernizr.com/i/js/modernizr.load.1.0.2.js",
                    "http://www.modernizr.com/i/js/feature-detects/cookies.js",
                    "http://www.modernizr.com/i/js/feature-detects/custom-protocol-handler.js",
                    "http://www.modernizr.com/i/js/feature-detects/elem-details.js",
                    "http://www.modernizr.com/i/js/feature-detects/file-api.js",
                    "http://www.modernizr.com/i/js/feature-detects/url-data-uri.js"
                ],
                "Destination": "org/modernizr",
                "Latest": ""
            },
        "jquery":
            {
                "License": "MIT/GPL",
                "Source": ["http://code.jquery.com/jquery-1.7.js"],
                "Destination": "org/jquery",
                "Latest": "jquery-1.7.js"
            },
        "backbone":
            {
                "License": "MIT",
                "Source": ["http://documentcloud.github.com/backbone/backbone.js"],
                "Destination": "org/backbone",
                "Latest": "backbone.js"
            },
        "sproutcore":
            {
                "License": "MIT",
                "Source": ["http://cloud.github.com/downloads/sproutcore/sproutcore20/sproutcore-2.0.beta.3.js"],
                "Destination": "org/sproutcore",
                "Latest": "sproutcore-2.0.beta.3.js"
            },

        "h5bp":
            {
                "License": "UNSPECIFIED",
                "Source": ["http://www.initializr.com/builder?mode=custom&h5bp-analytics&h5bp-chromeframe&h5bp-css&h5bp-csshelpers&h5bp-favicon&h5bp-iecond&h5bp-mediaqueries&h5bp-mediaqueryprint&h5bp-readmemd&h5bp-scripts&html5shiv"],
                "Destination": "org/h5bp",
                "Latest": "builder"
            },



    }

    description = "<h2>Third parties</h2>"
    for (k, burne) in fulllist.items():
        description += "<section>\n"
        description += "\t<h3><a href=\"third-party/" + k + "-latest.js\">" + k + "</a></h3>\n\t<dl>\n"
        for (key, v) in burne.items():
            if(isinstance(v, str)):
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + v + "</dd>\n"
            else:
                description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + "</dd><dd>".join(v) + "</dd>\n"
        description += "\t</dl>\n</section>\n"
        deepcopy(burne["Source"], os.path.join(BUILD_ROOT, "third-party", burne["Destination"]))
        sh("cd " + BUILD_ROOT + "/third-party" + "; rm " + k + "-latest.js; ln -s " + burne["Destination"] + "/" + burne["Latest"] + " " +  k + "-latest.js")


    h5 = os.path.join(BUILD_ROOT, "third-party", fulllist["h5bp"]["Destination"])
    sh("cd " + h5 + "; rm builder.zip; mv builder* builder.zip")
    unpack(os.path.join(h5, "builder.zip"), h5)


    goog = os.path.join(BUILD_ROOT, "third-party", fulllist["closure"]["Destination"])
    unpack(os.path.join(goog, "closure-library-20111110-r1376.zip"), goog)

    jasm = os.path.join(BUILD_ROOT, "third-party", fulllist["jasmine"]["Destination"])
    unpack(os.path.join(jasm, "jasmine-standalone-1.1.0.zip"), jasm)

    file = "src/doc.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)

    deepcopy(file, BUILD_ROOT, replace=s)


    # Deepcopy other stuff
    list = FileList("src", exclude="*robots.txt,*crossdomain.xml,*doc.html")
    deepcopy(list, BUILD_ROOT)

