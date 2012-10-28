AirStrip.js
=============

About
-------------

This project is meant to ease dealing with third-party javascript dependencies in large projects.

Problem
-------------

Modern javascript projects usually depend on numerous third-party libraries and frameworks 
(say: requirejs, handlebars, i18n, emberjs, jasmine).

Picking these, building, minifying, then tracking versions, possibly patching or forking them, maintaining dependencies, then integrating into a project can quickly become borringly repetitive and tedious.

Solution
-------------

The idea here is to help do that, by providing numerous, widely used libraries for each problem, build them uniformly, list various versions, then "dispatching" the results in a build directory to be then used by said projects - and obviously an "environment" to help you doing that for the (other) libraries you might want on top of that.

What it is not
-------------

Airstrip doesn't provide a way to "combine" multiple javascript libraries into a monolithic one (though you can easily do that with puke), and it doesn't manage dependencies between said libraries (yet).

The jsboot.js/airstrip.js projects will focus on that.

Technology
-------------

We use puke (https://github.com/webitup/puke), a (inhouse) versatile python build system.

Dependencies are listed in YAML.

And ah, all this is likely not working on windows (though we know it does on OSX and reasonable Linuxes).

How to use
-------------

- clone: `git clone https://github.com/jsBoot/airstrip.js`
- install puke: `pip install puke` (if you don't have pip, read http://www.pip-installer.org/en/latest/installing.html)
- build it as-is: `cd aistrip.js; puke all`

Serve the "build" directory from your "static" webserver. Check the airstrip.json file for a list of builded stuff (replace .js / .css by -min.js / -min.css for minified versions).

Doesn't work?
-------------

You probably miss a build dependency required by one or the other third-party projects.
Puke usually give you a hint about what's going wrong.

Do you have ruby installed, along with rvm and bundle? If not, grab rvm and gem install bundle.
Do you have nodejs and npm? If not, install them (aptitude install node, or brew install node, or
whichever method suits you).

Not interested in the provided dependencies and their build requirements? Just wipe-out the 
node (see down below) and specify what you're interested in.


Configuration
-------------

Edit config.yaml:
- create a new node "config-USER-BOX:", where USER is your unix nickname, and BOX the result of the `uname` command, or create a file named "config-USER-BOX.yaml", and add a "userYank" top node into it.
This node will be used to "specialize" your configuration (the generic configuration being stored in the baseYank and defaultYank nodes)
- add a node for example for "root": this is the root under which the other directories will live (eg: tmp, build, deploy...)
- when done editing, puke again (`puke all`)

Build result
-------------

In your path: deploy directory you will find:
- a number of "static" resources, copied from the src directory - these are mondane, edit or remove them at will
- a lib directory, with category subdirectories, containing said built dependencies: frameworks (emberjs, jquery), loaders (requirejs, labjs), plugins, tooling, shims, etc
- an airstrip.json file, containing a list of everything that has been built - this is the manifest to be used in other projects or build systems using this

Every dependency has been built or fetched, in versions specified in the yaml file, renamed, and minified (we use google closure to minify both css and js files, ECMA5, strict when possible).

How you organize your versions management is up-to-you, but we do try to provide for each library in:
- a "trunk" version
- simplify versions names to match only major.minor
- never remove a version once added
- have a "stable" version that points to the currently recommended version

Listing and managing simple dependencies
-------------

Edit (or create a new) yaml file in yanks folder.

A typical entry looks like ("stacktrace.js" here):

```
stacktrace:
    "License": "PublicDomain"
    "Destination": "shims-plus"
    "Source":
        stacktrace-0.3.js: "https://github.com/downloads/eriwen/javascript-stacktrace/stacktrace-0.3.js"
        stacktrace-stable.js: "https://raw.github.com/webitup/javascript-stacktrace/master/stacktrace.js"
        stacktrace-trunk.js: "https://raw.github.com/eriwen/javascript-stacktrace/master/stacktrace.js"
```

The root node ("stacktrace") is purely casual.

You should always specify the license of the project, obviously. This is provisional only for now, but should be either a string (like "MIT"), an array of strings (like ["MIT", "GPL"]), or an url if this is a custom licence.

The "Destination" node is a category directory (will live under the lib/ output folder).

The "Source" node list "versions" that you want to track for this library. Each version is a key
value pair, where the key is the final name you desire, and the value the url where to find the source.

In the case of stacktrace, we track three versions (a stable release, a forked release, and the upstream trunk).


Zipped dependencies
-------------

Some libraries come released in zip files.

Using these just requires:
- to have a "WHATEVER.zip: http://sourceurl" entry in your "Source" node
- to specify what to get from the zip in a "Build" node.

For example, LABJS:

```
lab:
    "License": "MIT"
    "Destination": "loaders"
    "Source":
        lab-2.0.3.zip: "http://labjs.com/releases/LABjs-2.0.3.zip"
        lab-stable.js: "https://raw.github.com/getify/LABjs/master/LAB.src.js"
        lab-trunk.js: "https://raw.github.com/getify/LABjs/master/LAB.src.js"
    "Build":
        type: 'zip'
        dir: 'LABjs-2.0.3'
        production:
            lab-2.0.3.js: 'LAB.src.js'
```

Here we track three versions: two direct "source form factor", and one zip (the lab-2.0.3.zip entry 
in the "Source" node).
In order to extract a specific file from the zip, we define a "Build" section, type "zip", we name
the "dir" resulting from the zip extraction, and a "production" node that specifies (using the same
key value syntax as the "Source" node) which files (from the extracted dir) to get and rename.


Git repositories and actual builds
-------------

In order to clone a git repository, just add a "git: sourceurl" entry in your "Source" node.

If there is a build step in order to produce the actual result, you specify that using the "Build" node.

For example, Emberjs is built that way:

```
ember:
    "License": "MIT"
    "Destination": "frameworks"
    "Source":
        ember.prod-0.9.6.js: "https://github.com/downloads/emberjs/ember.js/ember-0.9.6.min.js"
        ember.debug-0.9.6.js: "https://github.com/downloads/emberjs/ember.js/ember-0.9.6.js"
        ember.prod-1.0.pre.js: "https://github.com/downloads/emberjs/ember.js/ember-1.0.pre.min.js"
        ember.debug-1.0.pre.js: "https://github.com/downloads/emberjs/ember.js/ember-1.0.pre.js"
        git: "git://github.com/emberjs/ember.js.git"
    "Build":
        type: "rake"
        dir: "ember.js"
        production:
            ember.debug-trunk.js: "dist/ember.js"
            ember.prod-trunk.js: "dist/ember.prod.js"
```

... specifies a git entry in the Source list. Then requires build type "rake". Then copy two files
from the dir.

Understanding build and build types
-------------

For now, the following build types are "supported":
- rake
- thor
- make

You can pass random additional arguments to the command if you want, adding an "extra" node in the "Build" node.

Specifying any other build type (like "zip") will actually trigger no build operation, but is a way to let you specify a "working" directory and copy files operations (using the "production" node) from a random dir ("dir").

There also exist the experimental "sh" build type. By specifying "extra" you can perform *any* build operations that way that will get executed in a shell.


License
-------------


MIT license.
Note, though, that the result of the build contains numerous softwares with various licenses,
and that by using them means you should agree with their individual licenses, not with the MIT license of this system itself. But you knew that, right?