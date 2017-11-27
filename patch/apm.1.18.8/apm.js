#!/usr/lib/node_modules/atom-package-manager/bin/node
'use strict';

process.env.ATOM_RESOURCE_PATH = process.env.ATOM_RESOURCE_PATH ||
    '/usr/<lib>/atom';

try {
    process.env.ATOM_ELECTRON_VERSION = process.env.ATOM_ELECTRON_VERSION ||
        require('child_process')
    .execSync('/usr/bin/electron -v').toString().trim().slice(1);
} catch (e) {
    process.env.ATOM_ELECTRON_VERSION = undefined;
}

require('../lib/apm-cli.js').run(process.argv.slice(2), function (error) {
    process.exitCode = +!!error;
});
