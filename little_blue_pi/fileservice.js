var bleno = require('bleno');
var util = require('util');

var FileShareCharacteristic = require('./filecharacteristics/FileShare');
var getManifestCharacteristic = require('./filecharacteristics/getManifest');
var pulseCharacteristic = require('./filecharacteristics/pulse');
// var UptimeCharacteristic = require('./characteristics/uptime');
// var MemoryCharacteristic = require('./characteristics/memory');

function FileService() {

  bleno.PrimaryService.call(this, {
    uuid: 'a8a4d5bf-d2cb-4df5-8e95-a9d6ca7112cf',
    characteristics: [
      new FileShareCharacteristic(),
      new getManifestCharacteristic(),
      new pulseCharacteristic()
    ]
  });
};

util.inherits(FileService, bleno.PrimaryService);
module.exports = FileService;
