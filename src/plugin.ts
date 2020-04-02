var plugin = require('./index')
var base = require('@jupyter-widgets/base')
module.exports = {
  id: 'ipyevents',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipyevents',
          version: plugin.EXTENSION_SPEC_VERSION,
          exports: plugin
      });
  },
  autoStart: true
};
