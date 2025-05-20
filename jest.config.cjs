// jest.config.js
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;
module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
  },
  moduleFileExtensions: ['js', 'jsx', 'json', 'node'],
  setupFiles: ['<rootDir>/jest.setup.js']
};
