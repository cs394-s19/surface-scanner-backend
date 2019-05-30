import {PythonShell} from 'python-shell';
var assert = require('assert');

let pyshell = new PythonShell('my_script.py');

describe('User', function() {
    describe('#save()', function() {
        it('should save without error', function(done) {
            var user = new User('Luna');
            user.save(done);
        });
    });
});