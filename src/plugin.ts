import {
  Application, IPlugin
} from '@lumino/application';

import {
  Widget
} from '@lumino/widgets';

import {
  IJupyterWidgetRegistry
 } from '@jupyter-widgets/base';

import {
  EventModel
} from './events';

import {
  EXTENSION_SPEC_VERSION
} from './version';

/**
 * The example plugin.
 */
const ipyeventsPlugin: IPlugin<Application<Widget>, void> = {
  id: 'ipyevents',
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default ipyeventsPlugin;


/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: Application<Widget>, registry: IJupyterWidgetRegistry): void {
  registry.registerWidget({
    name: 'ipyevents',
    version: EXTENSION_SPEC_VERSION,
    exports: {
      EventModel: EventModel
    }
  });
}
