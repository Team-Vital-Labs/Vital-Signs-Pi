var bleno = require('bleno');
var os = require('os');
var util = require('util');
let {PythonShell} = require('python-shell');

var BlenoCharacteristic = bleno.Characteristic;

var pulseCharacteristic = function() {
  pulseCharacteristic.super_.call(this, {
    uuid: 'abb0994c-8312-480b-a253-57f3065c167d',
    properties: ['read', 'write'],
    value: null
  });

  this._value = new Buffer(0);
};

var py;

pulseCharacteristic.prototype.onReadRequest = function(offset, callback) {

  if(!offset){
    console.log(JSON.stringify(tree));
    this._value = new Buffer(JSON.stringify(tree));
  }
  callback(this.RESULT_SUCCESS, this._value.slice(offset, this._value.length));
};



pulseCharacteristic.prototype.onWriteRequest = function(data, offset, withoutResponse, callback)
{
  console.log("recived write request");
  if(!offset)
	{
  }
  var stringData = data.toString('ascii');
  console.log(stringData);
  if(stringData == "_START_")
  {
    py =  new PythonShell('bpmWrite.py');
    callback(this.RESULT_SUCCESS);
  }
  else if(stringData == "_STOP_")
  {
    // py.end(function (err,code,signal) {
    //   if (err) throw err;
    //   console.log('The exit code was: ' + code);
    //   console.log('The exit signal was: ' + signal);
    //   console.log('finished');
    //   console.log('finished');
    // });
    py.childProcess.kill('SIGINT');
    callback(this.RESULT_SUCCESS);
  }
  else
  {
    py.send(stringData);
    callback(this.RESULT_SUCCESS);
  }
};


util.inherits(pulseCharacteristic, BlenoCharacteristic);
module.exports = pulseCharacteristic;
