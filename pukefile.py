#!/usr/bin/env puke
# -*- coding: utf8 -*-

# XXX remove comments from html
# XXX have a default favicon
# XXX have a placeholder homepage

# XXX humans: <link type="text/plain" rel="author" href="http://domain/humans.txt" />
# humanstxt.org

@task("Default")
def default():
    executeTask("build")

@task("Deploy")
def deploy:
    DEPLOY_ROOT = "/var/www/deploy/static"
    executetask("build")
    deepcopy("dist", DEPLOY_ROOT)

@task("Deploying the static ressources, including approved third party dependencies")
def build():
    # Consts
    ALLOWED_DOMAIN = "app.roxee.net"
    BUILD_ROOT = "dist"

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

    # Other stuff
    list = FileList("src", exclude="*robots.txt,*crossdomain.xml")
    deepcopy(list, BUILD_ROOT)

    # Add external dependencies

    fulllist = {
        "jasmine":
            {"License": "MIT", "Source": "http://pivotal.github.com/jasmine/downloads/jasmine-standalone-1.1.0.zip", "Destination": "org/pivotal", "Latest": ""},
        "modernizr":
            {"License": "MIT/BSD", "Source": "http://saveasbro.com/download/modernizr.custom.32744.js", "Destination": "org/modernizr", "Latest": ""},
        "closure":
            {"License": "Apache", "Source":  "http://closure-library.googlecode.com/files/closure-library-20111110-r1376.zip", "Destination": "org/google", "Latest": ""},
        "jquery":
            {"License": "MIT/GPL", "Source": "http://code.jquery.com/jquery-1.7.js", "Destination": "org/jquery", "Latest": "jquery-1.7.js"},
        "backbone":
            {"License": "MIT", "Source": "http://documentcloud.github.com/backbone/backbone.js", "Destination": "org/backbone", "Latest": "backbone.js"},
        "sproutcore":
            {"License": "MIT", "Source": "http://cloud.github.com/downloads/sproutcore/sproutcore20/sproutcore-2.0.beta.3.js", "Destination": "org/sproutcore", "Latest": "sproutcore-2.0.beta.3.js"}
    }

    description = ""
    for (k, burne) in fulllist.items():
        description += "<section>\n"
        description += "\t<h2><a href=\"" + k + "-latest.js/\">" + k + "</a></h2>\n\t<dl>\n"
        for (key, v) in burne.items():
            description += "\t\t<dt>" + key + "</dt>\n\t\t<dd>" + v + "</dd>\n"
        description += "\t</dl>\n</section>\n"

#        deepcopy(burne["Source"], os.path.join(BUILD_ROOT, "third-party", burne["Destination"]))

    file = "src/third-party/index.html"
    s = Sed()
    s.add("{PUKE-LIST}", description)


#    combine(file, os.path.join(BUILD_ROOT, "third-party", "index.html"), replace=s)

#    sh("cd dist/tmp; unzip jasmine-standalone-1.1.0.zip")

